# from re import split
# from copy import *
# import json


# class MoveNotInTreeError(RuntimeError):
#     def __init__(self, str = ""):
#         super(str)
from __future__ import annotations
from collections import deque
import heapq


class _WeightedMove():
    """
    A class (record) of a move and its associated weight.

    ...

    Methods
    -------
    getMove()
        Returns the move associated with the instance
    setMove(move)
        Sets the instance's move
    getWeight()
        Returns the weight associated witht he instance
    setWeight(weight)
        Sets the instance's weight
    """

    def __init__(self, move, weight):
        """
        Parameters
        ----------
        move : str
            The text representation (typically in SAN) of the move
        weight : int
            The weight of the move
        """
        self._move = move
        self._weight = weight
    
    def __eq__(self, other):
        """ Checks for equality based on the weights """
        return self.getWeight() == other.getWeight()

    def __lt__(self, other):
        """ Comparisons based on the weights """
        return self.getWeight() < other.getWeight()

    def __le__(self, other):
        """ Comparisons based on the weights """
        return self.getWeight() <= other.getWeight()

    def __gt__(self, other):
        """ Comparisons based on the weights """
        return self.getWeight() > other.getWeight()

    def __ge__(self, other):
        """ Comparisons based on the weights """
        return self.getWeight() >= other.getWeight()
    
    def __repr__(self):
        """ Formatted as a constructor call """
        return f"WeightedMove({self._move}, {self._weight})"

    def getMove(self) -> str:
        """ 
        Returns the move associated with the instance

        Returns
        -------
        str: the move
        """
        return self._move

    def setMove(self, move):
        self._move = move

    def getWeight(self):
        return self._weight

    def setWeight(self, weight):
        self._weight = weight



class _LinkedTreeNode():

    def __init__(self, parentNode = None, parentsMove = None):
        self._parentNode = parentNode
        self._parentsMove = parentsMove
        self._moveQueue = []
        self._moveDict = {}

    def __str__(self):
        return f"Moves: {str(self._moveQueue)} | Dict: {str(self._moveDict)} | Parent: {self._parentNode}"
    
    def __repr__(self):
        return f"_LinkedTreeNode({self._parentNode})"
    
    def addMove(self, weightedMove) -> None:
        # TODO: Verify that heapify doesn't change order of 1s
        # TODO: Define behavior when the move is already in
        heapq.heappush(self._moveQueue, weightedMove)
        self._moveDict[weightedMove.getMove()] = _LinkedTreeNode(self, weightedMove.getMove())
        pass


    def getNext(self, weightedMove) -> _WeightedMove:
        return self._moveDict[weightedMove.getMove()]
    
    def hasMove(self, weightedMove) -> bool:
        return weightedMove.getMove() in list(self._moveDict.keys())

    def getParent(self) -> _LinkedTreeNode:
        return self._parentNode

    def getParentMove(self) -> str:
        return self._parentsMove

    def getMoveWeight(self, weightedMove) -> int:
        for move in self._moveQueue:
            if move.getMove() == weightedMove.getMove():
                return move.getWeight()
            
        raise IndexError()

    def setMoveWeight(self, weightedMove) -> None:
        for move in self._moveQueue:
            if move.getMove() == weightedMove.getMove():
                move.setWeight(weightedMove.getWeight())
                return
            
        raise IndexError()

    def getNumChildren(self) -> int:
        return len(self._moveDict)

    def getAllMoves(self) -> list:
        return [wmove.getMove() for wmove in self._moveQueue]


    def getAllChildren(self) -> list:
        moves = self.getAllMoves()
        return [self._moveDict[move] for move in moves]

    def dropNode(self, moveName):
        self._moveDict.pop(moveName)


