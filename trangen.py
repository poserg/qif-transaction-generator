#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from qif_transaction_generator.app import add_receipt


def add(args):
    add_receipt(args.fn, args.fp, args.fd, args.purchase_date, args.total)

parser = argparse.ArgumentParser(
    description="Transaction Generator",
)

logging_group = parser.add_mutually_exclusive_group()
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

subparsers = parser.add_subparsers()

# create the parser for the "add" command
parser_add = subparsers.add_parser('add', aliases=['a'],
                                   description='Add new receipt')
parser_add.set_defaults(func=add)
parser_add.add_argument('fn')
parser_add.add_argument('fp')
parser_add.add_argument('fd')
parser_add.add_argument('purchase_date', help='purchase date')
parser_add.add_argument('total', type=int)

args = parser.parse_args()
logging.basicConfig(level=args.log_level or logging.INFO)
logging.debug(args)

args.func(args)
