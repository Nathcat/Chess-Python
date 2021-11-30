"""
ChessEngine.py

A Chess engine program written in Python.

Author: Nathan "Nathcat" Baines
"""


class NoSuchPieceException(BaseException):
    """
    This Exception is thrown whenever a piece cannot be found in the given
    position.
    """
    def __str__(self):
        """
        Called when the class is cast to a string
        :return: Error message
        """
        return "The selected piece does not exist"


class Vector:
    """
    A Vector class to represent locations on the board, and movements
    of pieces.
    """
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __mul__(self, a):
        """
        :param a: The coefficient to multiply by (float/integer)
        :return: The result of the multiplication
        """
        return Vector(self.x * a, self.y * a)

    def __add__(self, a):
        """
        :param a: The Vector value to add to this Vector
        :return: The result of the addition
        """
        return Vector(self.x + a.x, self.y + a.y)

    def __truediv__(self, a):
        """
        :param a: The float/integer value to divide by
        :return: The result of the division
        """
        return Vector(self.x / a, self.y / a)

    def __sub__(self, a):
        """
        :param a: The Vector value to subtract from this Vector
        :return: The result of the subtraction
        """
        return Vector(self.x - a.x, self.y - a.y)

    def __str__(self):
        """
        Called when this class is cast to a string
        :return: A Coordinate representation of this Vector ie: (x, y)
        """
        return f"({self.x}, {self.y})"

    def __eq__(self, a):
        """
        :param a: The Vector to test
        :return: Whether or not this Vector and Vector a are equal
        """
        return self.x == a.x and self.y == a.y

    def __getitem__(self, index):
        """
        x and y values may be obtained from a Vector with the use of a list index,
        if 0, return x, if 1, return y.

        :param index: The index requested
        :return: The x or y value, depending on the given index, or IndexError
        """
        if index == 0:
            return self.x

        elif index == 1:
            return self.y

        else:
            raise IndexError()

    def is_out_of_bounds(self):
        """
        Test if this Vector is outside the boundary of the Chess board
        :return: A boolean determining whether or not this Vector is outside the boundary of the chess board
        """
        return self.x >= 8 or self.x <= -1 or self.y >= 8 or self.y <= -1


