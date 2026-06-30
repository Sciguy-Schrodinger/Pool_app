# 🎱 Pool / Billiards

A realistic pool simulation built with **Pygame**.  
Aim, shoot, and pot all the balls in this classic billiards game!

---

## 🎮 Features

- **Realistic physics** — elastic collisions, friction, and momentum transfer
- **Cue ball control** — click and drag to aim and set power
- **15 colored balls** — randomly arranged at the start
- **6 pockets** — pot balls by sinking them into the holes
- **Score tracking** — count how many balls you've potted
- **Sound effects** — collisions, potting, and background music
- **Visual feedback** — arrow indicator for aim direction and power

---

## 🛠️ Technologies Used

- **Python 3** — core logic
- **Pygame** — 2D rendering, input handling, audio

---

## 🚀 How to Run

### Requirements

Install dependencies:

bash
pip install pygame numpy

### Run

python3 pool.py

🎮 Controls
Mouse / Key	Action
Click on Cue Ball	Start aiming
Drag Backward	Set power and direction (drag away from the ball)
Release Mouse	Shoot the cue ball
Close Window	Exit the game

🧠 How It Works

  1.  Aim — click and drag the cue ball to set direction and power

  2.  Shoot — release the mouse to fire the cue ball

  3.  Collisions — balls collide elastically and transfer momentum

  4.  Friction — balls slow down over time

  5.  Potting — balls that enter pockets are removed

  6.  Win condition — pot all 15 balls to win
