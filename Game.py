import copy
from Chessboard import Chessboard
from tkinter import *
from Coordinate import Coordinate
from CanvasUtility import *
from Cell import Cell
from Player import *
import chess
from Kibitzer import *

from FileManager import *

from json.decoder import JSONDecodeError
import chess

class Game:
    BROWN = '#B58863'
    LIGHT_BROWN = '#F0D9B5'
    BOX_LEN = 95
    BOARD_LEN = 8
    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, base, FENCode, asWhite=True):
        """ Inits the Chessboard object from a Tkinter Base """

        # Tkinter object initailizers
        self.__base = base

        self.__boardFrame = Frame(base)
        self.__boardFrame.grid(row=0, column=0, rowspan=1, columnspan=1)
        self.__board = Chessboard(self.__boardFrame)
        self.__board.grid(row = 0, column = 0)
        self.__boardLogic = chess.Board()

        self.__promotionText = ''
        self.__promotionImages = []
        self.__promotionButtons = []

        # self.__positionToEnPassant = None

        # Bindings
        self.__base.bind('<B1-Motion>', self.__move)
        self.__base.bind('<Button-1>', self.__selectPiece)
        self.__base.bind('<ButtonRelease-1>', self.__deselectPiece)
        self.__base.bind('<Button-3>', self.__rightClickEvent)
        self.__base.bind('<ButtonRelease-3>', self.__finishShape)
        # self.__base.bind('<Right>', self.__advancePGN)
        # self.__base.bind('<Left>', self.__backtrackPGN)
        # self.__base.bind('<space>', self.__printFEN)
        # self.__base.bind('<Up>', self.__printPGN)
        # self.__base.bind('<Return>', self.__inputGo)

        # Tracker for when pieces are moved
        self.__activeCell = Cell()
        
        self.__isPlayerWhite = asWhite

        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = ()

        self.__readFEN(FENCode, asWhite)

        # self.__opponentPlayer = VariationPlayer(            
        #     {"e4" : {"c6": {"Nf3" : {"d5" : {"Nc3" : {"dxe4" : {"Nxe4" : {"Bf5" : {"Ng3" : {"Bg6" : {"h4" : {"h6" : {"Ne5" : {"Bh7" : {"Qh5" : {"g6" : {"Bc4" : {"e6" : {"Qe2" : {"Bg7" : {"Nxf7" : {"Kxf7" : {"Qxe6+" : {"Kf8" : {"Qf7#" : None}}}}}}}}}}}}}}}}}}}}}}}}}
        # )
        self.__opponentPlayer = LichessPlayer(startingFEN = FENCode)
        self.__kibitzer = ChessDBCNKibitzer()

    def __readFEN(self, FENCode, asWhite):
        """ Takes in a FENCode and initializes the board """
        self.__boardLogic.set_fen(FENCode)

        boardInfo = FENCode.split(" ")

        # Splits the FENCode into relevant information
        boardCode = boardInfo[0]

        # When the player at the bottom part of the board is black,
        # the position is simply miorred rather than changing indexing.
        # Consequently, when printing out the FEN, this must be reversed
        if not asWhite:
            boardCode = boardCode[::-1]
        self.__isPlayerWhite = asWhite

        cleanedCode = ""
        numberList = ("1", "2", "3", "4", "5", "6", "7", "8")

        # Converts numbers into dashes
        for index in range(len(boardCode)):
            if boardCode[index] in numberList:
                for repeats in range(int(boardCode[index])):
                    cleanedCode += "-"
            else:
                cleanedCode += boardCode[index]

        textBoard = [list(row) for row in cleanedCode.split("/")]
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                self.__board.textUpdate(textBoard[row][col], 
                                        Coordinate(row, col))


    def __move(self, event):
        """ Updates the piece to the mouse's position """
        # Makes sure that a piece has been selected
        if not self.__activeCell.isEmpty():

            # Centers the piece on the mouse's center
            self.__board.moveto(
                self.__activeCell.record, 
                event.x-int(self.BOX_LEN/2), 
                event.y-int(self.BOX_LEN/2)
                )
            
            # Moves the moving piece in front of all other drawn pieces
            self.__board.tag_raise(self.__activeCell.record)

    def __selectPiece(self, event):
        """ Determines the piece pressed, and marks the original position """
      #   # Blocks moves after game completion
      #   if not self.__isGameActive:
      #       return

        # Blocks selections outside of the game board
        if event.x >= 760 or event.y >= 760:
            return

        # Resets the arrows/highlighted boxes
        self.__resetShapes()

        # Records the old position
        self.__originalPos = getBoardCoordinate(event)

        # Remembers the current cell that will be manipulated
        self.__activeCell = \
            copy.copy(self.__board.getCell(self.__originalPos))

    def __deselectPiece(self, event):
        """ Puts down the piece and marks its completion """

        # Block any drops outside
        if event.x >= 760 or event.y >= 760:
            self.__rightClickEvent(None)

        # Gets the box that the mouse is in
        clickLoc = getBoardCoordinate(event)

        # Checks if an actual piece is being pressed
        if not self.__activeCell.isEmpty() and not clickLoc == self.__originalPos:

            # Promotion: Need to add an extra bit to get the user to choose their promotion piece
            if clickLoc.x in [0, 7] and self.__activeCell.text.upper() == 'P':
               originalLocation = self.__originalPos
               initialCell = self.__activeCell
               self.__displayPromotion(clickLoc.y)
               while len(self.__promotionText) == 0:
                  for button in self.__promotionButtons:
                        button.update()

               self.__board.delete(self.__testWindow)

               # Needs to reassign because of mixing between canvas and
               # buttons
               self.__originalPos = originalLocation
               self.__activeCell = initialCell

            # converts the coordinates to LAN
            attemptedMoveAN = \
                Coordinate.toLAN(self.__originalPos, clickLoc, self.__isPlayerWhite) \
                + self.__promotionText.lower()

            attemptedMove = chess.Move.from_uci(attemptedMoveAN)

            allMoves = self.__boardLogic.legal_moves

            if (attemptedMove in allMoves):
                self.__endMove(clickLoc)

                moveSAN = self.__boardLogic.san(chess.Move.from_uci(attemptedMoveAN))
                self.__boardLogic.push_uci(attemptedMoveAN)

                self.__board.update_idletasks()
                # self.__opponentPlayer = LichessPlayer()
                # self.pushMove(self.__opponentPlayer.getMove(self.__boardLogic.fen()))
                
                # self.pushMove(self.__opponentPlayer.getMove(moveSAN))
                self.pushMove(self.__opponentPlayer.getMove(attemptedMoveAN))

                ktext = self.__kibitzer.getMoves(self.__boardLogic.fen())

                # for move in list(ktext.keys()):
                moveTexts = list(ktext.keys())
                i = 5
                while(len(moveTexts) > 0 and i != 0):
                    move = moveTexts.pop(0)
                    evalText = ktext[move]['score']
                    evalText = f'{int(evalText)/100:+1.2f}'
                    print(self.__LANtoSAN(move) + " " + str(evalText) )
                    i -= 1
                print("--------------")


                return

        self.__rightClickEvent(None)
    

    def pushMove(self, text):
        # Rough SAN detection
        if self.__isLAN(text):
            lan = text
        else:
            lan = self.__SANtoLAN(text)

        self.__originalPos = Coordinate.stringToCoordinate(lan[0:2])
        endPos = Coordinate.stringToCoordinate(lan[2:4])
        self.__promotionText = "" if len(lan) == 4 else (lan[4].upper() if self.__boardLogic.turn else lan[4].lower())
        self.__activeCell = copy.copy(self.__board.getCell(self.__originalPos))

        self.__endMove(endPos)

        self.__boardLogic.push_san(text)

    def __isLAN(self, text):
        if text[0].isupper():
            return False
        if not len(text) in [4,5]:
            return False
        if "+" in text or "#" in text or "=" in text:
            return False
        return True

    # SAN -> LAN
    def __SANtoLAN(self, moveText):
        return self.__boardLogic.parse_san(moveText).uci()

    def __LANtoSAN(self, moveText):
        return self.__boardLogic.san(chess.Move.from_uci(moveText))

    def __endMove(self, finalPos):
        isWhite = self.__boardLogic.turn
        # Centers the object onto the square it landed on
        self.__board.moveto(
            self.__activeCell.record,
            getCanvasX(finalPos),
            getCanvasY(finalPos))

        delta = Coordinate.getDifference(self.__originalPos, finalPos)

        # Special Case: When en passant occurs, the pawn captured needs
        #               to be manually found and removed.
        if self.__activeCell.text.upper() == 'P' and abs(delta.y) == 1 and self.__board.getCell(finalPos).isEmpty():
            pawn_x_index = finalPos.x + (-1 if isWhite ^ 
                                         self.__isPlayerWhite else 1)
            
            self.__board.delete(self.__board.getCell(Coordinate(
                finalPos.x+ (1 if isWhite else -1),finalPos.y)))
            self.__board.textUpdate("-" , Coordinate(pawn_x_index,finalPos.y))

        # Special case: Castling
        # Manually assigns King displacement, as startPos != endPos when
        # castling sometimes (e.x. e1g1 e1h1 both work for O-O)
        if self.__activeCell.text.upper() == "K" and abs(delta.y) > 1:
            homeRowX = finalPos.x
            y_change = int(2 * abs(delta.y)/delta.y) * -1
            kingAdjustment = y_change
            
            # Need to find the rook's y location, default to 0
            rookY = 0
            if abs(7 - finalPos.y) <= 2: # close to the other side
                rookY = 7
            kingY = self.__originalPos.y

            oldKingCoordinate = self.__originalPos
            newKingCoordinate = Coordinate(homeRowX, kingY + kingAdjustment)
            
            # Because the rook can travel 2 or 3 spaces depending on
            # castle location, point of reference is the original king 
            # location, where 1 unit is the rook and 2 is the king.
            oldRookCoordinate = Coordinate(homeRowX, rookY)
            newRookCoordinate = Coordinate(homeRowX, kingY + kingAdjustment//2)

            # Moves the rook
            self.__board.moveto(
                self.__board.getCell(oldRookCoordinate).record,
                getCanvasX(newRookCoordinate),
                getCanvasY(newRookCoordinate),
            )

            self.__board.textUpdate(self.__board.getCell(oldRookCoordinate).text, newRookCoordinate)
            self.__board.textUpdate("-", oldRookCoordinate)

            # Moves the king
            self.__board.moveto(
                self.__board.getCell(oldKingCoordinate).record,
                getCanvasX(newKingCoordinate),
                getCanvasY(newKingCoordinate),
            )

            self.__board.textUpdate(self.__board.getCell(oldKingCoordinate).text, newKingCoordinate)
            self.__board.textUpdate("-", oldKingCoordinate)
        
        # non-castling cases
        else:
            # Removes old piece images on capture
            self.__board.delete(self.__board.getCell(finalPos).record)

            # Records the new position
            self.__board.textUpdate(self.__activeCell.text, finalPos)

            # Special case: Promotion
            if len(self.__promotionText) != 0:
                # Update promotion square
                self.__board.textUpdate(self.__promotionText, finalPos)

                # Clears all promotion variables
                self.__promotionText = ""
                self.__promotionButtons = []
                self.__promotionImages = []

            # Remove the old position of the piece
            self.__board.textUpdate("-", self.__originalPos)

        # Forget the active piece
        self.__activeCell = Cell()

    def __rightClickEvent(self, event):
        """ Restores the board prior to clicking anything """
        if not self.__activeCell.isEmpty():

            # Centers the piece back to its original position
            self.__board.moveto(
                self.__board.getCell(self.__originalPos).record,
                getCanvasX(self.__originalPos), 
                getCanvasY(self.__originalPos))

            # Forget the active piece
            self.__activeCell = Cell()
        elif event is not None:
            self.__beginShapeDrawing(event)

    def __resetShapes(self):
        for arrow in list(self.__activeArrows.values()):
            self.__board.delete(arrow)
        for circle in list(self.__activeCircles.values()):
            self.__board.delete(circle)
        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = None

    def __beginShapeDrawing(self, event):
        """ Records the inital coordinate that was right-clicked """
        x = event.x
        y = event.y

        self.__originalArrowCoordinate = Coordinate(
            (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
            (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
        )
        
    def __finishShape(self, event):
        """ Completes the shape if possible, erases any duplicates """
        # This blocks if you right click and then left click
        if self.__originalArrowCoordinate is not None:
            x = event.x
            y = event.y    

            final = Coordinate(
                (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
                (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
            )

            # Checks if the original and final square is the same
            if final.x == self.__originalArrowCoordinate.x and \
               final.y == self.__originalArrowCoordinate.y:
                # Checks and removes a duplicate circle
                if final.toTuple() in list(self.__activeCircles.keys()):
                    self.__board.delete(self.__activeCircles[final.toTuple()])
                    del self.__activeCircles[final.toTuple()]
                # Draws the circle, indexing the selected box
                else:
                    self.__activeCircles[final.toTuple()] = \
                        self.__board.drawCircleHighlight(final)
            # Arrow
            else:
                # Checks and removes a duplicate arrow
                if (self.__originalArrowCoordinate.toTuple(), final.toTuple())\
                                           in list(self.__activeArrows.keys()):
                    self.__board.delete(
                        self.__activeArrows[(
                            self.__originalArrowCoordinate.toTuple(), 
                            final.toTuple()
                            )]
                        )
                    del self.__activeArrows[
                        (self.__originalArrowCoordinate.toTuple(),
                         final.toTuple())]
                # Draws the arrow, indexing the original and final box
                else:
                    self.__activeArrows[
                        (self.__originalArrowCoordinate.toTuple(), 
                            final.toTuple())] = \
                         self.__board.drawArrow(self.__originalArrowCoordinate, 
                                                final)

            self.__originalArrowCoordinate = ()

    def __resetShapes(self):
        for arrow in list(self.__activeArrows.values()):
            self.__board.delete(arrow)
        for circle in list(self.__activeCircles.values()):
            self.__board.delete(circle)
        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = None

    def __displayPromotion(self, y_index):
        x_pixel = 0
        y_pixel = 0

        def makePromotionTextFunction(text):
            def promotionText():
                self.__promotionText = text
            return promotionText

        self.__frame = Frame(self.__base)

        # Top of the board, white
        isWhite = self.__boardLogic.turn
        promotionList = ['Q','N','R','B'] if isWhite else ['q','n','r','b']

        # Bottom screen
        if isWhite ^ self.__isPlayerWhite:
            promotionList.reverse()
            y_pixel = 4 * self.BOX_LEN
        x_pixel = self.BOX_LEN * y_index
        for i in range(4):
            self.__promotionImages.append(
                Chessboard.getPieceFromText(promotionList[i]))
            self.__promotionButtons.append(
                Button(self.__frame, bg = "White", borderwidth = 0,
                       highlightthickness=0,image = self.__promotionImages[i],
                       command = makePromotionTextFunction(promotionList[i])
                )
            )
            self.__promotionButtons[i].pack()
        self.__testWindow = self.__board.create_window(
            x_pixel,
            y_pixel,
            anchor = NW, 
            window = self.__frame
        )
        self.__board.update_idletasks()

    @staticmethod
    def numToLetter(num):
        """ Converts a number from 0-7 to a letter, A-H """
        return chr(num+97)

    @staticmethod
    def letterToNum(chr):
        """ Converts a letter, A-H, to a number from 0-7 """
        return ord(chr) - 97

base = Tk()

base.title("Chess")

# board = Game(base, Game.DEFAULT_FEN, True)
# board = Game(base, "r1b1kbnr/pppp1ppp/2n5/3NP3/5q2/5N2/PPP1PPPP/R2QKB1R b KQkq - 1 6", True)
board = Game(base, "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", True)

base.mainloop()