class Piece:
    """
    A parent class for all pieces.
    """
    def __init__(self, index, name, side, position, moves, attacks):
        self.name = name
        self.side = side
        self.position = position
        self.moves = moves
        self.attacks = attacks
        self.index = index

    def move(self, position, pieces, engine):
        """
        Try to move this piece to a new location.

        :param position: The position this piece should try to move to.
        :param pieces: A list of all pieces on the board.
        :param engine: The ChessEngine class managing the game.
        :return: True/False, depending on whether or not the move was executed.
        """
        if not engine.in_check:
            legal_moves = self.get_legal_moves(pieces, engine)
            if position in legal_moves:
                self.position = position

            return position in legal_moves

        else:
            moves = self.get_legal_check_moves(pieces, engine)

            if position in moves and not position.is_out_of_bounds():
                self.position = position
                return True

            else:
                return False

    def attack(self, position, attacked_piece, engine):
        """
        Attempt to attack a piece.

        :param position: The position this piece should move to.
        :param attacked_piece: The piece this move would attack
        :param engine: The ChessEngine managing the game
        :return: True/False, depending on whether or not the move was successful
        """
        if not engine.in_check:
            legal_attacks = self.get_legal_attacks(False, engine)
            if position in legal_attacks and attacked_piece.side != self.side:
                self.position = position

            return position in legal_attacks and attacked_piece.side != self.side

        else:
            attacks = self.get_legal_check_attacks(engine)

            if position in attacks:
                self.position = position
                return True

            else:
                return False

    def get_legal_moves(self, pieces, engine):
        """
        Get all the legal moves for this piece in the current game state.

        :param pieces: A list of all pieces on the board.
        :param engine: The ChessEngine managing the game.
        :return: A list of possible moves this piece could make.
        """
        legal_moves = []
        for move_set in self.moves:
            for move in move_set:
                valid = True

                for piece in pieces:
                    if piece.index == self.index:
                        continue

                    if piece.position == self.position + move:
                        valid = False

                if (self.position + move).is_out_of_bounds():
                    valid = False

                old_position = Vector(self.position.x, self.position.y)
                self.position += move
                engine.check_for_check()
                valid = not engine.in_check
                self.position = old_position
                engine.check_for_check()

                if valid:
                    legal_moves.append(self.position + move)

                else:
                    break

        return legal_moves

    def get_legal_check_moves(self, pieces, engine):
        """
        Get all the legal moves of this piece, given that the king is in check.

        :param pieces: A list of all pieces on the board.
        :param engine: The ChessEngine managing the game.
        :return: A list of possible moves for this piece.
        """
        moves = []

        for move in self.get_legal_moves(pieces, engine):
            old_position = Vector(self.position.x, self.position.y)
            self.position = move
            engine.check_for_check()
            self.position = old_position

            if not engine.in_check and not move.is_out_of_bounds() and engine.get_piece_by_position(move) is None:
                moves.append(move)

            engine.check_for_check()

        return moves

    def get_legal_attacks(self, friendly_fire, engine):
        """
        Get all the legal attacks this piece can make in the current game state.

        :param friendly_fire: Whether or not attacks on this pieces teammates should be included.
        :param engine: The ChessEngine managing the game.
        :return: A list of possible attacks for this piece.
        """
        legal_attacks = []

        for attack_set in self.attacks:
            for attack in attack_set:
                piece = engine.get_piece_by_position(self.position + attack)

                if piece is not None:
                    if piece.index == self.index:
                        continue

                    if piece.side == self.side and not friendly_fire:
                        break

                    legal_attacks.append(self.position + attack)
                    break

        return legal_attacks

    def get_legal_check_attacks(self, engine):
        """
        Get all the possible attacks this piece can make, given that the king is in check.

        :param engine: The ChessEngine managing the game.
        :return: A list of possible attacks for this piece.
        """
        attacks = []

        for threat in engine.threats:
            for attack in self.get_legal_attacks(False, engine):
                if threat.position == attack and not attack.is_out_of_bounds():
                    attacks.append(attack)

        return attacks

    def __str__(self):
        """
        Cast this piece to a string.

        :return: A string representation of this piece with coloured text.
        """
        colour = ""
        if self.side == 0:
            colour = "\u001b[30m"

        else:
            colour = "\u001b[37m"

        return f"{colour}{self.name}\u001b[0m"


class Pawn(Piece):
    """
    Class representing the Pawn piece
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        direction = 1
        if side == 1:
            direction = -1

        super().__init__(index,
                         "Pa",
                         side,
                         position,

                         [
                             [
                                 Vector(0, 1 * direction),
                                 Vector(0, 2 * direction)
                             ]
                         ],

                         [
                             [Vector(-1, 1 * direction)],
                             [Vector(1, 1 * direction)]
                         ])

    def move(self, position, pieces, engine):
        """
        The Pawn should override the move function, as its moves can change.

        :param position: The position this piece should try to move to.
        :param pieces: A list of pieces on the board.
        :param engine: The ChessEngine managing the game.
        :return: Whether or not the move was successful.
        """
        direction = 1
        if self.side == 1:
            direction = -1

        result = super().move(position, pieces, engine)

        if result:
            self.moves = [[Vector(0, 1 * direction)]]

        return result

    def should_promote(self):
        """
        Determine whether or not this Pawn should be allowed to promote.

        :return: True/False, depending on whether or not the Pawn is in a position to promote.
        """
        direction = 1
        if self.side == 1:
            direction = -1

        if direction == 1 and self.position.y == 7:
            return True

        elif direction == -1 and self.position.y == 0:
            return True

        else:
            return False


class Rook(Piece):
    """
    A class representing the Rook piece
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        moves = [
            [
                Vector(-1, 0),
                Vector(-2, 0),
                Vector(-3, 0),
                Vector(-4, 0),
                Vector(-5, 0),
                Vector(-6, 0),
                Vector(-7, 0),
            ],

            [
                Vector(1, 0),
                Vector(2, 0),
                Vector(3, 0),
                Vector(4, 0),
                Vector(5, 0),
                Vector(6, 0),
                Vector(7, 0),
            ],

            [
                Vector(0, -1),
                Vector(0, -2),
                Vector(0, -3),
                Vector(0, -4),
                Vector(0, -5),
                Vector(0, -6),
                Vector(0, -7),
            ],

            [
                Vector(0, 1),
                Vector(0, 2),
                Vector(0, 3),
                Vector(0, 4),
                Vector(0, 5),
                Vector(0, 6),
                Vector(0, 7),
            ]
        ]

        super().__init__(index, "Ro", side, position, moves, moves)


