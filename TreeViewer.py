from tkinter import *

# class TreeViewer(Frame):

#     def __init__(self, base):
#         super().__init__(base, borderwidth = 1, bg = "gray")
#         self._base = base
#         self._textLabels = []
#         self._size = 0

#     def _add(self, moveText):
#         newEntry = _TextLabel(self)
#         newEntry.text.set(moveText)
#         self._textLabels.append(newEntry)
#         newEntry.label.grid(row = int(self._size/2), column = self._size % 2, sticky = EW)

#         newEntry.label.bind("<Button-1>", lambda event : print(moveText))

#         self._size += 1

#     def fill(self, moveList):
#         self._size = 0
#         for item in self._textLabels:
#             item.label.grid_forget()

#         self._textLabels = []
#         for move in moveList:
#             self._add(move)

class TreeViewer(Frame):

    def __init__(self, base):
        super().__init__(base, borderwidth = 1, bg = "gray")
        self._base = base
        self._rows = []
        self._size = 0

    def _add(self, moveText):
        rowNum = self._size // 2
        if self._size % 2 == 0:
            a = _MoveRow(self)
            self._rows.append(a)
            curRow = self._rows[rowNum]
            curRow.setNumber(rowNum)
            curRow.grid(row = rowNum, sticky = EW)

            curRow.setLeft(moveText)
        else:
            curRow = self._rows[rowNum]
            curRow.setRight(moveText)

        self._size += 1

    def fill(self, moveList):
        self._size = 0
        for item in self._rows:
            item.grid_forget()

        self._rows = []
        for move in moveList:
            self._add(move)

class _MoveRow(Frame):
    def __init__(self, base):
        super().__init__(base, borderwidth = 1, bg = "gray")
        self._number = _TextLabel(self, 3)
        self._number.grid(row = 0, column = 0, sticky = EW)
        self._leftMove = _TextLabel(self, 6)
        self._leftMove.grid(row = 0, column = 1, sticky = EW)
        self._rightMove = _TextLabel(self, 6)
        self._rightMove.grid(row = 0, column = 2, sticky = EW)

    def setNumber(self, text):
        self._number.setText(text)

    def setLeft(self, text):
        self._leftMove.setText(text)

    def setRight(self, text):
        self._rightMove.setText(text)


class _TextLabel(Label):
    def __init__(self, base, width, text = ""):
        self._text = StringVar()
        if not text is None:
            self._text.set(text)

        super().__init__(base, textvariable = self._text, width = width)

    def setText(self, text):
        self._text.set(text)

if __name__ == "__main__":
    base = Tk()

    base.title("Chess")

    board = TreeViewer(base)
    board.grid(row = 0, column = 0)

    board.fill(["e1", "e2", "e3", "e4"])

    base.mainloop()