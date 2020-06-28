#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from qif_transaction_generator.ui.application import Application


logging.basicConfig(level=logging.DEBUG)

app = Application()
app.mainloop()
