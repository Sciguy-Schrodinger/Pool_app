import pygame
from pygame import mixer
import random
import math
import sys
import time
import numpy as np

pygame.init()

width = 950
height = 950

screen = pygame.display.set_mode((width,height))

pygame.display.set_caption("Pool")

background = pygame.image.load("Pool_table.jpg")
background = pygame.transform.scale(background,(20*width/19,98*height/95))
background = pygame.transform.rotate(background,90)

pygame.mixer.music.load("lounge.mp3")
collision = pygame.mixer.Sound("bounce.mp3")
cheer = pygame.mixer.Sound("cheer.mp3")
score = pygame.mixer.Sound("score.mp3")

pygame.mixer.music.play(-1)

running = True
in_hole = False

balls = []
pos = []
vel = []

ball_radius = 20
colours = ["yellow", "blue", "red", "purple","orange", "green", "maroon","cornsilk", "black","lime","pink","brown","tan","gray","cyan","white"]

colour_map = {
    "yellow": (255, 255, 0), "blue": (0, 0, 255), "red": (255, 0, 0),
    "purple": (128, 0, 128), "orange": (255, 165, 0), "green": (0, 128, 0),
    "maroon": (128, 0, 0), "white": (250, 250, 250), "black": (0, 0, 0),
    "lime": (0, 255, 0), "pink": (255, 192, 203), "brown": (139, 69, 19),
    "tan": (210, 180, 140), "gray": (128, 128, 128), "cyan": (0, 255, 255),
    "cornsilk": (255,248,220)
}

total_balls = 15
score_count = 0

top_left_edge = (130,110)
top_right_edge = (755,110)
bottom_right_edge = (755,875)
bottom_left_edge = (130,875)

top_left_hole = (125,100)
top_right_hole = (760,105)
middle_left_hole = (120,490)
middle_right_hole = (770,490)
bottom_left_hole = (125,895)
bottom_right_hole = (770,895)

holes = []

holes.append(top_left_hole)
holes.append(top_right_hole)
holes.append(middle_left_hole)
holes.append(middle_right_hole)
holes.append(bottom_left_hole)
holes.append(bottom_right_hole)

left_wall_x = 130
right_wall_x = 755
top_wall_y = 110
bottom_wall_y = 850

M_x = width/2 - 3*ball_radius/2
M_y = 4*height/5
main_ball_vel_x = 0
main_ball_vel_y = 0

friction = 0.001
boost = 100

def setup():
    dy = ball_radius*math.sqrt(3)
    
    for row in range(5,0,-1):
        y = (5-row)*dy + 2*height/9
        start_x = width/2-ball_radius*(row-1)
        for i in range(row):
            x = start_x +2*ball_radius*i
            pos.append((round(x,2)-5*ball_radius/4,round(y,2)))
            vel.append((0,0))
            
    selected_positions = random.sample(pos,total_balls)
    selected_colours = random.sample(colours,total_balls)
        
    for i in range(total_balls):
        colour = selected_colours[i]
        position = np.array(selected_positions[i],dtype=float)
        velocity = np.array((0,0),dtype=float)
        balls.append([position,velocity,colour_map[colour]])

        #[((x,y),(r,g,b)),...] so balls[i] is ith ball, balls[i][0] is ith ball pos, balls[i][1] is ith ball vel, balls[i][0][0] is x pos, balls[i][0][1] is y pos, balls[i][1][0] is x vel, balls[i][1][1] is y vel, balls[i][2] is the ith ball rgb, balls[i][2][0] is red, balls[i][2][1] is green, balls[i][2][2] is blue

def elastic_collision_2d(r1, v1, r2, v2):

    r1 = np.array(r1, dtype=float)
    v1 = np.array(v1, dtype=float)
    r2 = np.array(r2, dtype=float)
    v2 = np.array(v2, dtype=float)

    delta_pos = r1 - r2
    delta_vel = v1 - v2

    dist_squared = np.dot(delta_pos, delta_pos)
    if dist_squared == 0:
        # Perfect overlap – skip to avoid division by zero
        return v1, v2

    dot_product = np.dot(delta_vel, delta_pos)
    scaling = dot_product / dist_squared
    collision_vector = scaling * delta_pos

    v1f = v1 - collision_vector
    v2f = v2 + collision_vector

    return v1f, v2f

def separate_balls(ball1, ball2):
    delta_pos = ball1[0] - ball2[0]
    dist = np.linalg.norm(delta_pos)
    overlap = 2 * ball_radius - dist
    if overlap > 0 and dist != 0:
        direction = delta_pos/dist
        ball1[0] += direction*(overlap/2)
        ball2[0] -= direction*(overlap/2)

def draw_arrow(screen, start, end, color=(0, 0, 0), width=5, head_length=15, head_width=10):
    pygame.draw.line(screen, color, start, end, width)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)

    tip_x = end[0] + head_length * math.cos(angle)
    tip_y = end[1] + head_length * math.sin(angle)
    arrow_tip = (tip_x, tip_y)
    
    left = (
        tip_x - head_length * math.cos(angle) + head_width * math.sin(angle) / 2,
        tip_y - head_length * math.sin(angle) - head_width * math.cos(angle) / 2
    )
    right = (
        tip_x - head_length * math.cos(angle) - head_width * math.sin(angle) / 2,
        tip_y - head_length * math.sin(angle) + head_width * math.cos(angle) / 2
    )

    pygame.draw.line(screen, color, start, end, 2)
    pygame.draw.polygon(screen, color, [arrow_tip, left, right])

def scale_vector(start, end, scale):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    return (start[0] + dx*scale, start[1] + dy*scale)

setup()

dragging = False
played = False
drag_start_time = 0
drag_start_pos = (0,0)

