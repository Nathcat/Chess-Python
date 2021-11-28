# Chess-Python
A Chess engine written in Python.

Created by Nathcat 2021

Below is an example usage of the ChessEngine

```Python
"""
ChessEngine example usage

@author Nathan "Nathcat" Baines
"""


from ChessEngine import *  # Import the ChessEngine script
import os
import platform


def ask_exit():
    """
    Asks the user if they are sure they want to exit the game
    """
    answer = input("\n\nAre you sure? (y/n) > ")
    if answer in ["y", "Y"]:
        exit(0)


if __name__ == "__main__":
    # Determine the terminal clear command for this platform
    clear_command = ""
    if platform.system() == "Windows":
        clear_command = "cls"

    else:
        clear_command = "clear"

    chess = ChessEngine()  # Create an instance of ChessEngine
    front_end = FrontEnd()  # Create an instance of FrontEnd
    side_names = ["White", "Black"]  # The names of each side
    message = ""  # The message that should be shown in the next frame

    while True:
        os.system(clear_command)  # Clear the screen

        front_end.render(chess.pieces)  # Render the chess board

        if chess.checkmate:  # If checkmate has been reached, quit the game
            print("\n\n\u001b[31mCheckmate!\u001b[0m")
            exit(0)

        print(message)  # Show the message from the last frame

        message = ""

        print(f"\n\n{side_names[chess.turn_counter.turn]}'s turn")

        try:
            # Ask the user to enter the coordinates of a chess piece
            selection = input("\n\nSelect a piece > ")
            if selection == "exit":
                ask_exit()

            selection = selection.split(" ")

            # Split into coordinate list
            for x in range(0, len(selection)):
                selection[x] = int(selection[x])

            # Ask the user the position they want to move their selected piece to
            new_position = input("\nWhere to move to > ")
            if new_position == "exit":
                ask_exit()

            new_position = new_position.split(" ")

            # Split into coordinate list
            for x in range(0, len(new_position)):
                new_position[x] = int(new_position[x])

            try:
                # Try to move the piece
                result, message = chess.move_piece(selection, new_position)

                if not result:
                    message = f"\n\n\u001b[31m{message}\u001b[0m"

                else:
                    message = ""

            except NoSuchPieceException:
                message = "\n\n\u001b[31mThere is no piece there!\u001b[0m"

        except ValueError:
            message = "\n\n\u001b[31mInvalid entry!\u001b[0m"

```
