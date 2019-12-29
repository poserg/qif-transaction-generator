from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, \
    Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import enum

Base = declarative_base()


class Reference:

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)

    def __repr__(self):
        return "<%s(id = '%d', code = '%s')>" % (
            self.__tablename__,
            self.id,
            self.code)


class Status(Base, Reference):
    __tablename__ = 'statuses'


class StatusEnum(enum.Enum):
    CREATED = 1
    FOUND = 2
    NOT_FOUND = 3
    LOADED = 4
    DONE = 5
    CREATED_FROM_FILE = 6


class FnsReceipt(Base):
    __tablename__ = 'fns_receipts'

    id = Column(Integer, primary_key=True)
    fn = Column(String)
    fp = Column(String, nullable=False)
    fd = Column(String, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    total = Column(String, nullable=False)

    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    status = relationship('Status')

    def __repr__(self):
        return "<Receipt(id = %s fn = %s fp = %s fd = %s purchase_date = '%s', total = %s, status = %s)>" % (
                self.id,
            self.fn,
            self.fp,
            self.fd,
            self.purchase_date,
            self.total,
            self.status_id if self.status is None else self.status.code)


class Receipt(Base):
    __tablename__ = 'receipts'

    id = Column(Integer, primary_key=True)
    purchase_date = Column(DateTime)

    # для простоты используется целое - нужно делить на 100 при выгрузке
    total = Column(Integer)

    raw = Column(Text, nullable=False)
    ecash_total_sum = Column(Integer)
    cash_total_sum = Column(Integer)

    items = relationship('Item')
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    status = relationship('Status')

    fns_receipt_id = Column(Integer, ForeignKey('fns_receipts.id'))
    fns_receipt = relationship('FnsReceipt')

    def __repr__(self):
        return "<Receipt(id = %s purchase_date = '%s', total = %s, status = %s)>" % (
            self.id,
            self.purchase_date,
            self.total,
            self.status_id if self.status is None else self.status.code)


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey('receipts.id'))
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    sum = Column(Integer, nullable=False)

    account_guid = Column(String(32), ForeignKey('accounts.guid'))
    account = relationship('Account')

    def __repr__(self):
        return "<Item(name = '%s', price = '%d', quantity = '%d', sum = '%d', account_guid = '%s')>" % (
            self.name, self.price, self.quantity, self.sum, self.account_guid)


class Dictionary(Base):
    __tablename__ = 'dictionaries'

    id = Column(BigInteger, primary_key=True)
    account_guid = Column(String(32), ForeignKey('accounts.guid'), nullable=False)
    phrase = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)

    account = relationship('Account')

    def __repr__(self):
        return "<Dictionary(account_guid = '%s', phrase = '%s', weight = '%s')>" % (
            self.account_guid, self.phrase, self.weight)


class AccountType(Base, Reference):
    __tablename__ = 'account_types'


class AccountTypeEnum(enum.Enum):
    ASSET = 1
    BANK = 2
    CASH = 3
    CREDIT = 4
    EQUITY = 5
    EXPENSE = 6
    INCOME = 7
    LIABILITY = 8
    MUTUAL = 9
    ROOT = 10
    STOCK = 11
    TRADING = 12


class Account(Base):
    __tablename__ = 'accounts'

    guid = Column(String(32), primary_key=True)
    name = Column(String, nullable=False)
    full_name = Column(String)
    description = Column(String)
    parent_guid = Column(String(32), ForeignKey("accounts.guid"))
    account_type_id = Column(
        Integer, ForeignKey("account_types.id"), nullable=False)
    type = relationship('AccountType')

    def __repr__(self):
        return "<%s(guid = %s, name = %s, type = , parent_guid = %s, full_name = %s>" % (
            self.__tablename__, self.guid, self.name,
            #self.account_type_id
            #if self.type is None else self.type.value,
            self.parent_guid,
            self.full_name)

    def equals(self, other):
        if isinstance(other, Account):
            return self.guid == other.guid and \
                self.name == other.name and \
                self.description == other.description and \
                self.parent_guid == other.parent_guid and \
                self.account_type_id == other.account_type_id and \
                self.full_name == other.full_name
        return False

    def update_value(self, o):
        self.name = o.name
        self.description = o.description
        self.parent_guid = o.parent_guid
        self.account_type_id = o.account_type_id
        self.full_name = o.full_name
