#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from qif_transaction_generator.app import add_receipt

parser = argparse.ArgumentParser(
    description="Transaction Generator",
)
logging_group = parser.add_mutually_exclusive_group()
parser.add_argument('fn')
parser.add_argument('fp')
parser.add_argument('fd')
parser.add_argument('purchase_date', help='purchase date')
parser.add_argument('total')
logging_group.add_argument('-v',
                           '--verbose',
                           help='Verbose (debug) logging',
                           action='store_const',
                           const=logging.DEBUG,
                           dest='log_level')
logging_group.add_argument('-q',
                           '--quiet',
                           help='Silent mode, only log warnings',
                           action='store_const',
                           const=logging.WARN,
                           dest='log_level')


args = parser.parse_args()
logging.basicConfig(level=args.log_level or logging.INFO)
logging.debug(args)
add_receipt(args.fn, args.fp, args.fd, args.purchase_date, args.total)
