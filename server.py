import random
import socket

# Game Constants
CHASE = "The Chaser"
PLAYER = "Player"
ANSWERS = ["A", "B", "C", "D"]
WELCOME_MESSAGE = "Welcome to The Chase!"
QUESTION_MESSAGE = "Question: {question}"
ANSWER_OPTIONS = "\n".join("{}. {}".format(chr(65 + i), option) for i, option in enumerate(ANSWERS))
SELECT_ANSWER_MESSAGE = "Select your answer (A/B/C/D): "
INCORRECT_MESSAGE = "Incorrect! The correct answer was {correct_answer}."
WIN_MESSAGE = "Congratulations! You have won the game!"
LOSE_MESSAGE = "Sorry, you have been caught by the Chaser."

class Chaser:
    def __init__(self, name):
        self.name = name

    def generate_answer(self):
        return random.choice(ANSWERS)

class Question:
    def __init__(self, question, options, correct_answer):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

    def display(self):
        options_str = "\n".join("{}. {}".format(chr(65 + i), option) for i, option in enumerate(self.options))
        return "{}\n{}".format(QUESTION_MESSAGE.format(question=self.question), options_str)


class Game:
    def __init__(self, player_name):
        self.player_name = player_name
        self.chaser = Chaser(CHASE)
        self.questions = []
        self.correct_answers = 0

    def add_question(self, question, options, correct_answer):
        self.questions.append(Question(question, options, correct_answer))

    def ask_question(self, question):
        return question.display()

    def check_answer(self, question, answer):
        if answer == question.correct_answer:
            self.correct_answers += 1

    def end_game(self):
        if self.correct_answers == len(self.questions):
            return WIN_MESSAGE
        else:
            return LOSE_MESSAGE

    def play_game(self, conn):
        conn.sendall(WELCOME_MESSAGE.encode())

        for question in self.questions:
            conn.sendall(self.ask_question(question).encode())
            answer = conn.recv(1024).decode().strip().upper()
            self.check_answer(question, answer)

            if answer == question.correct_answer:
                conn.sendall(b"Correct!\n")
            else:
                conn.sendall(INCORRECT_MESSAGE.format(correct_answer=question.correct_answer).encode())

        result_message = self.end_game()
        conn.sendall(result_message.encode())

def run_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print("Server is up and listening on {}:{}".format(server_address[0], server_address[1]))

    while True:
        # Wait for a connection
        print("Waiting for a connection...")
        conn, client_address = server_socket.accept()
        print("Connected to client:", client_address)

        try:
            # Create a new game
            game = Game(PLAYER)

            # Add questions
            game.add_question("What is the capital of France?", ["Paris", "Berlin", "Rome", "London"], "A")
            game.add_question("Who painted the Mona Lisa?", ["Leonardo da Vinci", "Vincent van Gogh", "Pablo Picasso", "Claude Monet"], "A")
            game.add_question("What is the largest planet in our solar system?", ["Jupiter", "Mars", "Saturn", "Neptune"], "A")

            # Start the game
            game.play_game(conn)
        finally:
            # Clean up the connection
            conn.close()
            print("Connection closed\n")

# Run the server
run_server()