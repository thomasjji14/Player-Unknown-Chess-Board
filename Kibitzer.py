import json
import requests

class ChessDBCNKibitzer():

    def __init__(self, action = "queryall"):
        self.__params = {
            "action" : action
        }
        pass

    def getMoves(self, FEN) -> str:
        self.__params["board"] = FEN
        gameURLResponse = requests.get("http://www.chessdb.cn/cdb.php?", params = self.__params)
        json_response = gameURLResponse.text
        return self.__parseMoveResponse(json_response)
    
    def __parseMoveResponse(self, moveText) -> dict:
        parsedDictionary = {}
        lines = moveText.split("|")
        for line in lines:
            categorySplits = line.split(",")

            moveText = categorySplits.pop(0)
            uciText = moveText.split(":")[1]
            subDict = {}
            for categorySplit in categorySplits:
                dividedCategoryInfo = categorySplit.split(":")
                categoryName = dividedCategoryInfo[0]
                categoryInfo = dividedCategoryInfo[1]
                subDict[categoryName] = categoryInfo
            
            parsedDictionary[uciText] = subDict
        
        return parsedDictionary
            


# class LichessKibitzer():


