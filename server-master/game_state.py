import sys

sys.path.append("__HOME__/spaceteam")

import gamedb


def game_end():  # return true if game is over
    with gamedb.GameDB() as db:
        return db.game_over() or db.game_won()


def game_start():  # returns true if game has started and false if lobby is still open
    with gamedb.GameDB() as db:
        if not game_end():
            game_id = db.get_active_game()
            return db.get_start_time(game_id) < gamedb.sec_ago(30)
        return False
