from re import split
from copy import deepcopy


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

        try:
            for move in line:
                if not type(move) is str:
                    raise TypeError("List indicies must be string.")
                self.__currentSubtree = self.__currentSubtree[move]
        except:
            raise MoveNotInTreeError()
    
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
    
    @staticmethod
    def _visualizeEmbeddedDict(tree, delimiter):
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
                returnString += "\n" + delimiter * spacing
            else:
                returnString += char
        
        return returnString

if __name__ == "__main__":
    # Sample code
    a = Gametree()
    a.populateFromList(["e4", "e5", "c3"])
    a.populateFromList(["e4", "e5", "c4"])
    a.populateFromList(["e4", "e5", "d4"])
    a.populateFromList(["e4", "c5", "d4"])
    a.visualizeTrees(delimiter = "-")

    a.beginFromMoves(["e4"])

    print("----------")

    a.visualizeTrees(delimiter="-")
    a.populateFromList(["h5"])

    print("---------")
    a.visualizeTrees
    
    print("------")
    a.commitTree()
    a.visualizeTrees(delimiter= "-")

    a.populateFromList(["c4", "d5"])
    a.revertTree()
    a.visualizeTrees(delimiter="-")