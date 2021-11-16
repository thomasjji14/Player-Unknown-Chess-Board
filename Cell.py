from tkinter import *
from FileManager import getFile
class Cell():
    def __init__(self):
        self.text = "-"
        self.image = None
        self.record = None
    
    def isEmpty(self):
        return self.text == "-"