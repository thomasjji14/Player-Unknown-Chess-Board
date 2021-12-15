from tkinter import *

class TreeViewer(Frame):

    def __init__(self, base):
        super().__init__(base, borderwidth = 1, bg = "gray")
        self._base = base
        self._textLabels = []
        self._size = 0

    def _add(self, moveText):
        newEntry = _TextLabel(self)
        newEntry.text.set(moveText)
        self._textLabels.append(newEntry)
        newEntry.label.grid(row = int(self._size/2), column = self._size % 2, sticky = EW)
        
        newEntry.label.bind("<Button-1>", lambda event : print(moveText))

        self._size += 1

    def fill(self, moveList):
        self._size = 0
        for item in self._textLabels:
            item.label.grid_forget()

        self._textLabels = []
        for move in moveList:
            self._add(move)

# records structure only
class _TextLabel():
    def __init__(self, base):
        self.text = StringVar()
        self.label = Label(base, textvariable = self.text, width = 6)

if __name__ == "main":
    base = Tk()

    base.title("Chess")

    board = TreeViewer(base)
    board._fill(["e4gong", "e5dfa", "e6dfdsa", "e7dafsdf"])

    board.grid(row = 0, column = 0)

# a = Frame(base)

# t = StringVar()
# t.set('dong')
# label = Label(a, textvariable = t)
# label.grid(row = 0, column = 0)

# t2 = StringVar()
# t2.set('dong')
# label2 = Label(a)
# label2.grid(row = 1, column = 0)
# label2.configure(textvariable = t2)

# a.grid(row = 0, column = 0)

# t = StringVar()
# t.set('dong')
# label = Label(base, textvariable = t)
# label.grid(row = 0, column = 0)

    base.mainloop()