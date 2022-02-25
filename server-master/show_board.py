import sys

sys.path.append("__HOME__/spaceteam/")
import consts
from gamedb import GameDB


def request_handler(request):
    with GameDB() as db:
        if request["method"] == "GET":
            f = open("__HOME__/spaceteam/html/game.html", "r")
            page = f.read()
            username = request["values"]["user"]
            game_id = request["values"]["game_id"]

            # game_ids = db.get_game_id_from_player(username)
            # for g in game_ids:
            #     game_id = g[0]
            board_layout_filename = db.get_board_layout(username, game_id)
            if board_layout_filename == "MIT_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/ZlNGNme.png"></span><br><br><br>',
                )
            elif board_layout_filename == "mit_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/ZlNGNme.png"></span><br><br><br>',
                )
            elif board_layout_filename == "harry_potter_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/HMNHb0b.png"></span><br><br><br>',
                )
            elif board_layout_filename == "marvel_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/nlPQjmU.png"></span><br><br><br>',
                )
            elif board_layout_filename == "star_wars_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/JnoAayK.png"></span><br><br><br>',
                )
            elif board_layout_filename == "back_to_the_future_board.png":
                page = page.replace(
                    "<span><img></span>",
                    '<span><img src="https://i.imgur.com/T2MeYhj.png"></span><br><br><br>',
                )
            else:
                page = page.replace(
                    "<span><img></span>",
                    "<span>{}</span><br><br><br>".format(board_layout_filename),
                )

            page = page.replace("WEB_ROOT", consts.WEB_ROOT)
            page = page.replace("NUMBER_I_NEED", str(game_id))

            return page
            # FIXME: HTML THINGS

        if request["method"] == "POST":
            # # For demonstrating instructions and board and removing them
            # if "button" in request["form"]:
            #     if request["form"]["button"] == "0":
            #         user = request["form"]["user"]
            #         db.remove_instruction(
            #             user, db.get_next_instruction(user)[-1]
            #         )
            #     elif request["form"]["button"] == "1":
            #         # just in case we need to populate database with working values, post with button = 1
            #         db.add_board(
            #             "Panhel",
            #             "Answer Checkers",
            #             "My Major",
            #             "Productivity",
            #             "GPA",
            #             "Dorm Row",
            #             "MIT Timer",
            #             "Brass Rattler",
            #             "html/board2.png",
            #         )
            #         db.grab_board("mperaza")
            #         db.generate_instructions("mperaza")
            # # show values already in prepopulated database
            # instructions_list = db.get_instructions_text("mperaza")
            # board_layout_filename = db.get_board_layout("mperaza")
            # # FIXME: HTML THINGS
            return