clock = pygame.time.Clock()

while running:
    dt = clock.tick(60)/1000
    dt = max(dt,0.001)

    screen.blit(background,(-40,-10))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            Mn_x, Mn_y = pygame.mouse.get_pos()
            dx = M_x - Mn_x
            dy = M_y - Mn_y
            if dx**2 + dy**2 <= ball_radius**2:
                dragging = True
                drag_start_time = time.time()
                drag_start_pos = (M_x,M_y)
                
        elif event.type == pygame.MOUSEMOTION and dragging:
            M_x, M_y  = pygame.mouse.get_pos()
            
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            played = True
            dragging = False
            drag_end_time = time.time()
            drag_end_pos = pygame.mouse.get_pos()
            dt = drag_end_time-drag_start_time

            if dt > 0:
                dx = drag_end_pos[0] - drag_start_pos[0]
                dy = drag_end_pos[1] - drag_start_pos[1]
                main_ball_vel_x += dx/dt
                main_ball_vel_y += dy/dt           

    if not dragging:
        main_ball_vel_x *= math.exp(-friction * dt)
        main_ball_vel_y *= math.exp(-friction * dt)
        M_x -= main_ball_vel_x
        M_y -= main_ball_vel_y

        if main_ball_vel_x <= 0.1:
            main_ball_vel_x = 0
        if main_ball_vel_y <= 0.1:
            main_ball_vel_y = 0
            
    for i in range(len(balls)):
        dx = M_x - balls[i][0][0]
        dy = M_y - balls[i][0][1]
        if dx**2 + dy**2 < (2*ball_radius)**2:
            M = np.array([M_x, M_y])
            r2 = balls[i][0]
            v2 = balls[i][1]
            M_v = np.array([main_ball_vel_x,main_ball_vel_y])
            v1f, v2f = elastic_collision_2d(M, M_v, r2, v2)
            v1 = v2f
            v2 = v1f
            M_x += M_v[0]
            M_y += M_v[1]
            balls[i][1] = v2*boost*dt
            balls[i][0] += balls[i][1]
            if balls[i][1][0] <= 0.1:
                balls[i][1][0] = 0
            if balls[i][1][0] <= 0.1:
                balls[i][1][0] = 0
                
            main_ball_vel_x = v1[0]
            main_ball_vel_y = v1[1]


    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            pos_i = balls[i][0]
            pos_j = balls[j][0]
            dx, dy = pos_i - pos_j
            if np.dot(dx, dx) + np.dot(dy, dy) < (2*ball_radius)**2:
                if played:
                    collision.play()
                    played = False
                v1f, v2f = elastic_collision_2d(pos_i, balls[i][1], pos_j, balls[j][1])
                balls[i][1] = v1f
                balls[j][1] = v2f
                
                separate_balls(balls[i], balls[j])

    for i in range(len(balls)):
        pos = balls[i][0]
        vel = balls[i][1]

        # Left or Right Wall
        if pos[0] - ball_radius < left_wall_x:
            pos[0] = left_wall_x + ball_radius
            vel[0] *= -1
        elif pos[0] + ball_radius > right_wall_x:
            pos[0] = right_wall_x - ball_radius
            vel[0] *= -1

        # Top or Bottom Wall
        if pos[1] - ball_radius < top_wall_y:
            pos[1] = top_wall_y + ball_radius
            vel[1] *= -1
        elif pos[1] + ball_radius > bottom_wall_y:
            pos[1] = bottom_wall_y - ball_radius
            vel[1] *= -1

    # Cue ball wall collision
    if M_x - ball_radius < left_wall_x:
        M_x = left_wall_x + ball_radius
        main_ball_vel_x *= -1
    elif M_x + ball_radius > right_wall_x:
        M_x = right_wall_x - ball_radius
        main_ball_vel_x *= -1

    if M_y - ball_radius < top_wall_y:
        M_y = top_wall_y + ball_radius
        main_ball_vel_y *= -1
    elif M_y + ball_radius > bottom_wall_y:
        M_y = bottom_wall_y - ball_radius
        main_ball_vel_y *= -1

    dhole = 40
    new_balls = []
    
    for i in range(len(balls)):
        bx, by = balls[i][0]
        in_hole = False
        for hole in holes:
            #pygame.draw.circle(screen,(0,0,0),(hole[0],hole[1]),dhole) # Hit box detection
            hx, hy = hole
            dx = bx - hx
            dy = by - hy
            if dx**2 + dy**2 <= (dhole)**2:
                in_hole = True
                if score_count < 14 and balls[i][2] != (0,0,0):
                    score_count = score_count + 1
                    score.play()
                    cheer.play()
                    break
                else:
                    quit()
                break
            
        if not in_hole:
            new_balls.append(balls[i])

    balls = new_balls
    
    if dragging:
        start_pos = drag_start_pos
        end_pos = pygame.mouse.get_pos()
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx**2 + dy**2)
        dx /= length
        dy /= length

        scale = 100
        flipped_end = (start_pos[0] - scale*dx,start_pos[1] - scale*dy)

        raw_flipped_end_arrow = (
            2 * drag_start_pos[0] - pygame.mouse.get_pos()[0],
            2 * drag_start_pos[1] - pygame.mouse.get_pos()[1]
        )
        
        draw_arrow(screen, drag_start_pos,flipped_end)

        pygame.draw.line(screen,(0,0,0),start_pos,flipped_end,1)
        
    new_balls = []

    for ball in balls:
        pygame.draw.circle(screen, ball[2], ball[0], ball_radius)
        
    pygame.draw.circle(screen,colour_map["white"],(M_x,M_y),ball_radius)
    pygame.display.update()
