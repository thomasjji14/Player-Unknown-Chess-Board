# from re import split
# from copy import *
# import json


# class MoveNotInTreeError(RuntimeError):
#     def __init__(self, str = ""):
#         super(str)
from __future__ import annotations
from collections import deque
from typing import Deque

class _LinkedTreeNode():

    def __init__(self, parentNode = None, parentsMove = None):
        self._parentNode = parentNode
        self._parentsMove = parentsMove
        self._moveQueue = deque()
        self._moveDict = {}

    def __str__(self):
        return f"Moves: {str(self._moveQueue)} | Dict: {str(self._moveDict)} | Parent: {self._parentNode}"
    
    def __repr__(self):
        return f"_LinkedTreeNode({self._parentNode})"
    
    def addMove(self, move) -> None:
        self._moveQueue.append(move)
        self._moveDict[move] = _LinkedTreeNode(self, move)
        pass


    def getNext(self, move) -> str:
        return self._moveDict[move]
    
    def hasMove(self, move) -> bool:
        return move in list(self._moveDict.keys())

    def getParent(self) -> _LinkedTreeNode:
        return self._parentNode

    def getParentMove(self) -> str:
        return self._parentsMove

    # def getMoveWeight(self, move) -> int:
    #     for move in self._moveQueue:
    #         if move.getMove() == weightedMove.getMove():
    #             return move.getWeight()
            
    #     raise IndexError()

    # def setMoveWeight(self, move) -> None:
    #     for queuedmove in self._moveQueue:
    #         if move == move:
    #             move.setWeight(move.getWeight())
    #             return
            
    #     raise IndexError()

    def getNumChildren(self) -> int:
        return len(self._moveDict)

    def getAllMoves(self) -> list:
        return list(self._moveQueue)


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

    def advance(self, move) -> None:
        """
        Progresses in the tree; does not add moves into the tree
        """

        if not self._curNode.hasMove(move):
            raise KeyError("Move not found")

        self._startingMoves.append(move)

        self._curNode = self._curNode.getNext(move)

        # DEBUG
        print(self.asLines())

    def addMove(self, move):
        """
        Adds the move into the tree. No behavior changes if move exists 
        already.
        """
        if not self._curNode.hasMove(move):
            self._curNode.addMove(move)       
    
    def backpedal(self) -> str:
        """ Returns the last move played """
        if self._curNode is self._root: 
            raise IndexError("cannot go further back or tree not filled")

        self._curNode = self._curNode.getParent()
        return self._startingMoves.pop()
    
    def deleteMove(self):
        # self._curNode
        pass

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
            
            # The DFS goes from the last node to the first, flipping to
            # compensate
            children = curTraversal.node.getAllChildren()[::-1]
            for node in children:
                nodeStack.append(DepthNode(node, curTraversal.depth + 1))
        
        return treeString

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
                # The DFS goes from the last node to the first, flipping to
                # compensate
                children = curTraversal.node.getAllChildren()[::-1]
                for node in children:
                    nodeStack.append(DepthNode(node, curTraversal.depth + 1))
        
        return lines

    def getPlayedMoves(self) -> list:
        return list(self._startingMoves)

    def populateFromRoot(self, moves):
        oldCur = self._curNode

        self._curNode = self._root

        for move in moves:
            self.advance(move)

        self._curNode = oldCur
    
    def populateFromCur(self, moves):
        oldCur = self._curNode

        for move in moves:
            self.advance(move)

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