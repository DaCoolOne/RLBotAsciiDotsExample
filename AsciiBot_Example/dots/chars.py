import math

class Char(str):
    def __init__(self, value):
        self.value = value

    def isDot(self):
        return False

    def isOper(self):
        return False

    def isCurlyOper(self):
        return False

    def isSquareOper(self):
        return False

    def isWarp(self):
        return False

    def isLibWarp(self):
        return False

    def isSingletonLibWarp(self):
        return False

    def isSingletonLibReturnWarp(self):
        return False


class DotChar(Char):
    def isDot(self):
        return True


class OperChar(Char):
    def __init__(self, value):
        super().__init__(value)

        self.func = None

    def isOper(self):
        return True

    def calc(self, x, y):
        if self.func is None:
            print(x, y)
            function_dict = {
                '+': (lambda x, y: x + y),
                '-': (lambda x, y: x - y),
                '*': (lambda x, y: x * y),
                '/': (lambda x, y: x / y),
                '^': (lambda x, y: x ** y),
                '%': (lambda x, y: x % y),

                'o': (lambda x, y: x | y),
                'x': (lambda x, y: x ^ y),
                '&': (lambda x, y: x & y),
                '!': (lambda x, y: x != y),

                '=': (lambda x, y: x == y),
                '>': (lambda x, y: x > y),
                'G': (lambda x, y: x >= y),
                '<': (lambda x, y: x < y),
                'L': (lambda x, y: x <= y),

                's': (lambda x, y: math.sin(x / math.pi * 180) if y else math.sin(x)),
                'c': (lambda x, y: math.cos(x / math.pi * 180) if y else math.cos(x)),
                't': (lambda x, y: math.tan(x / math.pi * 180) if y else math.tan(x)),

                'S': (lambda x, y: math.asin(x) / math.pi * 180 if y else math.asin(x)),
                'C': (lambda x, y: math.acos(x) / math.pi * 180 if y else math.acos(x)),
                'T': (lambda x, y: math.atan(x) / math.pi * 180 if y else math.atan(x)),

                'x': (lambda x, y: math.atan2(x, y)),
                'X': (lambda x, y: math.atan2(x, y) / math.pi * 180),
                'a': (lambda x, y: x / math.pi * 180 if y else x / 180 * math.pi),
            }

            unicode_substitutions = {
                '÷': '/',
                '≠': '!',
                '≤': 'L',
                '≥': 'G'
            }

            if self in unicode_substitutions:
                raise RuntimeError('Unicode operator used. Operator "{}" should be replaced with "{}".'.format(self, unicode_substitutions[self]))

            self.func = function_dict[self]

        return self.func(x, y)


class CurlyOperChar(OperChar):
    def isCurlyOper(self):
        return True


class SquareOperChar(OperChar):
    def isSquareOper(self):
        return True


class WarpChar(Char):
    def __init__(self, value):
        super().__init__(value)

        self._teleporter_id = None
        self._dest_loc = None

    def isWarp(self):
        return True

    def set_id(self, teleporter_id):
        self._teleporter_id = teleporter_id

    def get_id(self):
        return self._teleporter_id

    def set_dest_loc(self, pos):
        self._dest_loc = pos

    def get_dest_loc(self):
        return self._dest_loc


class LibWarpChar(WarpChar):
    def isLibWarp(self):
        return True


class LibInnerWarpChar(LibWarpChar):
    def isLibWarp(self):
        return True

    def set_dest_loc(self, pos):
        raise Exception(
            "SingletonLibReturnWarpChar: cannot set destination; use the stack!")

    def get_dest_loc(self):
        raise Exception(
            "SingletonLibReturnWarpChar: unknown destination; use the stack!")


class LibOuterWarpChar(LibWarpChar):
    def isLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibWarpChar(LibWarpChar):
    def isSingletonLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibOuterWarpChar(SingletonLibWarpChar):
    pass


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibInnerWarpChar(LibInnerWarpChar, SingletonLibWarpChar):
    pass
