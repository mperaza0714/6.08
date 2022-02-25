#!/usr/bin/env python3
import sys

sys.path.append("__HOME__/spaceteam")

import consts
import gamedb
from boards import return_board


def request_handler(request):
    with gamedb.GameDB() as db:
        ret = ""
        if request["method"] == "POST":
            if "reset" in request["form"]:
                if request["form"]["reset"]:
                    db.delete_boards()
                    ret = ret + "Boards Removed | "
            if "add" in request["form"]:
                i = request["form"]["add"]
                board = return_board(int(i))
                # return f"{board}"
                db.add_board(*board)
                ret = "Board Added | "
        ret = ret + f"All Boards : {db.all_boards()}"
        return ret
