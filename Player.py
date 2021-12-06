import requests
import random
from chess import Move

DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class OutOfMovesException(Exception):
    def _init__(self):
        super()

class WrongVariationException(Exception):
    def _init__(self):
        super()

class LichessPlayer():

    def __init__(
        self, variant = "standard", 
        speeds = ["bullet", "blitz", "rapid", "classical"], 
        ratings = [1600, 1800, 2000, 2200, 2500],
        startingFEN = DEFAULT_FEN
        ):
        # self._pastMoves = []
        self._params = {
            "variant": variant,  
            "speeds[]": speeds, 
            "ratings[]" : ratings, 
            "moves" : 999, 
            "recentGames" : 1,
            "fen" : startingFEN
        }

#     def getMove(self, lastMove, moveList = None):
#         if moveList is None:
#             self._pastMoves.append(lastMove)
#         else:
#             self._pastMoves = moveList
#         self._params["play"] = self._moveToString(self._pastMoves)

    def getMove(self, newFEN):
        self._params["fen"] = newFEN

        gameURLResponse = requests.get("https://explorer.lichess.ovh/lichess", params = self._params)

        json_response = gameURLResponse.json()
        moves = json_response['moves']

        moveCumFrequency = {}
        totalGames = 0
        for move in moves:
            moveCount = move['white'] + move['black'] + move["draws"]
            totalGames += moveCount
            moveCumFrequency[move['uci']] = totalGames

        if totalGames == 0:
            print("Out of games.")
            raise OutOfMovesException()

        randomMoveNumber = random.randint(1, totalGames)
        randomMove = self._getRandomMove(randomMoveNumber, moveCumFrequency)

        # self._pastMoves.append(randomMove)

        return randomMove
    
    def _moveToString(self, moves):
        return "".join([i+"," for i in moves])[:-1]

    def _getRandomMove(self, randNum, moveFrequency):
        for key in list(moveFrequency.keys()):
            if randNum <= moveFrequency[key]:
                return key


class VariationPlayer():
    
    def __init__(self, inputVariation):
        self._variation = inputVariation
    
    def getMove(self, lastMove):
        if self._variation is None:
            # raise OutOfMovesException()
            return None
        if not lastMove in self._variation:
            return None
        
        self._variation = self._variation[lastMove]
        
        moveToReturn = list(self._variation.keys())[random.randint(0, len(self._variation)-1)]

        self._variation = self._variation[moveToReturn]
        return moveToReturn