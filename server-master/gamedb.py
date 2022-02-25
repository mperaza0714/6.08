#!/usr/bin/env python3

import sys

sys.path.append("__HOME__/spaceteam")

import consts
import datetime
import sqlite3
import random


def sec_ago(n):
    return datetime.datetime.now() - datetime.timedelta(seconds=n)


class GameDB:
    def __init__(self):
        self.conn = sqlite3.connect(
            consts.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.cur = self.conn.cursor()
        self.__create_tables()

    def __create_tables(self):
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS games "
            "(game_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " start_time TIMESTAMP,"
            " lives INTEGER DEFAULT 5,"
            " score INTEGER DEFAULT 0,"
            " stage INTEGER)"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS players "
            "(username TEXT,"
            " active_game_id INTEGER,"
            " player_id INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS boards "
            "(board_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " in_use INTEGER,"
            " button_panel_1 TEXT,"
            " button_panel_2 TEXT,"
            " switch_1 TEXT,"
            " dial_1 TEXT,"
            " slider_1 TEXT,"
            " phototransistor_1 TEXT,"
            " phototransistor_2 TEXT,"
            " imu_1 TEXT,"
            " image_path TEXT);"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS players_boards "
            "(username TEXT,"
            " game_id INTEGER,"
            " board_id INTEGER);"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS instructions "
            "(username TEXT,"
            " game_id INTEGER,"
            " board_id INTEGER,"
            " module TEXT,"
            " modifier TEXT,"
            " instruction TEXT,"
            " ord INTEGER);"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS instructions_queue "
            "(username TEXT,"
            " game_id INTEGER,"
            " board_id INTEGER,"
            " module TEXT,"
            " modifier TEXT,"
            " instruction TEXT,"
            " target_user TEXT,"
            " start_time TIMESTAMP);"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def new_game(self):
        self.cur.execute(
            "INSERT INTO games (start_time) VALUES (?)", (sec_ago(0),),
        )
        return self.cur.lastrowid

    def get_start_time(self, game_id):
        query = self.cur.execute(
            "SELECT start_time FROM games WHERE game_id = ?", (game_id,)
        )
        return query.fetchone()[0]

    def get_lives(self, game_id):
        query = self.cur.execute(
            "SELECT lives FROM games WHERE game_id = ?", (game_id,)
        )
        return query.fetchone()[0]

    def get_score(self, game_id):
        query = self.cur.execute(
            "SELECT score FROM games WHERE game_id = ?", (game_id,)
        )
        return query.fetchone()[0]

    def join_game(self, username, game_id):
        # self.cur.execute(
        #    "UPDATE OR IGNORE players SET active_game_id = ? WHERE username = ?",
        #    (game_id, username),
        # )
        query = self.cur.execute(
            "SELECT * FROM players WHERE username = ? AND active_game_id = ?",
            (username, game_id),
        ).fetchone()
        if query:
            raise NameError("name and game_id already in game")
        self.cur.execute(
            "INSERT INTO players (username, active_game_id) VALUES (?, ?)",
            (username, game_id),
        )

    def get_all_users(self, game_id):
        query = self.cur.execute(
            "SELECT username FROM players WHERE active_game_id = ?;", (game_id,)
        ).fetchall()
        result = []
        for user in query:
            result.append(user[0])
        return result

    def get_active_game(self):
        query = self.cur.execute("SELECT game_id FROM games ORDER BY game_id DESC;")
        return query.fetchone()[0]

    def get_game_time(self):
        game_id = self.get_active_game()
        start_time = self.get_start_time(game_id)
        return datetime.datetime.now() - start_time

    def get_remaining_time(self, duration=120):
        elapsed = self.get_game_time()
        return datetime.timedelta(seconds=duration) - elapsed

    def get_active_lives(self):
        game_id = self.get_active_game()
        return self.get_lives(game_id)

    def get_rand_user(self, user, game_id):
        users = self.get_all_users(game_id)
        x = user
        while x == user:
            x = random.choice(users)
        return x

    def lose_life(self, lost):
        old_lives = self.get_active_lives()
        new_lives = old_lives - lost
        self.cur.execute(
            """UPDATE games SET lives = ? WHERE game_id = ?;""",
            (new_lives, self.get_active_game()),
        )

    def get_active_score(self):
        game_id = self.get_active_game()
        return self.get_score(game_id)

    def add_score(self, bonus):
        old_score = self.get_active_score()
        new_score = old_score + bonus
        self.cur.execute(
            """UPDATE games SET score = ? WHERE game_id = ?;""",
            (new_score, self.get_active_game()),
        )

    def game_over(self):
        return any(
            (
                self.get_active_lives() <= 0,
                self.get_game_time() > datetime.timedelta(seconds=100),
            )
        )

    def game_won(self):
        return self.get_active_score() >= 20

    def empty_instruction_queue(self, game_id):
        query = self.cur.execute(
            "SELECT * FROM instructions_queue WHERE game_id = ?;", (game_id,)
        ).fetchone()
        return query is None

    def start_instruction_queue(self, user, game_id):
        # put an instruction in the instruction queue
        self.generate_instructions(user, game_id)
        next_instruct = self.get_next_instruction(user, game_id)
        self.remove_instruction(user, game_id, next_instruct[-1])
        self.add_instruction_queue(user, game_id, next_instruct)
        return self.get_next_instruction_queue(user, game_id)

    def start_queue(self, game_id):
        users = self.get_all_users(game_id)
        for user in users:
            target = self.get_rand_user(user, game_id)
            next_instruct = self.get_next_instruction(target, game_id)
            self.remove_instruction(target, game_id, next_instruct[-1])
            self.add_instruction_queue(game_id, user, next_instruct)

    def get_next_instruction_queue(self, user, game_id):
        # return next instruction in the queue
        if self.empty_instruction_queue(game_id):
            self.start_queue(game_id)
            return ":("
        query = self.cur.execute(
            "SELECT * FROM instructions_queue WHERE username = ? AND game_id = ?;",
            (user, game_id),
        ).fetchone()
        return query

    def show_instruction_queue(self, target, game_id):
        ####must implement in other files####
        query = self.cur.execute(
            "SELECT * FROM instructions_queue WHERE target_user = ? AND game_id = ?;",
            (target, game_id),
        ).fetchone()
        # if query:
        #     start_time = query[-1]
        #     elapsed = datetime.datetime.now() - start_time
        #     if elapsed > datetime.timedelta(seconds = 10):
        #         self.update_instructions_queue(target, game_id)
        #         # self.lose_life(1)
        if query is None:
            self.update_instructions_queue(target, game_id)
            return f" sorry {target} but here {self.get_next_instruction_queue(target, game_id)}"
        return query[-3]

    def add_instruction_queue(self, game_id, target_user, instruction):
        ###IN THIS FUNCTION, TARGET IS THE USER WHO IS BEING SHOWN THE INSTRUCTION###
        instruct = instruction[:6]
        self.cur.execute(
            "INSERT INTO instructions_queue"
            "(username,"
            " board_id,"
            " module,"
            " modifier,"
            " instruction,"
            " target_user,"
            " game_id,"
            " start_time) VALUES(?,?,?,?,?,?,?,?);",
            (
                *instruct[:1],
                *instruct[2:],
                target_user,
                game_id,
                datetime.datetime.now(),
            ),
        )

    def remove_instruction_queue(self, user, game_id):
        self.cur.execute(
            "DELETE FROM instructions_queue WHERE target_user = ? AND game_id = ?;",
            (user, game_id),
        )

    def get_instruction_time(self, user, game_id):
        instruct = self.get_next_instruction_queue(user, game_id)
        start_time = instruct[-1]
        elapsed = datetime.datetime.now() - start_time
        return elapsed

    def update_instructions_queue(self, user, game_id):
        ###IN THIS FUNCTION, TARGET IS THE USER WHOSE BOARD THE INSTRUCTION CORRESPONDS TO###
        self.remove_instruction_queue(user, game_id)
        target = self.get_rand_user(user, game_id)
        next_instruct = self.get_next_instruction(target, game_id)
        self.remove_instruction(target, game_id, next_instruct[-1])
        self.add_instruction_queue(game_id, user, next_instruct)
        return self.get_next_instruction_queue(user, game_id)

    def print_instructions_queue(self):
        game_id = self.get_active_game()
        query = self.cur.execute(
            "SELECT * FROM instructions_queue WHERE game_id = ?;", (game_id,)
        )
        return query.fetchall()

    def add_board(
        self,
        button_panel_1,
        button_panel_2,
        switch_1,
        dial_1,
        slider_1,
        phototransistor_1,
        phototransistor_2,
        imu_1,
        image_path,
    ):  # can add more params later
        # Add a new row into board table with a board
        self.cur.execute(
            """INSERT INTO boards
                    (in_use,
                    button_panel_1,
                    button_panel_2,
                    switch_1,
                    dial_1,
                    slider_1,
                    phototransistor_1,
                    phototransistor_2,
                    imu_1,
                    image_path)
                    VALUES(?,?,?,?,?,?,?,?,?,?);""",
            (
                0,
                button_panel_1,
                button_panel_2,
                switch_1,
                dial_1,
                slider_1,
                phototransistor_1,
                phototransistor_2,
                imu_1,
                image_path,
            ),
        )

    def grab_board(self, user, game_id):
        # Randomly choose a board for a user
        # Store user with their board id in a table
        boards = self.cur.execute(
            """SELECT * FROM boards WHERE in_use = 0;"""
        ).fetchall()
        board = random.choice(boards)
        board_id = board[0]
        self.cur.execute(
            """INSERT OR IGNORE INTO players_boards VALUES(?, ?, ?);""",
            (user, game_id, board_id),
        )
        # self.cur.execute(
        #     """UPDATE OR IGNORE players_boards SET board_id = ? WHERE username = ?""",
        #     (board_id, user),
        # )
        self.cur.execute(
            """UPDATE boards SET in_use = 1 WHERE board_id = ?;""", (board_id,)
        )
        layout = board[-1]
        return layout

    def get_board(self, user, game_id):
        # returns a user's board
        board_id = self.cur.execute(
            """SELECT board_id FROM players_boards WHERE username = ? AND game_id = ?;""",
            (user, game_id),
        ).fetchone()[0]
        board = self.cur.execute(
            """SELECT * FROM boards WHERE board_id = ?;""", (board_id,)
        ).fetchone()
        return board

    def get_board_layout(self, user, game_id):
        return self.get_board(user, game_id)[-1]

    def all_boards(self):
        boards = self.cur.execute("""SELECT * FROM boards;""").fetchall()
        return boards

    def get_players(self, game_id):
        players = self.cur.execute(
            """SELECT username FROM players WHERE active_game_id = ?;""", (game_id,)
        ).fetchall()
        return players

    def generate_instructions(self, user, game_id, n=20):
        # Given a board, randomly generate a list of instructions (20 items long)
        board = self.get_board(user, game_id)
        board_id = board[0]
        modules = board[2:-1]  # all modules
        last_switch = random.randint(0, 1)
        last_slide = None
        last_dial = None

        def generate_button_instruction(mods, i, shift):
            # Press a button, 1 to 4
            modifier = random.randint(1, 4)
            m_name = mods[i]
            text = f"Press {modifier} on the {m_name}"
            return f"button_panel_{i + shift}", modifier, text

        def generate_switch_instruction(mods, i, shift, ls):
            # Flip a switch to On or Off
            modifier = 0 if ls else 1
            m_name = mods[i]
            state = "On" if modifier else "Off"
            text = f"Flip {m_name} to {state}"
            return f"switch_{i - shift}", modifier, text

        def generate_slider_instruction(mods, i, shift, ls):
            # Set slider to Low Medium or High, or maybe levels?
            states = ["Low", "Medium", "High"]
            modifier = random.randint(0, 2)
            while modifier == ls:
                modifier = random.randint(0, 2)
            m_name = mods[i]
            state = states[modifier]
            text = f"Push {m_name} to {state}"
            return f"slider_{i - shift}", modifier, text

        def generate_dial_instruction(mods, i, shift, ld):
            # Turn knob to 1-4
            modifier = random.randint(1, 4)
            while modifier == ld:
                modifier = random.randint(1, 4)
            m_name = mods[i]
            text = f"Turn {m_name} to level {modifier}"
            return f"dial_{i - shift}", modifier, text

        def generate_phototransistor_instruction(mods, i, shift):
            # The instruction is always just to wave in front of it
            m_name = mods[i]
            text = f"Activate {m_name}!"
            return f"phototransistor_{i-shift}", 1, text

        def generate_imu_instruction(mods, i, shift):
            m_name = mods[i]
            text = f"Shake your controller!"
            return f"imu_{i-shift}", 1, text

        def generate_buttonlist_instruction(mods, i, shift):
            # Press a button, 1 to 4
            _range = random.randint(2, 4)
            modifier = [random.randint(1, 4) for _ in range(_range)]
            m_name = mods[i]
            text = f"Press buttons on the {m_name} in this order: {modifier}"
            return f"button_panel_{i - shift}", modifier, text

        for i in range(n):
            # randomly generate instruction, with i as instruction order
            module_index = random.randint(0, 7)  ##Update once everything works
            if module_index in (0, 1):
                instruct = generate_button_instruction(modules, module_index, 1)
            if module_index in (2,):
                instruct = generate_switch_instruction(
                    modules, module_index, 1, last_switch
                )
                last_switch = instruct[1]
            if module_index in (3,):
                instruct = generate_dial_instruction(
                    modules, module_index, 2, last_dial
                )
                last_dial = instruct[1]
            if module_index in (4,):
                instruct = generate_slider_instruction(
                    modules, module_index, 3, last_slide
                )
                last_slide = instruct[1]
            if module_index in (5, 6):
                instruct = generate_phototransistor_instruction(
                    modules, module_index, 4
                )
            if module_index in (7,):
                instruct = generate_imu_instruction(modules, module_index, 6)
            # if module_index in (6,):
            #     #instruct = generate_buttonlist_instruction(modules, module_index, 5)
            #     instruct = generate_ball_instruction(modules, module_index, 5)

            instruction = (
                (user, game_id, board_id) + instruct + (i,)
            )  # Make the full row

            self.cur.execute(
                """INSERT INTO instructions VALUES(?,?,?,?,?,?,?);""", instruction,
            )

    def get_instructions(self, user, game_id):
        # returns list of user instructions in order
        instructs = self.cur.execute(
            """SELECT * FROM instructions WHERE username = ? AND game_id = ? ORDER BY ord;""",
            (user, game_id),
        ).fetchall()
        return instructs

    def get_next_instruction(self, user, game_id):  # get_instructions[0]
        # return only the next instruction
        return self.get_instructions(user, game_id)[0]

    def get_instructions_text(self, user, game_id):
        instructs = self.get_instructions(user, game_id)
        s = ""
        for row in instructs:
            s = s + row[5] + " | \n"
        return s

    def remove_instruction(self, user, game_id, instruction_number):
        # remove the next instruction, given it has been satisfied or time is up
        self.cur.execute(
            """DELETE FROM instructions WHERE username = ? AND game_id = ? AND ord = ?;""",
            (user, game_id, instruction_number),
        )

    def clear_user_boards(self):
        # drops table with all users and their boards, along with all user instructions
        self.cur.execute("""DELETE FROM players;""")
        self.cur.execute("""DELETE FROM players_boards;""")
        self.cur.execute("""DELETE FROM instructions""")
        self.cur.execute("""DELETE FROM instructions_queue""")
        self.cur.execute("""UPDATE boards SET in_use = 0;""")

    def delete_boards(self):
        # deletes all boards in db
        self.cur.execute("""DELETE FROM boards;""")

    def delete_board(self, board_id):
        # remove a board from db
        self.cur.execute("""DELETE FROM boards WHERE board_id = ?;""", (board_id,))
