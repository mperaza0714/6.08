import sys
import datetime

sys.path.append("__HOME__/spaceteam")

import gamedb


def request_handler(req):
    with gamedb.GameDB() as db:
        if req["method"] == "GET":
            form = req["values"]
            game_id = form["game_id"]

            s = ""
            s += str(db.get_lives(game_id))
            s += ", "
            t = db.get_start_time(game_id)
            now = datetime.datetime.now()

            s += str(int(100 - (now - t).total_seconds()))
            s += ", "
            s += str(db.get_score(game_id))

            return s