class LinkedTree():
    """
    LinkedTree is similar to a linked list, but allows for multiple
    (ordered) connections. The order is first by the weight (if 
    specified), or otherwise by the order (LIFO). 

    Note that 1 is defined as the default and highest weight, and lower
    priorities are higher values (i.e. using a min heap)
    """

    def __init__(self):
        self._root = _LinkedTreeNode()
        self._curNode = self._root
        self._startingMoves = deque()

    def advance(self, move, weight = 1) -> None:
        """
        Progresses in the tree; adds the move or updates the weight.
        """
        weightedMove = _WeightedMove(move, weight)

        self._startingMoves.append(move)

        # Already seen
        if self._curNode.hasMove(weightedMove):
            # Update the weight; doesn't change queue order
            self._curNode.setMoveWeight(weightedMove)
        else:
            self._curNode.addMove(weightedMove)

        self._curNode = self._curNode.getNext(weightedMove)

        print(self.printTree())
    
    def backpedal(self) -> str:
        """ Returns the last move played """
        if self._curNode is self._root: 
            raise IndexError("cannot go further back or tree not filled")

        self._curNode = self._curNode.getParent()
        return self._startingMoves.pop()
    
    def deleteMove(self):
        self._curNode

    def printTree(self, spacer = " ") -> str:
        class DepthNode():
            def __init__(self, node, depth):
                self.node = node
                self.depth = depth

        treeString = ""

        nodeStack = deque()

        nodeStack.append(DepthNode(self._root, 0))
        while len(nodeStack) != 0:
            curTraversal = nodeStack.pop()

            parentMove = curTraversal.node.getParentMove()
            if not parentMove is None:
                treeString += spacer*curTraversal.depth + curTraversal.node.getParentMove() + "\n"
            for node in curTraversal.node.getAllChildren():
                nodeStack.append(DepthNode(node, curTraversal.depth + 1))
        
        return treeString
    
    def getPlayedMoves(self) -> list:
        return list(self._startingMoves)

    def asLines(self) -> list:
        class DepthNode():
            def __init__(self, node, depth):
                self.node = node
                self.depth = depth

        moveCallStack = deque()
        nodeStack = deque()

        lines = []

        nodeStack.append(DepthNode(self._root, 0))
        while len(nodeStack) != 0:
            curTraversal = nodeStack.pop()

            while curTraversal.depth != 0 and curTraversal.depth - 1 < len(moveCallStack):
                moveCallStack.pop()
            
            parentMove = curTraversal.node.getParentMove()

            if not parentMove is None:
                moveCallStack.append(parentMove)

            if curTraversal.node.getNumChildren() == 0:
                lines.append(list(moveCallStack))
            else:
                for node in curTraversal.node.getAllChildren():
                    nodeStack.append(DepthNode(node, curTraversal.depth + 1))
        
        return lines

    def populateFromRoot(self, moves, weight = 1):
        oldCur = self._curNode

        self._curNode = self._root

        for move in moves:
            self.advance(move, weight)

        self._curNode = oldCur
    
    def populateFromCur(self, moves, weight = 1):
        oldCur = self._curNode

        for move in moves:
            self.advance(move, weight)

        self._curNode = oldCur

    def hasMoves(self):
        return len(self._startingMoves) != 0

    # def toDict(self):
    #     returnDict = {}

        
    

if __name__ == "__main__":
    a = LinkedTree()
    lines = [
        ["e4", "e5", "d3"],
        ["e4", "d4", "exd4"],
    ]

    for line in lines:
        a.populateFromRoot(line)

    print(a.printTree())
    print(a.asLines())

    lines = lines





