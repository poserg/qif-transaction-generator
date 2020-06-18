import platform
from os import environ
import tkinter as tk
from tkinter import ttk
from . import views as v
from . import models as m
from .. config import Config
from .. import models as db_m
from .. dao import DBUtil

class Application(tk.Tk):
    """Application root window"""
    config_dirs = {
        'Linux': environ.get('$XDG_CONFIG_HOME', '~/.config'),
        'freebsd7': environ.get('$XDG_CONFIG_HOME', '~/.config'),
        'Darwin': '~/Library/Application Support',
        'Windows': '~/AppData/Local'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("QIF transaction generator")
        self.resizable(width=False, height=False)

        self.inserted_rows = []
        self.updated_rows = []

        # settings model & settings
        config_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.SettingsModel(path=config_dir)
        #self.load_settings()
        #self.set_font()
        #self.settings['font size'].trace('w', self.set_font)

        style = ttk.Style()
        #theme = self.settings.get('theme').get()
        #if theme in style.theme_names():
        #    style.theme_use(theme)
        
        self.callbacks = {
            'on_open_record': self.open_record
        }
        
        self.config = Config()
        self.config.dbpath = 'sqlite:///db_prod_copy.sqlite'
        self.db_util = DBUtil(self.config.dbpath)

        column_defs = {
            '#0': {'label': 'Row', 'anchor': tk.W},
            'date': {'label': 'Date', 'width': 150, 'stretch': True},
            'status': {'label': 'Status', 'width': 200},
            'total': {'label': 'Total', 'width': 150, 'anchor': tk.E}
        }

        # The data record list
        self.recordlist = v.RecordList(
            self,
            self.callbacks,
            column_defs,
            inserted=self.inserted_rows,
            updated=self.updated_rows
        )
        self.recordlist.grid(row=1, padx=10, sticky='NSEW')
        self.populate_recordlist()

    def populate_recordlist(self):
        receipts = self.db_util.get_receipts_by_status_with_items_and_accounts(
            [db_m.StatusEnum.DONE.value, db_m.StatusEnum.CREATED_FROM_FILE.value], 100)
        rows = []
        for r in receipts:
            d = {'date': r.purchase_date, 'status': r.status.code}
            d['total'] = '%.2f' % (r.total/100.0) if r.total else r.total
            rows.append(d)
        self.recordlist.populate(rows)
        
    def open_record(self, rowkey):
        print(rowkey)