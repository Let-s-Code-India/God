from __future__ import annotations

import turtle

from god_ai import aura


def generate_art(command: str) -> None:
    screen = turtle.Screen()
    screen.title("Aura Generative Art")
    artist = turtle.Turtle()
    artist.speed(0)
    artist.penup()
    artist.goto(-150, 0)
    artist.pendown()

    for index in range(12):
        artist.forward(60)
        artist.left(30)
        artist.circle(25)

    artist.hideturtle()
    screen.onkey(lambda: screen.bye(), "q")
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    generate_art("Create a radial geometric pattern")
