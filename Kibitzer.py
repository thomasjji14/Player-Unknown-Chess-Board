import requests


class LichessKibitzer():
    # Note: The Lichess API seems to be buggy with multiPV > 1,
    #       i.e. the API doesn't return more than one line.
    def __init__(self, multiPV = 1, variant = "standard"):
        self._params = {
            "fen": "",
            "multiPV" : multiPV,
            "variant" : variant
        }
    
    def getMoves(self, FEN) -> dict:
        self._params["fen"] = FEN
        gameURLResponse = requests.get("https://lichess.org/api/cloud-eval", params = self._params)
        dictResponse = gameURLResponse.json()
        return dictResponse


class ChessDBCNKibitzer():

    def __init__(self, action = "queryall"):
        self._params = {
            "action" : action
        }

    def getMoves(self, FEN) -> dict:
        self._params["board"] = FEN
        gameURLResponse = requests.get("http://www.chessdb.cn/cdb.php?", params = self._params)
        textResponse = gameURLResponse.text
        return self._parseMoveResponse(textResponse)
    
    def _parseMoveResponse(self, moveText) -> dict:
        parsedDictionary = {}
        lines = moveText.split("|")
        if len(lines) == 0:
            return {}
        for line in lines:
            categorySplits = line.split(",")

            moveText = categorySplits.pop(0)
            if "unknown" in moveText or "mate" in moveText:
                return {}
            uciText = moveText.split(":")[1]
            subDict = {}
            for categorySplit in categorySplits:
                dividedCategoryInfo = categorySplit.split(":")
                categoryName = dividedCategoryInfo[0]
                categoryInfo = dividedCategoryInfo[1]
                subDict[categoryName] = categoryInfo
            
            parsedDictionary[uciText] = subDict
        
        return parsedDictionary
