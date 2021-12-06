class Coordinate():
    def __init__(self, x_index, y_index):
        self.x = x_index
        self.y = y_index
    
    def __eq__(self, other):
        if self is None or other is None:
            return False
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return "Coordinate("+str(self.x)+", "+str(self.y)+")"
    
    def toTuple(self):
        return (self.x,self.y)

    def invert(self):
        self.x = 7 - self.x
        self.y = 7 - self.y

    def negate(self):
        self.x *= -1
        self.y *= -1
    
    def _asAN(self, isWhitePerspective = True) -> str:
        if not isWhitePerspective:
            self.invert()
        letter = self.numToLetter(self.y)
        number = 8 - self.x
        # Needs to reinvert if it had
        if not isWhitePerspective:
            self.invert()
        return letter + str(number)

    @staticmethod
    def toLAN(fromCoordinate, toCoordinate, isWhitePerspective = True) -> str:
        return fromCoordinate._asAN(isWhitePerspective) + toCoordinate._asAN(isWhitePerspective)

    @staticmethod
    def stringToCoordinate(string):
        letter = string[0]
        num = int(string[1])
        y = Coordinate.letterToNum(letter)
        x = 8 - num
        return Coordinate(x,y)

    @staticmethod
    def numToLetter(num):
        """ Converts a number from 0-7 to a letter, A-H """
        return chr(num+97)

    @staticmethod
    def letterToNum(chr):
        """ Converts a letter, A-H, to a number from 0-7 """
        return ord(chr) - 97

    @staticmethod
    def getDifference(firstCoordinate, secondCoordinate):
        return Coordinate(firstCoordinate.x-secondCoordinate.x, 
                          firstCoordinate.y-secondCoordinate.y)