class Bishop(Piece):
    """
    A class representing the Bishop piece.
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        moves = [
            [
                Vector(1, 1),
                Vector(2, 2),
                Vector(3, 3),
                Vector(4, 4),
                Vector(5, 5),
                Vector(6, 6),
                Vector(7, 7),
            ],

            [
                Vector(-1, 1),
                Vector(-2, 2),
                Vector(-3, 3),
                Vector(-4, 4),
                Vector(-5, 5),
                Vector(-6, 6),
                Vector(-7, 7),
            ],

            [
                Vector(1, -1),
                Vector(2, -2),
                Vector(3, -3),
                Vector(4, -4),
                Vector(5, -5),
                Vector(6, -6),
                Vector(7, -7),
            ],

            [
                Vector(-1, -1),
                Vector(-2, -2),
                Vector(-3, -3),
                Vector(-4, -4),
                Vector(-5, -5),
                Vector(-6, -6),
                Vector(-7, -7),
            ]
        ]

        super().__init__(index, "Bi", side, position, moves, moves)


class Knight(Piece):
    """
    A class representing the Knight piece.
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        moves = [
            [Vector(1, 2)],
            [Vector(2, 1)],
            [Vector(2, -1)],
            [Vector(1, -2)],
            [Vector(-1, -2)],
            [Vector(-2, -1)],
            [Vector(-2, 1)],
            [Vector(-1, 2)]
        ]

        super().__init__(index, "Kn", side, position, moves, moves)


