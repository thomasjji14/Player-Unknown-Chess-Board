from Chessboard import Chessboard
from tkinter import *
from Coordinate import Coordinate
from CanvasUtility import *
from Cell import Cell
from Player import *
from collections import deque
from Kibitzer import *
from FileManager import *
from Gametree import LinkedTree
import chess
import copy

class Game:
    BROWN = '#B58863'
    LIGHT_BROWN = '#F0D9B5'
    BOX_LEN = 95
    BOARD_LEN = 8
    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, base, FENCode, asWhite=True):
        """ Inits the Chessboard object from a Tkinter Base """

        # Tkinter object initailizers
        self._base = base

        self._boardFrame = Frame(base)
        self._boardFrame.grid(row=0, column=0, rowspan=1, columnspan=1)
        self._board = Chessboard(self._boardFrame)
        self._board.grid(row = 0, column = 0)
        self._boardLogic = chess.Board()

        self._promotionText = ''
        self._promotionImages = []
        self._promotionButtons = []

        # self._positionToEnPassant = None

        # Bindings
        self._base.bind('<B1-Motion>', self._move)
        self._base.bind('<Button-1>', self._selectPiece)
        self._base.bind('<ButtonRelease-1>', self._deselectPiece)
        self._base.bind('<Button-3>', self._rightClickEvent)
        self._base.bind('<ButtonRelease-3>', self._finishShape)
        self._base.bind('<Right>', self._advancePGN)
        self._base.bind('<Left>', self._backtrackPGN)
        # self._base.bind('<space>', self._printFEN)
        # self._base.bind('<Up>', self._printPGN)
        # self._base.bind('<Return>', self._inputGo)
        self._base.bind('r', self._resetBoard)
        self._base.bind('<Control_L>s', self._commitAllVariations)
        self._base.bind('a', self._analyzePosition)

        # Tracker for when pieces are moved
        self._activeCell = Cell()
        
        self._isPlayerWhite = asWhite

        self._activeArrows = {}
        self._activeCircles = {}
        self._originalArrowCoordinate = ()

        self._readFEN(FENCode, asWhite)

        # self._opponentPlayer = VariationPlayer(            
        #     {"e4" : {"c6": {"Nf3" : {"d5" : {"Nc3" : {"dxe4" : {"Nxe4" : {"Bf5" : {"Ng3" : {"Bg6" : {"h4" : {"h6" : {"Ne5" : {"Bh7" : {"Qh5" : {"g6" : {"Bc4" : {"e6" : {"Qe2" : {"Bg7" : {"Nxf7" : {"Kxf7" : {"Qxe6+" : {"Kf8" : {"Qf7#" : None}}}}}}}}}}}}}}}}}}}}}}}}}
        # )
        self._opponentPlayer = LichessPlayer(startingFEN = FENCode)
        # self._kibitzer = ChessDBCNKibitzer()
        self._kibitzer = ChessDBCNKibitzer()
        # self._tree = Gametree()

        
        # self._tree.loadTree("user.json")

        self._activeTree = LinkedTree()

        self._customFEN = FENCode
        # self._customMoveList = ["e4","e5","Nf3","Nc6","Bc4","Nf6","Ng5"]
        # self._tree.beginFromMoves(self._customMoveList)

    def _move(self, event):
        """ Updates the piece to the mouse's position """
        # Makes sure that a piece has been selected
        if not self._activeCell.isEmpty():

            # Centers the piece on the mouse's center
            self._board.moveto(
                self._activeCell.record, 
                event.x-int(self.BOX_LEN/2), 
                event.y-int(self.BOX_LEN/2)
                )
            
            # Moves the moving piece in front of all other drawn pieces
            self._board.tag_raise(self._activeCell.record)

    def _selectPiece(self, event):
        """ Determines the piece pressed, and marks the original position """
      #   # Blocks moves after game completion
      #   if not self._isGameActive:
      #       return

        # Blocks selections outside of the game board
        if event.x >= 760 or event.y >= 760:
            return

        # Resets the arrows/highlighted boxes
        self._resetShapes()

        # Records the old position
        self._originalPos = getBoardCoordinate(event)

        # Remembers the current cell that will be manipulated
        self._activeCell = \
            copy.copy(self._board.getCell(self._originalPos))

    def _deselectPiece(self, event):
        """ Puts down the piece and marks its completion """

        # Block any drops outside
        if event.x >= 760 or event.y >= 760:
            self._rightClickEvent(None)

        # Gets the box that the mouse is in
        clickLoc = getBoardCoordinate(event)

        # Checks if an actual piece is being pressed
        if not self._activeCell.isEmpty() and not clickLoc == self._originalPos:

            # Promotion: Need to add an extra bit to get the user to choose their promotion piece
            if clickLoc.x in [0, 7] and self._activeCell.text.upper() == 'P':
               originalLocation = self._originalPos
               initialCell = self._activeCell
               self._displayPromotion(clickLoc.y)
               while len(self._promotionText) == 0:
                  for button in self._promotionButtons:
                        button.update()

               self._board.delete(self._testWindow)

               # Needs to reassign because of mixing between canvas and
               # buttons
               self._originalPos = originalLocation
               self._activeCell = initialCell

            # converts the coordinates to LAN
            attemptedMoveAN = \
                Coordinate.toLAN(self._originalPos, clickLoc, self._isPlayerWhite) \
                + self._promotionText.lower()

            attemptedMove = chess.Move.from_uci(attemptedMoveAN)

            allMoves = self._boardLogic.legal_moves

            if (attemptedMove in allMoves):
                self._endMove(clickLoc)

                moveSAN = self._boardLogic.san(chess.Move.from_uci(attemptedMoveAN))

                self._boardLogic.push_uci(attemptedMoveAN)
                self._activeTree.addMove(moveSAN)
                self._activeTree.advance(moveSAN)

                self._board.update_idletasks()
                # try:p
                if True:
                    # Get and push the oppponent's move
                    #lan
                    oppMove = self._opponentPlayer.getMove(
                        self._boardLogic.fen()
                        # attemptedMoveAN, 
                        # [self._SANtoLAN(move) \
                        #  for move in self._activeTree.getPlayedMoves()]
                        )

                    self._activeTree.addMove(self._LANtoSAN(oppMove))
                    self._activeTree.advance(self._LANtoSAN(oppMove))
                    self.pushMove(oppMove)
                # except:
                    # print("Out of moves.")
                ktext = self._kibitzer.getMoves(self._boardLogic.fen())

                moveTexts = list(ktext.keys())
                i = 5
                while(len(moveTexts) > 0 and i != 0):
                    move = moveTexts.pop(0)
                    evalText = ktext[move]['score']
                    evalText = f'{int(evalText)/100:+1.2f}'
                    print(self._LANtoSAN(move) + " " + str(evalText) )
                    i -= 1
                print("--------------")


                return

        self._rightClickEvent(None)
    
    def pushMove(self, text):
        # Rough SAN detection
        if self._isLAN(text):
            lan = text
        else:
            lan = self._SANtoLAN(text)

        self._originalPos = Coordinate.stringToCoordinate(lan[0:2])
        endPos = Coordinate.stringToCoordinate(lan[2:4])

        if not self._isPlayerWhite:
            self._originalPos.invert()
            endPos.invert()
        self._promotionText = "" if len(lan) == 4 else (lan[4].upper() if self._boardLogic.turn else lan[4].lower())
        self._activeCell = copy.copy(self._board.getCell(self._originalPos))

        self._endMove(endPos)

        self._boardLogic.push_san(text)

    def _endMove(self, finalPos):
        isWhite = self._boardLogic.turn
        # Centers the object onto the square it landed on
        self._board.moveto(
            self._activeCell.record,
            getCanvasX(finalPos),
            getCanvasY(finalPos))

        delta = Coordinate.getDifference(self._originalPos, finalPos)

        # Special Case: When en passant occurs, the pawn captured needs
        #               to be manually found and removed.
        if self._activeCell.text.upper() == 'P' and abs(delta.y) == 1 and self._board.getCell(finalPos).isEmpty():
            pawn_x_index = finalPos.x + (-1 if isWhite ^ 
                                         self._isPlayerWhite else 1)
            
            self._board.delete(self._board.getCell(Coordinate(
                finalPos.x+ (1 if isWhite else -1),finalPos.y)))
            self._board.textUpdate("-" , Coordinate(pawn_x_index,finalPos.y))

        # Special case: Castling
        # Manually assigns King displacement, as startPos != endPos when
        # castling sometimes (e.x. e1g1 e1h1 both work for O-O)
        if self._activeCell.text.upper() == "K" and abs(delta.y) > 1:
            homeRowX = finalPos.x
            y_change = int(2 * abs(delta.y)/delta.y) * -1
            kingAdjustment = y_change
            
            # Need to find the rook's y location, default to 0
            rookY = 0
            if abs(7 - finalPos.y) <= 2: # close to the other side
                rookY = 7
            kingY = self._originalPos.y

            oldKingCoordinate = self._originalPos
            newKingCoordinate = Coordinate(homeRowX, kingY + kingAdjustment)
            
            # Because the rook can travel 2 or 3 spaces depending on
            # castle location, point of reference is the original king 
            # location, where 1 unit is the rook and 2 is the king.
            oldRookCoordinate = Coordinate(homeRowX, rookY)
            newRookCoordinate = Coordinate(homeRowX, kingY + kingAdjustment//2)

            # Moves the rook
            self._board.moveto(
                self._board.getCell(oldRookCoordinate).record,
                getCanvasX(newRookCoordinate),
                getCanvasY(newRookCoordinate),
            )

            self._board.textUpdate(self._board.getCell(oldRookCoordinate).text, newRookCoordinate)
            self._board.textUpdate("-", oldRookCoordinate)

            # Moves the king
            self._board.moveto(
                self._board.getCell(oldKingCoordinate).record,
                getCanvasX(newKingCoordinate),
                getCanvasY(newKingCoordinate),
            )

            self._board.textUpdate(self._board.getCell(oldKingCoordinate).text, newKingCoordinate)
            self._board.textUpdate("-", oldKingCoordinate)
        
        # non-castling cases
        else:
            # Removes old piece images on capture
            self._board.delete(self._board.getCell(finalPos).record)

            # Records the new position
            self._board.textUpdate(self._activeCell.text, finalPos)

            # Special case: Promotion
            if len(self._promotionText) != 0:
                # Update promotion square
                self._board.textUpdate(self._promotionText, finalPos)

                # Clears all promotion variables
                self._promotionText = ""
                self._promotionButtons = []
                self._promotionImages = []

            # Remove the old position of the piece
            self._board.textUpdate("-", self._originalPos)

        # Forget the active piece
        self._activeCell = Cell()

    def _rightClickEvent(self, event):
        """ Restores the board prior to clicking anything """
        if not self._activeCell.isEmpty():

            # Centers the piece back to its original position
            self._board.moveto(
                self._board.getCell(self._originalPos).record,
                getCanvasX(self._originalPos), 
                getCanvasY(self._originalPos))

            # Forget the active piece
            self._activeCell = Cell()
        elif event is not None:
            self._beginShapeDrawing(event)

    def _resetShapes(self):
        for arrow in list(self._activeArrows.values()):
            self._board.delete(arrow)
        for circle in list(self._activeCircles.values()):
            self._board.delete(circle)
        self._activeArrows = {}
        self._activeCircles = {}
        self._originalArrowCoordinate = None

    def _beginShapeDrawing(self, event):
        """ Records the inital coordinate that was right-clicked """
        x = event.x
        y = event.y

        self._originalArrowCoordinate = Coordinate(
            (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
            (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
        )
        
    def _finishShape(self, event):
        """ Completes the shape if possible, erases any duplicates """
        # This blocks if you right click and then left click
        if self._originalArrowCoordinate is not None:
            x = event.x
            y = event.y    

            final = Coordinate(
                (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
                (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
            )

            # Checks if the original and final square is the same
            if final.x == self._originalArrowCoordinate.x and \
               final.y == self._originalArrowCoordinate.y:
                # Checks and removes a duplicate circle
                if final.toTuple() in list(self._activeCircles.keys()):
                    self._board.delete(self._activeCircles[final.toTuple()])
                    del self._activeCircles[final.toTuple()]
                # Draws the circle, indexing the selected box
                else:
                    self._activeCircles[final.toTuple()] = \
                        self._board.drawCircleHighlight(final)
            # Arrow
            else:
                # Checks and removes a duplicate arrow
                if (self._originalArrowCoordinate.toTuple(), final.toTuple())\
                                           in list(self._activeArrows.keys()):
                    self._board.delete(
                        self._activeArrows[(
                            self._originalArrowCoordinate.toTuple(), 
                            final.toTuple()
                            )]
                        )
                    del self._activeArrows[
                        (self._originalArrowCoordinate.toTuple(),
                         final.toTuple())]
                # Draws the arrow, indexing the original and final box
                else:
                    self._activeArrows[
                        (self._originalArrowCoordinate.toTuple(), 
                            final.toTuple())] = \
                         self._board.drawArrow(self._originalArrowCoordinate, 
                                                final)

            self._originalArrowCoordinate = ()

    def _resetShapes(self):
        for arrow in list(self._activeArrows.values()):
            self._board.delete(arrow)
        for circle in list(self._activeCircles.values()):
            self._board.delete(circle)
        self._activeArrows = {}
        self._activeCircles = {}
        self._originalArrowCoordinate = None

    def _displayPromotion(self, y_index):
        x_pixel = 0
        y_pixel = 0

        def makePromotionTextFunction(text):
            def promotionText():
                self._promotionText = text
            return promotionText

        self._frame = Frame(self._base)

        # Top of the board, white
        isWhite = self._boardLogic.turn
        promotionList = ['Q','N','R','B'] if isWhite else ['q','n','r','b']

        # Bottom screen
        if isWhite ^ self._isPlayerWhite:
            promotionList.reverse()
            y_pixel = 4 * self.BOX_LEN
        x_pixel = self.BOX_LEN * y_index
        for i in range(4):
            self._promotionImages.append(
                Chessboard.getPieceFromText(promotionList[i]))
            self._promotionButtons.append(
                Button(self._frame, bg = "White", borderwidth = 0,
                       highlightthickness=0,image = self._promotionImages[i],
                       command = makePromotionTextFunction(promotionList[i])
                )
            )
            self._promotionButtons[i].pack()
        self._testWindow = self._board.create_window(
            x_pixel,
            y_pixel,
            anchor = NW, 
            window = self._frame
        )
        self._board.update_idletasks()

    def _resetBoard(self, event):
        print('r')
        self._promotionText = ''
        self._promotionImages = []
        self._promotionButtons = []

        # Tracker for when pieces are moved
        self._activeCell = Cell()

        self._activeArrows = {}
        self._activeCircles = {}
        self._originalArrowCoordinate = ()

        self._board.resetBoard()

        self._readFEN(self._customFEN, self._isPlayerWhite)

        # self._tree.revertTree()
        self._opponentPlayer = LichessPlayer(startingFEN = self._customFEN)

    def _commitAllVariations(self, event):
        print('c')
        # self._tree.commitTree()
        # self._tree.saveTree("user.json")

    def _analyzePosition(self, event):
        print(self._kibitzer.getMoves(self._boardLogic.fen()))

    def _readFEN(self, FENCode, asWhite):
        """ Takes in a FENCode and initializes the board """
        self._boardLogic.set_fen(FENCode)
        self._isPlayerWhite = asWhite

        boardInfo = FENCode.split(" ")

        # Splits the FENCode into relevant information
        boardCode = boardInfo[0]

        # When the player at the bottom part of the board is black,
        # the position is simply miorred rather than changing indexing.
        # Consequently, when printing out the FEN, this must be reversed
        if not self._isPlayerWhite:
            boardCode = boardCode[::-1]

        boardGrid = self._expandFEN(boardCode)

        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                self._board.textUpdate(boardGrid[row][col], 
                                        Coordinate(row, col))

    def _expandFEN(self, boardFEN) -> list:
        cleanedCode = ""
        numberList = ("1", "2", "3", "4", "5", "6", "7", "8")

        # Converts numbers into dashes
        for index in range(len(boardFEN)):
            if boardFEN[index] in numberList:
                for repeats in range(int(boardFEN[index])):
                    cleanedCode += "-"
            else:
                cleanedCode += boardFEN[index]
        
        boardRowLists = [list(row) for row in cleanedCode.split("/")] 

        boardGrid = []
        for row in boardRowLists:
            rowInfo = []
            for character in row:
                rowInfo.append(character)

            boardGrid.append(rowInfo)
        
        return boardGrid

    def _backtrackPGN(self, event):
        if not self._activeTree.hasMoves():
            return
        
        # The actual move isn't important
        self._activeTree.backpedal()

        # # Update tree to follow the game progress
        # self._activeTree.startFrom(list(self._playedMoves))
        
        lastBoardFEN = self._boardLogic.board_fen()
        self._boardLogic.pop()
        newBoardFEN = self._boardLogic.board_fen()

        self._updateVisualBoard(lastBoardFEN, newBoardFEN)

    def _advancePGN(self, event):
        if self._activeTree.hasNext():
            lastBoardFEN = self._boardLogic.board_fen()
            self._boardLogic.push_san(self._activeTree.advance())
            newBoardFEN = self._boardLogic.board_fen()
            self._updateVisualBoard(lastBoardFEN, newBoardFEN)

    def _updateVisualBoard(self, lastBoardFEN, newBoardFEN):
        if not self._isPlayerWhite:
            lastBoardFEN = lastBoardFEN[::-1]
            newBoardFEN = newBoardFEN[::-1]

        lastBoard = self._expandFEN(lastBoardFEN)
        newBoard = self._expandFEN(newBoardFEN)

        # It's faster to check what needs to be updated instead of
        # redrawing every new image 
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                if not lastBoard[row][col] == newBoard[row][col]:
                    self._board.textUpdate(
                        newBoard[row][col], Coordinate(row,col))

    def _isLAN(self, text):
        if text[0].isupper():
            return False
        if not len(text) in [4,5]:
            return False
        if "+" in text or "#" in text or "=" in text:
            return False
        return True

    # SAN -> LAN
    def _SANtoLAN(self, moveText):
        return self._boardLogic.parse_san(moveText).uci()

    def _LANtoSAN(self, moveText):
        return self._boardLogic.san(chess.Move.from_uci(moveText))

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

board = Game(base, Game.DEFAULT_FEN, True)
# board = Game(base, "r1bqkb1r/pppp1ppp/2n2n2/4p1N1/2B1P3/8/PPPP1PPP/RNBQK2R b KQkq - 5 4", False)
# board = Game(base, "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", True)

base.mainloop()