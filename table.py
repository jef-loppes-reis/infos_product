from os import path
from tkinter import END
import tkinter as tk

import customtkinter as ctk
from pandastable import Table
from pandas import DataFrame
# from pandastable import Table

from main import re


class DisplayTable(ctk.CTkFrame):

    _path_here = path.dirname(__file__)
    with open(path.join(_path_here, 'data/sql/', 'query.sql'), 'r', encoding='utf-8') as fp:
        QUERY = fp.read()

    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        _label = ctk.CTkLabel(self, text='DisplayTable')
        _label.grid(row=10, column=10, padx=10, pady=10, columnspan=4)

        _df = DataFrame([re(self.QUERY, '017708')])

        print(_df)

        self.table_FRAME = ctk.CTkFrame(self)

        self.table = Table(self.table_FRAME,
                           dataframe=_df,
                           showtoolbar=True,
                           showstatusbar=True)

        self.table.grid(row=10, column=10, padx=10, pady=10, columnspan=4)

        self.table_FRAME.grid(row=10, column=10, padx=30, pady=10, columnspan=4,
                              rowspan=10)

        self.table.show()


if __name__ == '__main__':

    root = tk.Tk()

    app = DisplayTable(parent=root)
    app.pack(fill="both", expand=True)

    root.mainloop()
