import sys
import json

sys.path.append("__HOME__/spaceteam")

import gamedb
import consts
import random
import boards


def random_m_username(game_id, db):
    names = [
        "Alfa",
        "Bravo",
        "Charlie",
        "Delta",
        "Echo",
        "Foxtrot",
        "Golf",
        "Hotel",
        "India",
        "Juliett",
        "Kilo",
        "Lima",
        "Mike",
        "November",
        "Oscar",
        "Papa",
        "Quebec",
        "Romeo",
        "Sierra",
        "Tango",
        "Uniform",
        "Victor",
        "Whiskey",
        "X-ray",
        "Yankee",
        "Zulu",
    ]
    username = random.choice(names)
    while True:
        try:
            db.join_game(username, game_id)
            return username
        except:
            names.remove(username)
            username = random.choice(names)


def random_username():
    # FIXME: use dictionary words
    username = ""
    for _ in range(5):
        username += chr(random.randint(ord("a"), ord("z")))
    for _ in range(2):
        username += str(random.randint(0, 9))
    return username


def request_handler(req):
    with gamedb.GameDB() as db:
        if req["method"] == "GET":
            game_id = db.new_game()
            f = open("__HOME__/spaceteam/html/index.html", "r")
            page = f.read()
            ret = '<span>game id: {}<br></span><span id = "lobby">game lobby closes in <p id="seconds">{}</p> seconds</span>'.format(
                game_id, 30
            )
            page = page.replace("<span>form</span>", "")
            page = page.replace(
                """<span><a href="WEB_ROOT/home.py">go home</a></span>""", ""
            )
            page = page.replace("WEB_ROOT", consts.WEB_ROOT)
            page = page.replace("GAME_ID", str(game_id))
            page = page.replace("NUMBER_I_NEED", str(game_id))
            return page.replace("<span></span>", ret)
        elif req["method"] == "POST":
            if req["is_json"]:
                data = req["data"]
                form = json.loads(data)
            else:
                form = req["form"]
            # username = random_username()

            game_id = form["game_id"]
            if db.get_start_time(game_id) < gamedb.sec_ago(30):
                return "Game has already started"
            else:
                username = random_m_username(game_id, db)
                # db.clear_user_boards()
                # db.join_game(username, game_id)
                # db.add_board(*boards.return_board(1))

                db.grab_board(username, game_id)
                # db.generate_instructions(username, game_id)
                db.generate_instructions(username, game_id)
                return username
