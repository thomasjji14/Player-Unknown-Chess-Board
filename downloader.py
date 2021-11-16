import requests
import re
import json
import time
import copy
import pickle


ECO_INDEX = 7
OPENING_INDEX = 1
GAME_MOVES = 0
GAME_OUTCOME = 1



# startTime = time.time()
# Start from the beginning, then keep going
# Idea: Change the start date (+1 month) once it's verified that all
#       data within a month is done.
# Keep an archieve of already seen games

def downloadGames(userdata):
    # Gets user game data
    gameURLResponse = requests.get('https://api.chess.com/pub/player/' + userdata["USERNAME"] + '/games/archives')

    # Retrieves past monthy game archieves, oldest -> newest
    gameURLs = gameURLResponse.json()['archives']

    #Gets the monthly games, and adds them to a large list of games
    games = []
    for url in gameURLs:
        month = url.split("/")[-1]
        year = url.split("/")[-2]

        # Note: this process gathers games from past the current month
        if int(year) > int(userdata["CURRENT_YEAR"]) or ((int(year) == int(userdata["CURRENT_YEAR"])) and int(month) >= int(userdata["CURRENT_MONTH"])):
            monthlyGamesResponse = requests.get(url)
            monthlyGames = monthlyGamesResponse.json()['games']
            games += monthlyGames

    if userdata["CURRENT_GAME_ID"] is not None:
        newGameIndex = 0
        while True:
            if newGameIndex == len(games):
                return []

            gameID = int(games[newGameIndex]["url"].split("/")[-1])
            newGameIndex += 1


            # Finds the first game that is greater
            if gameID > userdata["CURRENT_GAME_ID"]:
                date = re.findall("(?<=EndDate \\\")\d*.\d*.\d*", games[newGameIndex]["pgn"])[0]
                splitDate = date.split(".")
                year = splitDate[0]
                month = splitDate[1]

                # Should you advance to the last game of the month or
                # go beyond, it will update the month/year accordingly
                # to prevant over-downloading.
                if int(year) > int(userdata["CURRENT_YEAR"]) or ((int(year) == int(userdata["CURRENT_YEAR"])) and int(month) >= int(userdata["CURRENT_MONTH"])):
                    userdata["CURRENT_YEAR"] = year
                    userdata["CURRENT_MONTH"] = month
                    with open("user.json", "w") as f:
                        json.dump(userdata, f)
                break
        games = games[newGameIndex-1:]

    return games

def parsePGN(pgnText):
    return re.findall("(?<=\. )[A-Za-z]+\S*(?= )", pgnText)

# games = downloadGames("bankericebutt")


# print(re.findall("(?<= )[A-Za-z]+\d+\S*", games[0]['pgn']))



# print(type(games))
# print(games[0])
# with open("bankerice.pkl", "wb") as f:
#     pickle.dump(games, f)
# with open("dump.txt", "w") as f:
#     json.dump(games, f)




# The opening repotoire needs to be sorted, one as black, one as white
# as to distinguish my moves from my opponents moves.
# Should also go from most recent to oldest, going to the first game