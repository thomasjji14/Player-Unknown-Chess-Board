from re import split
from copy import *
import json


class MoveNotInTreeError(RuntimeError):
    def __init__(self, str = ""):
        super(str)

class Gametree():
    def __init__(self):
        # Full tree that changes with the subtree
        self.__tree = {}
        # Copy of the original tree between resets, used if you want
        # to revert back to the original
        self.__memoryTree = {}
        # Active subtree
        self.__currentSubtree = self.__tree

    def clearMemory(self):
        self.__tree = {}
        self.__currentSubtree = {}
        self.__memoryTree = self.__tree

    def commitTree(self):
        self.__memoryTree = deepcopy(self.__tree)
    
    def revertTree(self):
        self.__tree = deepcopy(self.__memoryTree)
    
    def clearInitialMoves(self):
        self.__currentSubtree = self.__tree

    def populateFromList(self, line):
        """
        Takes a list of moves represented as SAN strings        
        """
        if not type(line) is list:
            raise TypeError("Gametree population must be done with a list.")
        populationSubtree = self.__currentSubtree
        while(len(line) > 0):
            move = line.pop(0)
            if move not in list(populationSubtree.keys()):
                populationSubtree[move] = {}
            populationSubtree = populationSubtree[move]
    
    def pushMove(self, move):
        self.populateFromList([move])
        self.__currentSubtree = self.__currentSubtree[move]
    
    @staticmethod
    def moveStringToList(line):
        """ From PGN move styles, assuming that there are no comments"""
        moveList = []
        splitString = line.split(" ")
        for i in range(len(splitString)):
            if i % 3 != 0:
                moveList.append(splitString[i])
        return moveList
        
    def beginFromMoves(self, line):
        """ 
        Takes a list of SAN to begin the line with     
        """
        # Modifies the current subtree
        if not type(line) is list:
            raise TypeError("Gametree population must be done with a list.")

        # try:
        for move in line:
            if not type(move) is str:
                raise TypeError("List indicies must be string.")
            if not move in list(self.__currentSubtree.keys()):
                self.populateFromList([move])
            self.__currentSubtree = self.__currentSubtree[move]
        # except:
        #     raise MoveNotInTreeError()
    
    def visualizeTrees(self, delimiter = " "):
        """
        Performs a printout of the tree (debugging purposes only).
        """
        print("Tree")
        print(self._visualizeEmbeddedDict(self.__tree, delimiter))
        print("MemoryTree")
        print(self._visualizeEmbeddedDict(self.__memoryTree, delimiter))
        print("Subtree")
        print(self._visualizeEmbeddedDict(self.__currentSubtree, delimiter))

    def saveTree(self, filename):
        with open(filename, "w+") as f:
            json.dump(self.__tree, f, sort_keys = True, indent = 4)

    def loadTree(self, filename):
        with open(filename, "r+") as f:
            self.__tree = json.load(f)
            self.commitTree()
            self.__currentSubtree = self.__tree
        # self.__tree = json.loads(filename)
    
    @staticmethod
    def _visualizeEmbeddedDict(tree, delimiter, moveSplitter = "\n"):
        charactersToIgnore = [" ", ","]
        charactersToNewline = ["\'"]
        # the character, ' , is used to determine when a new line is
        # found, so remove trailing chars
        treeString = str(tree).replace("\':", "")

        returnString = ""
        spacing = -1
        for char in treeString:
            if char in charactersToIgnore:
                continue
            elif char == "{":
                spacing += 1
            elif char == "}":
                spacing -= 1
            elif char in charactersToNewline:
                returnString += moveSplitter + delimiter * spacing
            else:
                returnString += char
        
        return returnString

    def toLines(self):
        """ Returns the saved version of the tree in PGN lines """
        dictString = self._visualizeEmbeddedDict(self.__memoryTree, delimiter = " ", moveSplitter = "|")

        moves = dictString.split("|")
        moves = moves[1:] # discard first element (a dud empty string)

        moveStack = []
        lines = []

        lastDepth = 0
        curDepth = 0

        for move in moves:
            curDepth = move.count(" ")
            
            if len(moveStack) == 0:
                moveStack.append(move)
            else:
                if curDepth <= lastDepth:
                    # if curDepth != lastDepth:
                    lines.append(copy(moveStack)[::-1])
                    for i in range(abs(curDepth - lastDepth) + 1):
                        moveStack.pop(0)
                moveStack.insert(0, move.strip())
                
            lastDepth = curDepth
        
        # Since the for loop only compares moving forward, the last
        # one will be dropped; manually add it in.
        if len(moveStack) != 0:
            lines.append(copy(moveStack)[::-1])
        return lines

            


    # @staticmethod
    # def _toLinesHelper(currDict, line = "", depth = 2):
    #     if currDict is None:
            
    #         return
    #     for move in list(currDict.keys()):
    #         Gametree._toLinesHelper(
    #             currDict[move], 
    #             line = line + (str(int(depth/2)) + ". " if depth % 2 == 0 else "") + move, 
    #             depth = depth + 1
                # )


            

if __name__ == "__main__":
    # Sample code
    a = Gametree()
    a.populateFromList(["e4", "e5", "c3"])
    a.populateFromList(["e4", "e5", "c4"])
    a.populateFromList(["e4", "e5", "d4"])
    a.populateFromList(["e4", "c5", "d4"])
    
    a.commitTree()
    print(a.toLines())
    # a.visualizeTrees(delimiter = "-")

    # a.beginFromMoves(["e4"])

    # print("----------")

    # a.visualizeTrees(delimiter="-")
    # a.populateFromList(["h5"])

    # print("---------")
    # a.visualizeTrees
    
    # print("------")
    # a.commitTree()
    # a.visualizeTrees(delimiter= "-")

    # a.populateFromList(["c4", "d5"])
    # a.revertTree()
    # a.visualizeTrees(delimiter="-")