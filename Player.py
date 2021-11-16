import requests
import random
from chess import Move

DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class OutOfMovesException(Exception):
    def __init__(self):
        super()

class WrongVariationException(Exception):
    def __init__(self):
        super()

class LichessPlayer():

    def __init__(
        self, variant = "standard", 
        speeds = ["bullet", "blitz", "rapid", "classical"], 
        ratings = [1600, 1800, 2000, 2200, 2500],
        startingFEN = DEFAULT_FEN
        ):
        self.__pastMoves = []
        self.__params = {
            "variant": variant,  
            "speeds[]": speeds, 
            "ratings[]" : ratings, 
            "moves" : 999, 
            "recentGames" : 1,
            "fen" : startingFEN
        }

    def getMove(self, lastMove):
        self.__pastMoves.append(lastMove)
        self.__params["play"] = self.__moveToString()

        gameURLResponse = requests.get("https://explorer.lichess.ovh/lichess?", params = self.__params)

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
        randomMove = self.__getRandomMove(randomMoveNumber, moveCumFrequency)

        self.__pastMoves.append(randomMove)

        return randomMove
    
    def __moveToString(self):
        return "".join([i+"," for i in self.__pastMoves])[:-1]

    def __getRandomMove(self, randNum, moveFrequency):
        for key in list(moveFrequency.keys()):
            if randNum <= moveFrequency[key]:
                return key

class VariationPlayer():
    
    def __init__(self, inputVariation):
        self.__variation = inputVariation
    
    def getMove(self, lastMove):
        if self.__variation is None:
            raise OutOfMovesException()
        
        try:
            self.__variation = self.__variation[lastMove]
        except:
            raise WrongVariationException()
        
        moveToReturn = list(self.__variation.keys())[0]
        self.__variation = self.__variation[moveToReturn]
        return moveToReturn