class Queen(Piece):
    """
    A class representing the Queen piece
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        moves = [
            [
                Vector(1, 1),
                Vector(2, 2),
                Vector(3, 3),
                Vector(4, 4),
                Vector(5, 5),
                Vector(6, 6),
                Vector(7, 7),
            ],

            [
                Vector(-1, 1),
                Vector(-2, 2),
                Vector(-3, 3),
                Vector(-4, 4),
                Vector(-5, 5),
                Vector(-6, 6),
                Vector(-7, 7),
            ],

            [
                Vector(1, -1),
                Vector(2, -2),
                Vector(3, -3),
                Vector(4, -4),
                Vector(5, -5),
                Vector(6, -6),
                Vector(7, -7),
            ],

            [
                Vector(-1, -1),
                Vector(-2, -2),
                Vector(-3, -3),
                Vector(-4, -4),
                Vector(-5, -5),
                Vector(-6, -6),
                Vector(-7, -7),
            ],

            [
                Vector(-1, 0),
                Vector(-2, 0),
                Vector(-3, 0),
                Vector(-4, 0),
                Vector(-5, 0),
                Vector(-6, 0),
                Vector(-7, 0),
            ],

            [
                Vector(1, 0),
                Vector(2, 0),
                Vector(3, 0),
                Vector(4, 0),
                Vector(5, 0),
                Vector(6, 0),
                Vector(7, 0),
            ],

            [
                Vector(0, -1),
                Vector(0, -2),
                Vector(0, -3),
                Vector(0, -4),
                Vector(0, -5),
                Vector(0, -6),
                Vector(0, -7),
            ],

            [
                Vector(0, 1),
                Vector(0, 2),
                Vector(0, 3),
                Vector(0, 4),
                Vector(0, 5),
                Vector(0, 6),
                Vector(0, 7),
            ]
        ]

        super().__init__(index, "Qu", side, position, moves, moves)


class King(Piece):
    """
    A class representing the King piece
    """
    def __init__(self, index, side, position):
        """
        __init__

        :param index: A unique identifier for this individual piece.
        :param side: The side this piece is on.
        :param position: The starting position of this piece.
        """
        moves = [
            [Vector(-1, 1)],
            [Vector(0, 1)],
            [Vector(1, 1)],
            [Vector(1, 0)],
            [Vector(1, -1)],
            [Vector(0, -1)],
            [Vector(-1, -1)],
            [Vector(-1, 0)]
        ]

        super().__init__(index, "Ki", side, position, moves, moves)

    def get_legal_check_attacks(self, engine):
        """
        The King has different conditions for being able to attack under check.

        :param engine: The ChessEngine managing the game.
        :return: A list of possible attacks for this piece
        """
        attacks = []

        for threat in engine.threats:
            for attack in self.get_legal_attacks(False, engine):
                if threat.position == attack and not attack.is_out_of_bounds():
                    threats = engine.get_threats(self.index, attack)

                    empty_pass = False
                    while not empty_pass:
                        empty_pass = True
                        for x in range(0, len(threats)):
                            if threats[x].side == self.side:
                                del threats[x]
                                empty_pass = False
                                break

                    if len(threats) == 0:
                        attacks.append(attack)

        return attacks


class TurnCounter:
    """
    A class to keep track of which player's turn it is
    """
    def __init__(self):
        self.turn = 0

    def toggle(self):
        """
        Toggle the current player
        """
        if self.turn == 0:
            self.turn = 1

        else:
            self.turn = 0


class FrontEnd:
    """
    The FrontEnd class is used to create an interface between the player and the ChessEngine.
    """
    def render(self, pieces):
        """
        Render the chess board, by default this is text based.

        :param pieces: A list of pieces on the board.
        """
        board = []
        for y in range(0, 8):
            board.append([])

            for x in range(0, 8):
                found = False
                for piece in pieces:
                    if piece.position == Vector(x, y):
                        board[y].append(str(piece))
                        found = True
                        break

                if not found:
                    board[y].append("  ")

        print("  0  1  2  3  4  5  6  7")
        for y in range(0, len(board)):
            string = f"{y}|"

            for x in range(0, len(board[y])):
                string += board[y][x] + "|"

            print(string)


class ChessEngine:
    """
    The ChessEngine class manages the Chess game itself.
    """
    def __init__(self):
        """
        __init__
        """
        self.pieces = [
            Pawn(0, 0, Vector(0, 1)),
            Pawn(1, 0, Vector(1, 1)),
            Pawn(2, 0, Vector(2, 1)),
            Pawn(3, 0, Vector(3, 1)),
            Pawn(4, 0, Vector(4, 1)),
            Pawn(5, 0, Vector(5, 1)),
            Pawn(6, 0, Vector(6, 1)),
            Pawn(7, 0, Vector(7, 1)),
            Rook(8, 0, Vector(0, 0)),
            Rook(9, 0, Vector(7, 0)),
            Knight(10, 0, Vector(1, 0)),
            Knight(11, 0, Vector(6, 0)),
            Bishop(12, 0, Vector(2, 0)),
            Bishop(13, 0, Vector(5, 0)),
            Queen(14, 0, Vector(3, 0)),
            King(15, 0, Vector(4, 0)),

            Pawn(16, 1, Vector(0, 6)),
            Pawn(17, 1, Vector(1, 6)),
            Pawn(18, 1, Vector(2, 6)),
            Pawn(19, 1, Vector(3, 6)),
            Pawn(20, 1, Vector(4, 6)),
            Pawn(21, 1, Vector(5, 6)),
            Pawn(22, 1, Vector(6, 6)),
            Pawn(23, 1, Vector(7, 6)),
            Rook(24, 1, Vector(0, 7)),
            Rook(25, 1, Vector(7, 7)),
            Knight(26, 1, Vector(1, 7)),
            Knight(27, 1, Vector(6, 7)),
            Bishop(28, 1, Vector(2, 7)),
            Bishop(29, 1, Vector(5, 7)),
            Queen(30, 1, Vector(3, 7)),
            King(31, 1, Vector(4, 7)),
        ]
        self.turn_counter = TurnCounter()
        self.in_check = False
        self.checkmate = False
        self.threats = []  # Threats to the king

    def get_piece_by_position(self, position):
        """
        Try to find a piece at a given location.

        :param position: The location to search for a piece at.
        :return: The piece that was found, or None if none were found.
        """
        position = Vector(position[0], position[1])
        selected_piece = None

        for piece in self.pieces:
            if piece.position == position:
                selected_piece = piece
                break

        return selected_piece

    def get_legal_moves(self, position):
        """
        Get all the legal moves for the given piece.

        :param position: list/Vector/Piece, for any of the given types, this will be used to determine the selected
        piece, the process of determining the selected piece is as follows: list -> Vector -> Piece, this can start from
        any point in that process.
        :return: Two lists, one of possible moves, and one of possible attacks.
        """
        if isinstance(position, list):
            position = Vector(position[0], position[1])

        if not isinstance(position, Piece):
            selected_piece = self.get_piece_by_position(position)

        else:
            selected_piece = position

        if selected_piece is None:
            raise NoSuchPieceException()

        moves = None
        attacks = None

        if not self.in_check:
            moves = selected_piece.get_legal_moves(self.pieces, self)
            attacks = selected_piece.get_legal_attacks(False, self)

        else:
            moves = selected_piece.get_legal_check_moves(self.pieces, self)
            attacks = selected_piece.get_legal_check_attacks(self)

        return moves, attacks

    def get_threats(self, index, position):
        """
        Get all the given threats to a location, excluding the piece identified with index.

        :param index: The index of the piece to ignore.
        :param position: The position to check.
        :return: A list of pieces threatening the given location.
        """
        threats = []
        for piece in self.pieces:
            if piece.index == index:
                continue

            if position in piece.get_legal_attacks(True, self):
                threats.append(piece)

        return threats

    def check_for_check(self):
        """
        Check if the king is in check.
        """
        king = None
        for piece in self.pieces:
            if piece.name == "Ki" and piece.side == self.turn_counter.turn:
                king = piece
                break

        if king is None:
            raise NoSuchPieceException()

        threats = self.get_threats(king.index, king.position)
        empty_pass = False
        while not empty_pass:
            empty_pass = True
            for x in range(0, len(threats)):
                if threats[x].side == king.side:
                    del threats[x]
                    empty_pass = False
                    break

        if len(threats) != 0:
            self.in_check = True
            self.threats = threats

        else:
            self.in_check = False
            self.threats = []

    def check_for_checkmate(self):
        """
        Check if the king is in checkmate.
        """
        number_of_moves = 0
        for piece in self.pieces:
            if piece.side == self.turn_counter.turn:
                moves, attacks = self.get_legal_moves(piece)
                number_of_moves += (len(moves) + len(attacks))

        self.checkmate = number_of_moves == 0

    def move_piece(self, selection, new_position):
        """
        Try to move the selected piece to the given position.

        :param selection: The coordinate of the selected piece (list).
        :param new_position: The position to try and move the piece to (list).
        :return: Whether or not this move was successful, and an error message, if applicable.
        """
        position = Vector(selection[0], selection[1])
        selected_piece = self.get_piece_by_position(position)

        if selected_piece is None:
            raise NoSuchPieceException()

        if selected_piece.side != self.turn_counter.turn:
            return False, "That's not your piece!"

        if not isinstance(new_position, Vector):
            new_position = Vector(new_position[0], new_position[1])

        result = selected_piece.move(new_position, self.pieces, self)

        if not result:
            attacked_piece = self.get_piece_by_position(new_position)

            if attacked_piece is None:
                return result, None

            else:
                result = selected_piece.attack(new_position, attacked_piece, self)
                if result:
                    for x in range(0, len(self.pieces)):
                        if self.pieces[x].index == attacked_piece.index:
                            del self.pieces[x]
                            break

        for x in range(0, len(self.pieces)):
            if isinstance(self.pieces[x], Pawn):
                if self.pieces[x].should_promote():
                    self.pieces[x] = Queen(self.pieces[x].index, self.pieces[x].side, self.pieces[x].position)

        if result:
            self.turn_counter.toggle()

        self.check_for_check()
        if self.in_check:
            self.check_for_checkmate()

        return result, "Invalid move!"
