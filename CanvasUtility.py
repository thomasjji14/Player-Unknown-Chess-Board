from Coordinate import Coordinate 

BOX_LEN = 95
X_INDEX = 0
Y_INDEX = 1

def getBoardCoordinate(event):
    """ Retrieves the board x-coordinate from a click event """
    return Coordinate(int(event.y/BOX_LEN), int(event.x/BOX_LEN))

def getCanvasX(boardCoordinate):
    """ Retrieves canvas x-coordinate from board coordinates """
    return boardCoordinate.y*BOX_LEN

def getCanvasY(boardCoordinate):
    """ Retrieves canvas y-coordinate from board coordinates """
    return boardCoordinate.x*BOX_LEN

def getCanvasFromBoardCoordinate(boardCoordinate):
    return Coordinate(int((boardCoordinate.y+0.5)*BOX_LEN), int((boardCoordinate.x+0.5)*BOX_LEN))

def getNextCanvasX(boardCoordinate):
    """ Retrieves next canvas X-coordinate from board coordinates """
    return (boardCoordinate.y + 1) * BOX_LEN

def getNextCanvasY(boardCoordinate):
    """ Retrieves next canvas Y-coordinate from board coordinates """
    return (boardCoordinate.x + 1) * BOX_LEN