# from re import split
# from copy import *
from __future__ import annotations
import json


# class MoveNotInTreeError(RuntimeError):
#     def __init__(self, str = ""):
#         super(str)
from collections import deque
from tkinter.constants import NONE

class _LinkedTreeNode():

    def __init__(self, parentNode = None, parentsMove = None):
        self._parentNode = parentNode
        self._parentsMove = parentsMove
        self._moveDict = {}

    def __str__(self):
        return f"Moves: {str(self._moveQueue)} | Dict: {str(self._moveDict)} | Parent: {self._parentNode}"

    def __repr__(self):
        return f"_LinkedTreeNode({self._parentNode})"

    def addMove(self, move) -> None:
        self._moveDict[move] = _LinkedTreeNode(self, move)
        pass

    def getNext(self, move) -> str:
        return self._moveDict[move]

    def isMoveIn(self, move) -> bool:
        return move in list(self._moveDict.keys())

    def getParent(self) -> _LinkedTreeNode:
        return self._parentNode

    def getParentMove(self) -> str:
        return self._parentsMove

    def getNumChildren(self) -> int:
        return len(self._moveDict)

    def getAllMoves(self) -> list:
        return list(self._moveDict.keys())

    def getAllChildren(self) -> list:
        return list(self._moveDict.values())

    def dropNode(self, moveName):
        self._moveDict.pop(moveName)

    def isEmpty(self):
        return self.getNumChildren() == 0

    def getNextTop(self):
        if self.isEmpty():
            return None
        return self.getAllMoves()[0]

class LinkedTree():
    """
    LinkedTree is similar to a linked list, but allows for multiple
    (ordered) connections. The order is first by the weight (if
    specified), or otherwise by the order (LIFO).

    Note that 1 is defined as the default and highest weight, and lower
    priorities are higher values (i.e. using a min heap)
    """

    def __init__(self, FEN = None):
        self._root = _LinkedTreeNode()
        self._curNode = self._root
        self._startingMoves = deque()

    def advance(self, move = None) -> str:
        """
        Progresses in the tree; does not add moves into the tree

        Return
        ------
        (str) The move advanced
        """
        if self._curNode.isEmpty():
            raise KeyError("Move not found")

        if move is None:
            move = self._curNode.getAllMoves()[0]
        elif not self._curNode.isMoveIn(move):
            raise KeyError("Move not found")

        self._startingMoves.append(move)

        self._curNode = self._curNode.getNext(move)

        # DEBUG
        # print(self.asLines())
        print(self.toDict())

        return move

    def addMove(self, move):
        """
        Adds the move into the tree. No behavior changes if move exists
        already.
        """
        if not self._curNode.isMoveIn(move):
            self._curNode.addMove(move)

    def backpedal(self) -> str:
        """ Returns the last move played. Returns None if it's at the root"""
        parent = self._curNode.getParent()
        if parent is None:
            return None
        self._curNode = parent
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

    def hasNext(self):
        return self._curNode.getNumChildren() != 0

    def saveTree(self, filename = "user.json"):
        with open(filename, "w+") as f:
            json.dump(self.toDict(), f, sort_keys = True, indent = 4)

    def loadTree(self, filename = "user.json"):
        # Reset tree
        self.resetTree()


        with open(filename, "r+") as f:
            dictTree = json.load(f)

        class DepthMove():
            def __init__(self, dictTree, depth, lastMove):
                self.dictTree = dictTree
                self.depth = depth
                self.lastMove = lastMove

        moveCallStack = deque()
        nodeStack = deque()

        lines = []

        nodeStack.append(DepthMove(dictTree, 0, None))
        while len(nodeStack) != 0:

            curTraversal = nodeStack.pop()

            parentMove = curTraversal.lastMove
            if not parentMove is None:
                moveCallStack.append(parentMove)
                self.addMove(parentMove)
                self.advance(parentMove)

            while curTraversal.depth != 0 and curTraversal.depth - 1 < len(moveCallStack):
                moveCallStack.pop()
                self.backpedal()

            if len(curTraversal.dictTree) == 0:
                lines.append(list(moveCallStack))
            else:
                # Reverse keys to reinforce DFS ordering
                keys = list(curTraversal.dictTree.keys())[::-1]
                for move in keys:
                    nodeStack.append(DepthMove(curTraversal.dictTree[move], curTraversal.depth + 1, move))

        return lines


    # NOTE: This data structure is used instead of directly a dictioanry
    #       since it allows for easier traversal.
    def toDict(self):
        returnDict = {}
        self._toDictHelper(self._root, returnDict)
        return returnDict

    def resetTree(self):
        self._root = _LinkedTreeNode()
        self._curNode = self._root
        self._startingMoves = deque()

    def moveToRoot(self):
        self._curNode = self._root
        self._startingMoves = deque()

    def moveToEnd(self):
        while not self._curNode.isEmpty():
            self.advance(self._curNode.getAllMoves[0])

    def getTopMoves(self):
        cur = self._root
        moves = []
        while not cur.isEmpty():
            moveName = cur.getNextTop()
            moves.append(moveName)
            cur = cur.getNext(moveName)

        return moves

    @staticmethod
    def _toDictHelper(curNode, curDict):
        if curNode.isEmpty():
            return
        for child in curNode.getAllChildren():
            move = child.getParentMove()
            curDict[move] = {}
            LinkedTree._toDictHelper(child, curDict[move])

if __name__ == "__main__":
    a = LinkedTree()
    a.loadTree("user.json")
    print(a.toDict())
    # lines = [
    #     ["e4", "e5", "d3"],
    #     ["e4", "d4", "exd4"],
    # ]

    # for line in lines:
    #     a.populateFromRoot(line)

    # print(a.printTree())
    # print(a.asLines())

    # lines = lines