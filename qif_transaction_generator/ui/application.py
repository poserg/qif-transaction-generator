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
    """Application root window."""

    config_dirs = {
        'Linux': environ.get('$XDG_CONFIG_HOME', '~/.config'),
        'freebsd7': environ.get('$XDG_CONFIG_HOME', '~/.config'),
        'Darwin': '~/Library/Application Support',
        'Windows': '~/AppData/Local'
    }

    def _build_receiptlist(self):
        column_defs = {'#0': {'label': 'Row', 'anchor': tk.W},
                       'date': {'label': 'Date', 'width': 150},
                       'status': {'label': 'Status', 'width': 200},
                       'total': {'label': 'Total', 'width': 150,
                                 'anchor': tk.E}
                       }
        # The data receipt list
        self.receiptlist = v.RecordList(self,
                                        self.callbacks,
                                        column_defs,
                                        inserted=self.inserted_rows,
                                        updated=self.updated_rows)
        self.receiptlist.grid(row=1, padx=10, sticky='NSEW')
        self._populate_receiptlist()

    def _build_itemlist(self):
        column_defs = {'#0': {'label': 'Row', 'anchor': tk.W},
                       'name': {'label': 'Name', 'width': 300, 'anchor': tk.W},
                       'price': {'label': 'Price', 'width': 150,
                                 'anchor': tk.E},
                       'quantity': {'label': 'Quantity', 'width': 150,
                                    'anchor': tk.E},
                       'sum': {'label': 'Sum', 'width': 150, 'anchor': tk.E},
                       'account': {'label': 'Account', 'width': 400,
                                   'stretch': True, 'anchor': tk.W}}
        self.itemlist = v.RecordList(
            self,
            {'on_open_record': self._open_item},
            column_defs,
            inserted=self.inserted_rows,
            updated=self.updated_rows)
        self.itemlist.grid(row=2, padx=10, sticky='NSEW')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("QIF transaction generator")
        self.resizable(width=False, height=False)

        self.inserted_rows = []
        self.updated_rows = []

        # settings model & settings
        config_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.SettingsModel(path=config_dir)
        # self.load_settings()
        # self.set_font()
        # self.settings['font size'].trace('w', self.set_font)

        style = ttk.Style()
        # theme = self.settings.get('theme').get()
        # if theme in style.theme_names():
        #    style.theme_use(theme)

        self.callbacks = {
            'on_open_record': self.open_receipt
        }

        self.config = Config()
        self.config.dbpath = 'sqlite:///db_prod_copy.sqlite'
        self.db_util = DBUtil(self.config.dbpath)

        self._build_add_button()
        self._build_receiptlist()


    def _convert_int_to_money_str(self, value):
        return '%.2f' % (value / 100.0) if value else value

    def _populate_receiptlist(self):
        receipts = self.db_util.get_receipts_by_status_with_items_and_accounts(
            [db_m.StatusEnum.DONE.value,
             db_m.StatusEnum.CREATED_FROM_FILE.value], 100)
        rows = []
        for r in receipts:
            d = {'id': r.id, 'date': r.purchase_date, 'status': r.status.code,
                 'total': self._convert_int_to_money_str(r.total)}
            rows.append(d)
        self.receiptlist.populate(rows)

    def _open_receipt(self, row):
        self._populate_itemlist(row['id'])

    def _populate_itemlist(self, receipt_id):
        items = self.db_util.get_items_by_receipt_id(receipt_id)
        rows = []
        for i in items:
            d = {'id': i.id, 'name': i.name,
                 'price': self._convert_int_to_money_str(i.price),
                 'quantity': i.quantity,
                 'sum': self._convert_int_to_money_str(i.sum),
                 'account':
                 i.account.full_name if i.account else i.account_guid}
            rows.append(d)
        self.itemlist.populate(rows)

    def _open_item(self, row):
        print ('item = %s' % row)
