import tkinter as tk
from tkinter import ttk

class RecordList(tk.Frame):
    """Display for CSV file contents 
    From https://github.com/PacktPublishing/Python-GUI-Programming-with-Tkinter/blob/master/Chapter11/ABQ_Data_Entry/abq_data_entry/views.py
    """

    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self, parent, callbacks, column_defs,
                 inserted, updated,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.column_defs = column_defs
        self.inserted = inserted
        self.updated = updated
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create treeview
        self.treeview = ttk.Treeview(
            self,
            columns=list(self.column_defs.keys())[1:],
            selectmode='browse'
        )
        # hide first column
        self.treeview.config(show='headings')

        # configure scrollbar for the treeview
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.grid(row=0, column=0, sticky='NSEW')
        self.scrollbar.grid(row=0, column=1, sticky='NSW')

        # Configure treeview columns
        for name, definition in self.column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)
            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(name, anchor=anchor, minwidth=minwidth,
                                 width=width, stretch=stretch)

        # configure row tags
        self.treeview.tag_configure('inserted', background='lightgreen')
        self.treeview.tag_configure('updated', background='lightblue')

        # Bind double-clicks
        self.treeview.bind('<<TreeviewOpen>>', self.on_open_record)

    def populate(self, rows):
        """Clear the treeview and write the supplied data rows to it."""

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rownum, rowdata in enumerate(rows):
            values = [rowdata[key] for key in valuekeys]
            self.treeview.insert('', 'end', iid=str(rownum), text=str(rownum), values=values)

        if len(rows) > 0:
            firstrow = self.treeview.identify_row(0)
            self.treeview.focus_set()
            self.treeview.selection_set(firstrow)
            self.treeview.focus(firstrow)

    def on_open_record(self, *args):
        selected_id = self.treeview.selection()[0]
        self.callbacks['on_open_record'](selected_id.split('|'))
