import sys

sys.path.append("__HOME__/spaceteam/")
from gamedb import GameDB
import datetime


def request_handler(request):
    if request["method"] == "POST":
        with GameDB() as db:
            module_dict = request["form"]
            user = module_dict["user"]
            game_id = db.get_active_game()
            instruction = db.get_next_instruction_queue(user, game_id)
            target = instruction[6]
            if module_dict[instruction[3]] == instruction[4]:
                db.update_instructions_queue(target, game_id)
                db.add_score(1)
                return "Success"
            elif db.get_instruction_time(user, game_id) > datetime.timedelta(
                seconds=18
            ):
                db.update_instructions_queue(target, game_id)
                db.lose_life(1)
                return "Fail"
            return f"Instruction: {instruction}, modules_dict: {module_dict}"
    if request["method"] == "GET":
        with GameDB() as db:
            return db.print_instructions_queue()
    else:
        return "Invalid Request"
