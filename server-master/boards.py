# All MODULES
button_panels = [
    "Panhel",
    "Answer Checker",
    "Infinity Stones",
    "Ultron",
    "Horcrux",
    "O.W.L.s",
    "Millennium Falcon",
    "Death Star",
    "The DeLorean",
    "Almanac",
]

switches = ["Productivity", "Gamma Rays", "Golden Snitch", "Hyperdrive", "Great Scott"]

sliders = ["Dorm Row", "Pym Particles", "Basilisk", "Podracer", "Hoverboard"]

dials = ["MIT Timer", "S.H.I.E.L.D.", "Time Turner", "Sith", "Clock Tower"]

phototransistors = [
    "Succulent",
    "Solar Car",
    "Spidey Senses",
    "Arc Reactor",
    "Deluminator",
    "Lumos",
    "Holocron",
    "Lightsaber",
    "Lightning Rod",
    "Plutonium",
]

imus = ["DBF", "Sling Ring", "Portkey", "BB-8", "Flux Capacitor"]

image_paths = [
    "mit_board.png",
    "marvel_board.png",
    "harry_potter_board.png",
    "star_wars_board.png",
    "back_to_the_future_board.png",
]


def return_board(i):
    board = [
        button_panels[2 * i],
        button_panels[2 * i + 1],
        switches[i],
        dials[i],
        sliders[i],
        phototransistors[2 * i],
        phototransistors[2 * i + 1],
        imus[i],
        image_paths[i],
    ]
    return board
