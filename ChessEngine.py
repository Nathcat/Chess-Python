"""
ChessEngine.py

A Chess engine program written in Python.

Author: Nathan "Nathcat" Baines
"""
import os
import platform


class NoSuchPieceException(BaseException):
    def __str__(self):
        return "The selected piece does not exist"


class Vector:  # A Vector class to represent positions/movements
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __mul__(self, a):
        return Vector(self.x * a, self.y * a)

    def __add__(self, a):
        return Vector(self.x + a.x, self.y + a.y)

    def __truediv__(self, a):
        return Vector(self.x / a, self.y / a)

    def __sub__(self, a):
        return Vector(self.x - a.x, self.y - a.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, a):
        return self.x == a.x and self.y == a.y

    def __getitem__(self, index):
        if index == 0:
            return self.x

        elif index == 1:
            return self.y

        else:
            raise IndexError()

    def is_out_of_bounds(self):
        return self.x >= 8 or self.x <= -1 or self.y >= 8 or self.y <= -1


class Piece:  # Piece parent class
    def __init__(self, index, name, side, position, moves, attacks):
        self.name = name
        self.side = side
        self.position = position
        self.moves = moves
        self.attacks = attacks
        self.index = index

    def move(self, position, pieces, engine):
        if not engine.in_check:
            legal_moves = self.get_legal_moves(pieces)
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

    def attack(self, position, attacked_piece, pieces, engine):
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

    def get_legal_moves(self, pieces):
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

                if valid:
                    legal_moves.append(self.position + move)

                else:
                    break

        return legal_moves

    def get_legal_check_moves(self, pieces, engine):
        moves = []

        for move in self.get_legal_moves(pieces):
            old_position = Vector(self.position.x, self.position.y)
            self.position = move
            engine.check_for_check()
            self.position = old_position

            if not engine.in_check:
                moves.append(move)

            engine.check_for_check()

        return moves

    def get_legal_attacks(self, friendly_fire, engine):
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
        attacks = []

        for threat in engine.threats:
            for attack in self.get_legal_attacks(False, engine):
                if threat.position == attack and not attack.is_out_of_bounds():
                    attacks.append(attack)

        return attacks

    def __str__(self):
        colour = ""
        if self.side == 0:
            colour = "\u001b[30m"

        else:
            colour = "\u001b[37m"

        return f"{colour}{self.name}\u001b[0m"


class Pawn(Piece):  # Pawn subclass
    def __init__(self, index, side, position):
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
        direction = 1
        if self.side == 1:
            direction = -1

        result = super().move(position, pieces, engine)

        if result:
            self.moves = [[Vector(0, 1 * direction)]]

        return result


class Rook(Piece):
    def __init__(self, index, side, position):
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
    def __init__(self, index, side, position):
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
    def __init__(self, index, side, position):
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
    def __init__(self, index, side, position):
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
    def __init__(self, index, side, position):
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
    def __init__(self):
        self.turn = 0

    def toggle(self):
        if self.turn == 0:
            self.turn = 1

        else:
            self.turn = 0


class FrontEnd:
    def render(self, pieces):
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
    def __init__(self):
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
        self.threats = []

    def get_piece_by_position(self, position):
        position = Vector(position[0], position[1])
        selected_piece = None

        for piece in self.pieces:
            if piece.position == position:
                selected_piece = piece
                break

        return selected_piece

    def get_legal_moves(self, position):
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
            moves = selected_piece.get_legal_moves(self.pieces)
            attacks = selected_piece.get_legal_attacks(False, self)

        else:
            moves = selected_piece.get_legal_check_moves(self.pieces, self)
            attacks = selected_piece.get_legal_check_attacks(self)

        return moves, attacks

    def get_threats(self, index, position):
        threats = []
        for piece in self.pieces:
            if piece.index == index:
                continue

            if position in piece.get_legal_attacks(True, self):
                threats.append(piece)

        return threats

    def check_for_check(self):
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
        number_of_moves = 0
        for piece in self.pieces:
            if piece.side == self.turn_counter.turn:
                moves, attacks = self.get_legal_moves(piece)
                number_of_moves += (len(moves) + len(attacks))

        self.checkmate = number_of_moves == 0

    def move_piece(self, selection, new_position):
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
                result = selected_piece.attack(new_position, attacked_piece, self.pieces, self)
                if result:
                    for x in range(0, len(self.pieces)):
                        if self.pieces[x].index == attacked_piece.index:
                            del self.pieces[x]
                            break

        if result:
            self.turn_counter.toggle()

        self.check_for_check()
        if self.in_check:
            self.check_for_checkmate()

        return result, "Invalid move!"