# class Gametree():

    # def __init__(self):
    #     # Full tree that changes with the subtree
    #     self.__tree = {}
    #     # Copy of the original tree between resets, used if you want
    #     # to revert back to the original
    #     self.__memoryTree = {}
    #     # Active subtree    
    #     self.__currentSubtree = self.__tree

    # def clearMemory(self):
    #     self.__tree = {}
    #     self.__currentSubtree = {}
    #     self.__memoryTree = self.__tree

    # def commitTree(self):
    #     self.__memoryTree = deepcopy(self.__tree)
    
    # def revertTree(self):
    #     self.__tree = deepcopy(self.__memoryTree)
    
    # def clearInitialMoves(self):
    #     self.__currentSubtree = self.__tree

    # def populateFromList(self, line):
    #     """
    #     Takes a list of moves represented as SAN strings        
    #     """
    #     if not type(line) is list:
    #         raise TypeError("Gametree population must be done with a list.")
    #     populationSubtree = self.__currentSubtree
    #     while(len(line) > 0):
    #         move = line.pop(0)
    #         if move not in list(populationSubtree.keys()):
    #             populationSubtree[move] = {}
    #         populationSubtree = populationSubtree[move]
    
    # def pushMove(self, move):
    #     self.populateFromList([move])
    #     self.__currentSubtree = self.__currentSubtree[move]
    
    # @staticmethod
    # def moveStringToList(line):
    #     """ From PGN move styles, assuming that there are no comments"""
    #     moveList = []
    #     splitString = line.split(" ")
    #     for i in range(len(splitString)):
    #         if i % 3 != 0:
    #             moveList.append(splitString[i])
    #     return moveList
        
    # def beginFromMoves(self, line):
    #     """ 
    #     Takes a list of SAN to begin the line with     
    #     """
    #     # Modifies the current subtree
    #     if not type(line) is list:
    #         raise TypeError("Gametree population must be done with a list.")

    #     # try:
    #     for move in line:
    #         if not type(move) is str:
    #             raise TypeError("List indicies must be string.")
    #         if not move in list(self.__currentSubtree.keys()):
    #             self.populateFromList([move])
    #         self.__currentSubtree = self.__currentSubtree[move]
    #     # except:
    #     #     raise MoveNotInTreeError()
    
    # def visualizeTrees(self, delimiter = " "):
    #     """
    #     Performs a printout of the tree (debugging purposes only).
    #     """
    #     print("Tree")
    #     print(self._visualizeEmbeddedDict(self.__tree, delimiter))
    #     print("MemoryTree")
    #     print(self._visualizeEmbeddedDict(self.__memoryTree, delimiter))
    #     print("Subtree")
    #     print(self._visualizeEmbeddedDict(self.__currentSubtree, delimiter))

    # def saveTree(self, filename):
    #     with open(filename, "w+") as f:
    #         json.dump(self.__tree, f, sort_keys = True, indent = 4)

    # def loadTree(self, filename):
    #     with open(filename, "r+") as f:
    #         self.__tree = json.load(f)
    #         self.commitTree()
    #         self.__currentSubtree = self.__tree
    #     # self.__tree = json.loads(filename)
    
    # @staticmethod
    # def _visualizeEmbeddedDict(tree, delimiter, moveSplitter = "\n"):
    #     charactersToIgnore = [" ", ","]
    #     charactersToNewline = ["\'"]
    #     # the character, ' , is used to determine when a new line is
    #     # found, so remove trailing chars
    #     treeString = str(tree).replace("\':", "")

    #     returnString = ""
    #     spacing = -1
    #     for char in treeString:
    #         if char in charactersToIgnore:
    #             continue
    #         elif char == "{":
    #             spacing += 1
    #         elif char == "}":
    #             spacing -= 1
    #         elif char in charactersToNewline:
    #             returnString += moveSplitter + delimiter * spacing
    #         else:
    #             returnString += char
        
    #     return returnString

    # def toLines(self):
    #     """ Returns the saved version of the tree in PGN lines """
    #     dictString = self._visualizeEmbeddedDict(self.__memoryTree, delimiter = " ", moveSplitter = "|")

    #     moves = dictString.split("|")
    #     moves = moves[1:] # discard first element (a dud empty string)

    #     moveStack = []
    #     lines = []

    #     lastDepth = 0
    #     curDepth = 0

    #     for move in moves:
    #         curDepth = move.count(" ")
            
    #         if len(moveStack) == 0:
    #             moveStack.append(move)
    #         else:
    #             if curDepth <= lastDepth:
    #                 # if curDepth != lastDepth:
    #                 lines.append(copy(moveStack)[::-1])
    #                 for i in range(abs(curDepth - lastDepth) + 1):
    #                     moveStack.pop(0)
    #             moveStack.insert(0, move.strip())
                
    #         lastDepth = curDepth
        
    #     # Since the for loop only compares moving forward, the last
    #     # one will be dropped; manually add it in.
    #     if len(moveStack) != 0:
    #         lines.append(copy(moveStack)[::-1])
    #     return lines





    # print(_WeightedMove("s",5))
    # a = LinkedTree()
    # a.pushMove("e4")
    # print(a.popMove())



    


# if __name__ == "__main__":
#     # a = [_WeightedMove("e"+str(i), i) for i in range(8)]
#     # a = [i for i in range(8)]
#     a = [3,2,1,4]

#     print([str(move) for move in a])

#     heapq.heapify(a)

#     print([str(move) for move in a])


#     # Sample code
#     a = Gametree()
#     a.populateFromList(["e4", "e5", "c3"])
#     a.populateFromList(["e4", "e5", "c4"])
#     a.populateFromList(["e4", "e5", "d4"])
#     a.populateFromList(["e4", "c5", "d4"])
    
#     a.commitTree()
#     print(a.toLines())
#     # a.visualizeTrees(delimiter = "-")

#     # a.beginFromMoves(["e4"])

#     # print("----------")

#     # a.visualizeTrees(delimiter="-")
#     # a.populateFromList(["h5"])

#     # print("---------")
#     # a.visualizeTrees
    
#     # print("------")
#     # a.commitTree()
#     # a.visualizeTrees(delimiter= "-")

#     # a.populateFromList(["c4", "d5"])
#     # a.revertTree()
#     # a.visualizeTrees(delimiter="-")