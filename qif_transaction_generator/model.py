from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, \
 Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import enum

Base = declarative_base()


class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)

    def __repr__(self):
        return "<Status(code = '%s')>" % (self.code)


class StatusEnum(enum.Enum):
    CREATED = 1
    FOUND = 2
    NOT_FOUND = 3
    LOADED = 4


class Receipt(Base):
    __tablename__ = 'receipts'

    id = Column(Integer, primary_key=True)
    fn = Column(String, nullable=False)
    fp = Column(String, nullable=False)
    fd = Column(String, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    total = Column(String, nullable=False)
    raw = Column(Text)
    ecash_total_sum = Column(Integer)
    cash_total_sum = Column(Integer)

    items = relationship('Item')
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    staus = relationship('Status')

    def __repr__(self):
        return "<Receipt(total_sum = '%d', date_time = '%s', status = '%s')>" % (
            self.total_sum, self.date_time, self.status)


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey('receipts.id'))
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    sum = Column(Integer, nullable=False)

    category_id = Column(Integer, ForeignKey('categories.id'))

    def __repr__(self):
        return "<Item(name = '%s', price = '%d', quantity = '%d', sum = '%d')>" % (
            self.name, self.price, self.quantity, self.sum)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)

    def __repr__(self):
        return "<Category(code = '%s')>" % (self.code)


class Dictionary(Base):
    __tablename__ = 'dictionaries'

    id = Column(BigInteger, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    phrase = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)

    category = relationship('Category')
    item = relationship('Item')

    def __repr__(self):
        return "<Dictionary(category = '%s', phrase = '%s', item = '%s', weight = '%s')>" % (
            self.category.code, self.phrase, self.item.name, self.weight)
