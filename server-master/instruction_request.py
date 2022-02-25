import sys

sys.path.append("__HOME__/spaceteam")

from gamedb import GameDB
import game_state as gs


# def request_handler(request):
#     if request["method"] == "GET":
#         if game_state.game_start():
#             user = request["values"]["user"]
#             with GameDB() as db:
#                 return db.get_next_instruction_queue(user)[-3]
#         if game_state.game_end():
#             with GameDB() as db:
#                 if db.game_over(): return "You Lost :("
#                 elif db.game_won(): return "Congratulations!!!"
#
#     elif request["method"] == "POST":
#         return request["form"]
#     else:
#         return "Invalid Request"


def request_handler(request):
    with GameDB() as db:
        if request["method"] == "GET":
            if gs.game_end():
                if db.game_won():
                    return "You Won the Game!!!"
                if db.game_over():
                    return "Game Over, Try Again"
            elif gs.game_start():
                user = request["values"]["user"]
                game_id = db.get_active_game()
                try:
                    return db.show_instruction_queue(user, game_id)
                except Exception as e:
                    return f"this is not working {e}"
            elif not gs.game_start():
                return "Game will start when the lobby closes."
        elif request["method"] == "POST":
            return request["form"]
        else:
            return "Invalid Request"
