from tkinter import *
from Coordinate import Coordinate
from CanvasUtility import *
from Cell import Cell
from FileManager import *

class Chessboard(Canvas):

    BOARD_LEN = 8
    BOX_LEN = 95
    BROWN = '#B58863'
    LIGHT_BROWN = '#F0D9B5'
    SHORT_DISTANCE = 3 / 38 * BOX_LEN
    LONG_DISTANCE = BOX_LEN * 0.34
    ARROW_BASE_DISTANCE = BOX_LEN / 2.5
    CIRCLE_OUTLINE_LENGTH = 7.5

    def __init__(self, base):
        super(Chessboard, self).__init__(base, width=760, height=760,
                bg='White', highlightthickness=0)
        self.drawBoard()
        self.__board = [[Cell() for j in range(self.BOARD_LEN)
                        ] for i in range(self.BOARD_LEN)]

    def textUpdate(self, pieceText, coordinate):
        currentCell = self.__board[coordinate.x][coordinate.y]
        currentCell.text = pieceText
        currentCell.image = self.getPieceFromText(pieceText)
        currentCell.record = super().create_image(
                            getCanvasX(coordinate), 
                            getCanvasY(coordinate), 
                            image = currentCell.image, 
                            anchor = NW
                        )

    def getTextBoard(self):
        textBoard = []
        for row in range(self.BOARD_LEN):
            textBoard.append([])
            for col in range(self.BOARD_LEN):
                textBoard[row].append(self.__board[row][col].text)
        return textBoard

    def getCell(self, coordinate):
        return self.__board[coordinate.x][coordinate.y]

    def drawBoard(self):
        # Used to aternate colors
        lightBrownFlag = True

        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                coordinatePair = Coordinate(row,col)
                super().create_rectangle(
                    getCanvasX(coordinatePair),
                    getCanvasY(coordinatePair),
                    getNextCanvasX(coordinatePair),
                    getNextCanvasY(coordinatePair),
                    fill=(self.LIGHT_BROWN if lightBrownFlag else self.BROWN),
                    width=0,
                    )

                # Color shifts on every column
                lightBrownFlag = not lightBrownFlag

            # Color shifts on every row
            lightBrownFlag = not lightBrownFlag

    # God this was a mess and an awful thing to try and figure out
    def drawArrow(self, point1, point2, color = "#6D9F58"):
        """ Draws an arrow on the canvas, taking two coordinates as input """

        deltaX = point2.x - point1.x
        deltaY = point2.y - point1.y
        hypotnuse = (deltaX ** 2 + deltaY ** 2) ** 0.5
        cosineVal = deltaX / hypotnuse
        sineVal = deltaY / hypotnuse

        arrowBase = Coordinate(point2.x - cosineVal
                     * self.ARROW_BASE_DISTANCE, point2.y
                     - sineVal * self.ARROW_BASE_DISTANCE)
        points = [
            point1.x - self.SHORT_DISTANCE * sineVal,
            point1.y + self.SHORT_DISTANCE * cosineVal,
            arrowBase.x - self.SHORT_DISTANCE * sineVal,
            arrowBase.y + self.SHORT_DISTANCE * cosineVal,
            arrowBase.x - self.LONG_DISTANCE * sineVal,
            arrowBase.y + self.LONG_DISTANCE * cosineVal,
            point2.x,
            point2.y,
            arrowBase.x + self.LONG_DISTANCE * sineVal,
            arrowBase.y - self.LONG_DISTANCE * cosineVal,
            arrowBase.x + self.SHORT_DISTANCE * sineVal,
            arrowBase.y - self.SHORT_DISTANCE * cosineVal,
            point1.x + self.SHORT_DISTANCE * sineVal,
            point1.y - self.SHORT_DISTANCE * cosineVal,
            ]

        return super().create_polygon(points, fill = color,
                stipple="gray75")

    def drawCircleHighlight(self, point, customWidth=7.5):
        return super().create_oval(
            point.x - 0.5 * self.BOX_LEN + customWidth / 2,
            point.y - 0.5 * self.BOX_LEN + customWidth / 2,
            point.x + 0.5 * self.BOX_LEN - customWidth / 2,
            point.y + 0.5 * self.BOX_LEN - customWidth / 2,
            outline='#6D9F58',
            width=customWidth,
            )
    
    def resetBoard(self):
        self.__board = [[Cell() for j in range(self.BOARD_LEN)
                        ] for i in range(self.BOARD_LEN)]


    # Photoimages can only be created AFTER declaring a tkinter object
    @staticmethod
    def getPieceFromText(pieceText):
        """ Maps the piece character to the piece's image """
        PIECE_IMAGE_MAP = {
            'p' : PhotoImage(file = getFile('cpieces/bpawn.png')),
            'r' : PhotoImage(file = getFile('cpieces/brook.png')),
            'b' : PhotoImage(file = getFile('cpieces/bbishop.png')),
            'n' : PhotoImage(file = getFile('cpieces/bknight.png')),
            'k' : PhotoImage(file = getFile('cpieces/bking.png')),
            'q' : PhotoImage(file = getFile('cpieces/bqueen.png')),

            'P' : PhotoImage(file = getFile('cpieces/wpawn.png')),
            'R' : PhotoImage(file = getFile('cpieces/wrook.png')),
            'B' : PhotoImage(file = getFile('cpieces/wbishop.png')),
            'N' : PhotoImage(file = getFile('cpieces/wknight.png')),
            'K' : PhotoImage(file = getFile('cpieces/wking.png')),
            'Q' : PhotoImage(file = getFile('cpieces/wqueen.png')),

            '-' : None
        }
        return PIECE_IMAGE_MAP[pieceText]
        # CREDITS TO max OF Stackoverflow