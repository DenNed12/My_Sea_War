from random import randint
# Классы исключений для отлова ошибок в ходе игры.
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаететсь селать выстрел вне координат доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return " Вы уже стреляли в эту клетку!"

class ShipException(BoardException):
    pass


# Класс точек доски.
class Dot:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x},{self.y})"


# Класс корабля
class Ship:
    def __init__(self, first_dot, length, orient):
        self.first_dot = first_dot
        self.length = length
        self.orient = orient
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cord_x = self.first_dot.x
            cord_y = self.first_dot.y

            if self.orient == 0:
                cord_x += i

            elif self.orient == 1:
                cord_y += i

            ship_dots.append(Dot(cord_x, cord_y))
        return ship_dots

    def ship_hit(self,shot):
        return shot in self.dots




class Board:
    def __init__(self, hid = True, size = 6):
        self.hid = hid
        self.size = size

        self.count = 0 # счетчик уничтоженных кораблей.
        self.field = [["0"] * size for i in range(size)]
        self.busy = [] # список занятых клеток
        self.ships = [] # список кораблей


    def __str__(self): # метод выводящий доску в консоль
        brd = ""
        brd += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row  in enumerate(self.field):
            brd += f"\n {i+1} " + " | ".join(row) + " | "

        if self.hid:
            brd = brd.replace("0", "-")
        return brd

    def out_of_range(self,d): # проверка попадания точки в координаты доски
            return not((0<= d.x < self.size) and (0<= d.y < self.size))


    def contour(self, ship, verb = False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in around:
                cord = Dot(d.x +dx,d.y + dy)
                if not(self.out_of_range(cord)) and cord not in self.busy:
                    if verb:
                        self.field[cord.x][cord.y] = "."
                    self.busy.append(cord)

    def add_ship(self,ship):
        for d in ship.dots:
            if self.out_of_range(d) or d in self.busy:
                raise ShipException
        for d in ship.dots:
            self.field[d.x][d.y] = "#"

        self.ships.append(ship)
        self.contour(ship)

    def shot(self,d):
        if self.out_of_range(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship,verb = True)

                    print("Корабрь уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print(" Не попал!")
        return False

    def start(self):
        self.count = 0
        self.busy = []




# Класс игрока
class Player:
    def __init__(self,board,enemy):
        self.board = board
        self.enemy = enemy
    def ask(self):
        raise NotImplementedError()
    def turn(self):
        while True:
            try:
                aim = self.ask()
                repeat = self.enemy.shot(aim)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        dot = Dot(randint(0,5),randint(0,5))
        print(f"Ход компьютера: {dot.x+1},{dot.y+1}")
        return dot

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue
            x,y = cords
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите цифры!")
                continue
            x, y = int(x), int(y)

            return Dot(x-1, y-1)

class Game:
    def __init__(self, size =6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co,pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1,1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0,self.size),randint(0,self.size)),l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except ShipException:
                    pass
        board.start()
        return board


    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
#
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.turn()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.turn()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()



g = Game()
g.start()