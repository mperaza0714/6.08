#!/usr/bin/env python3

import sys

sys.path.append("__HOME__/spaceteam")

import consts
import gamedb
import datetime


def request_handler(req):

    f = open("__HOME__/spaceteam/html/index.html")
    page = f.read()
    form = req["values"]
    if "game_id" in form:
        game_id = form["game_id"]
        with gamedb.GameDB() as db:
            start_time = db.get_start_time(game_id)
        if start_time < gamedb.sec_ago(30):
            ret = "<span>Game has already started</span>"
        else:
            time_left = datetime.datetime.now() - start_time
            ret = '<span>game id: {0}<br></span><span id="lobby">game lobby closes in <p id="seconds">{1}</p> seconds</span>'.format(
                game_id, 30 - int(time_left.total_seconds())
            )
        page = page.replace("GAME_ID", str(game_id))
        page = page.replace('"NUMBER_I_NEED"', str(game_id))
        page = page.replace("<span>form</span>", "")
    else:
        ret = f"""<span>Click <b><a href="{consts.WEB_ROOT}/new_game.py">here</a></b> to start a new game </span>"""
        ret2 = """<span>  
                Click 
                <button onclick="handle()"> here </button> 
                to join a game with id 
                <input id="gamid" type="number" min="1" value="1"> 
                 </span>"""
        page = page.replace("<span>form</span>", ret2)
        page = page.replace(
            """<span><a href="WEB_ROOT/home.py">go home</a></span>""", ""
        )

    page = page.replace("<span></span>", ret)

    page = page.replace("WEB_ROOT", consts.WEB_ROOT)

    return page
