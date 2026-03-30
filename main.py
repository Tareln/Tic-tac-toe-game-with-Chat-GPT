from math import fabs
from openai import OpenAI
import os
from dotenv import load_dotenv

class Board:
    def __init__(self):
        self.board = [0] * 9
        self.symbols = {0: " ", 1: "O", 2: "X"}

    def update(self, moves, player):
        for move in moves:
            row = ord(move[0]) - ord('A')
            col = int(move[1]) - 1
            index = row * 3 + col
            self.board[index] = player

    def draw(self):
        for i in range(0, 9, 3):
            wiersz = [self.symbols[self.board[i]], self.symbols[self.board[i+1]], self.symbols[self.board[i+2]]]
            print(" | ".join(wiersz))
            if i < 6:
                print("--+---+--")

    def check_winner(self):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in winning_combinations:
            if self.board[a] != 0 and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return 0

    def check_draw(self):
        return 0 not in self.board

class GPTPlayer:
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI()
        self.model_name = "gpt-4.1-mini"

    def table_to_string(self, tab):
        return " ".join(tab)

    def to_chat(self, move, past_move_p, past_move_g):
        return [
            {"role": "system", "content": """You are a player in the match of tic tac toe. Columns are enumerated with letters A,B and C. Rows are enumerated
            with numbers 1,2,3. For example a middle spot has a coordinates of B2. 
            Win condition is to get 3 moves in the same column, row or diagonal. For example A1, B1, C1 is a win or A1, A2, A3 is also a win.
            You have to try to win against human player. 
            For his every move you have to think if you can block your opponent if yes do it, if not think about a good move and then give back your answear using only coordinates. 
            Give answear using only coordinates."""},
            {"role": "user", "content": "Past player moves: " + self.table_to_string(past_move_p)},
            {"role": "assistant", "content": "Past GPT moves: " + self.table_to_string(past_move_g)},
            {"role": "user", "content": "My next move is: "+ move}
        ]

    def chat_move(self, move, past_move_p, past_move_g):
        response = self.client.chat.completions.create(
            model= self.model_name,
            messages=self.to_chat(move, past_move_p, past_move_g)
        )
        return response.choices[0].message.content

class Game:
    def __init__(self):
        self.board = Board()
        self.gpt = GPTPlayer()
        self.move_log_p = []
        self.move_log_g = []
        self.first_turn = True

    def check_end_game(self):
        if self.board.check_winner() == 2:
            self.board.draw()
            print("Zwycięża Chat GPT")
            return True
        elif self.board.check_draw():
            self.board.draw()
            print("Remis")
            return True
        return False

    def run(self):
        while True:
            if self.first_turn:
                move_p = input("Witaj w grze w kółko i krzyżyk.\nKolumny to A,B,C a wiersze to 1,2,3. Na przykład środek to B2.\nPodaj swój pierwszy ruch: ")
                move_g = self.gpt.chat_move(move_p, self.move_log_p, self.move_log_g)
                print(move_g)
                self.move_log_p.append(move_p)
                self.move_log_g.append(move_g)
                self.first_turn = False
            else:
                move_p = input("Podaj swój następny ruch: ")
                move_g = self.gpt.chat_move(move_p, self.move_log_p, self.move_log_g)
                print(move_g)
                self.move_log_p.append(move_p)
                self.move_log_g.append(move_g)

            self.board.update(self.move_log_p, 1)
            if self.board.check_winner() == 1:
                self.board.draw()
                print("Zwycięża gracz")
                return

            self.board.update(self.move_log_g, 2)
            if self.check_end_game():
                return

            print("Plansza po tej rundzie:")
            self.board.draw()

if __name__ == "__main__":
    Game().run()