#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse
import configparser

from qif_transaction_generator.app import App
from qif_transaction_generator.config import Config

logger = logging.getLogger('trangen')
config_file = 'config.ini'
config = Config()
app = App()


def add():
    return app.add_receipt(config.args.fn,
                           config.args.fp,
                           config.args.fd,
                           config.args.purchase_date,
                           config.args.total)


def revise():
    return app.revise_receipt()


def sync_accounts():
    return app.sync_accounts()


def enrich():
    return app.enrich_receipts()


def add_phrase():
    return app.add_phrase()


def search_accounts():
    return app.search_accounts(config.args.search_text)

def generate_transaction():
    app.generate_transaction(config.args.output_file)
    config.args.output_file.close()


def parse_arguments():
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

    parser.add_argument('-c',
                        help='Config file (default \'%s\')' % config_file,
                        default=config_file,
                        dest='config',
                        )

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

    # create the parser for the "revise" command
    parser_revise = subparsers.add_parser('revise', aliases=['r'],
                                          description='Revise receipts')
    parser_revise.set_defaults(func=revise)

    # create the parser for the "sync" command
    parser_sync = subparsers.add_parser(
        'sync', aliases=['s'],
        description='Import or sync accounts from GnuCash')
    parser_sync.set_defaults(func=sync_accounts)
    parser_sync.add_argument('account_file',
                             help='path to account file',)

    # create the parser for the "enrich" command
    parser_enrich = subparsers.add_parser(
        'enrich', aliases=['e'], description='Enrich receipts')
    parser_enrich.set_defaults(func=enrich)

    # create the parser for the "add-phrase" command
    add_phrase_parser = subparsers.add_parser(
        'add-phrase', aliases=['b'], description='add phrase to dictionary')
    add_phrase_parser.set_defaults(func=add_phrase)
    add_phrase_parser.add_argument('guid', help='account guid')
    add_phrase_parser.add_argument('phrase')

    # create the parser for the "search-account" command
    search_accounts_parser = subparsers.add_parser(
        'search-accounts', aliases=['sa'], description='search accounts')
    search_accounts_parser.set_defaults(func=search_accounts)
    search_accounts_parser.add_argument('search_text', help='search text')

    # create the parser for the "generate-transaction" command
    generate_transaction_parser = subparsers.add_parser(
        'generate-transaction',
        aliases=['gt'],
        description='generate transaction')
    generate_transaction_parser.add_argument('output_file', type=argparse.FileType('w', encoding='UTF-8'), help='output file')
    generate_transaction_parser.set_defaults(func=generate_transaction)

    args = parser.parse_args()
    return args


def init_config(args):
    config.args = args
    cfg = configparser.ConfigParser()
    cfg.read_file(open(args.config))
    config.login = cfg['fns']['login']
    config.password = cfg['fns']['password']
    config.dbpath = cfg['db']['dbpath']
    config.args = args


def main():
    args = parse_arguments()
    logging.basicConfig(level=args.log_level or logging.INFO)
    if logging.DEBUG == args.log_level:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    # %(asctime)s - %(name)s - %(levelname)s - %(message)s
    # %(name)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s
    logger.debug(args)

    init_config(args)
    app.init()
    args.func()


if __name__ == '__main__':
    main()
