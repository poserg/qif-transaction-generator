"""Widgets."""
import tkinter as tk
from tkinter import ttk


class SearchableTreeview(ttk.Treeview):
    """TreeView with search.

    from from https://stackoverflow.com/questions/17225920/python-tkinter-treeview-searchable
    """

    def __init__(self, *args, **kwargs):
        ttk.Treeview.__init__(self, *args, **kwargs)
        # create the entry on init but does no show it
        self._toSearch = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self._toSearch)

        self.bind("<KeyPress>", self._key_on_tree)
        self._toSearch.trace_variable("w", self._search)
        self.entry.bind("<Return>", self._hide_entry)
        self.entry.bind("<Escape>", self._hide_entry)

    def _key_on_tree(self, event):
        self.entry.place(relx=1, anchor=tk.NE)
        if event.char.isalpha():
            self.entry.insert(tk.END, event.char)
        self.entry.focus_set()

    def _hide_entry(self, event):
        self.entry.delete(0, tk.END)
        self.entry.place_forget()
        self.focus_set()

    def _search(self, *args):
        pattern = self._toSearch.get()
        # avoid search on empty string
        if len(pattern) > 0:
            self.search(pattern)

    def search(self, pattern, item=''):
        children = self.get_children(item)
        for child in children:
            text = self.item(child, 'text')
            if text.lower().startswith(pattern.lower()):
                self.selection_set(child)
                self.see(child)
                return True
            else:
                res = self.search(pattern, child)
                if res:
                    return True
