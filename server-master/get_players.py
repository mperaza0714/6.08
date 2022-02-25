import sys

sys.path.append("__HOME__/spaceteam")

import gamedb


def request_handler(req):
    with gamedb.GameDB() as db:
        if req["method"] == "GET":
            form = req["values"]
            game_id = form["game_id"]
            players = db.get_players(game_id)
            s = ""
            for p in players:
                s += p[0]
                s += ", "
            return s
