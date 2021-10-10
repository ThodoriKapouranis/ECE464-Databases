# Part 3 

# Students are hired as software consults for a small business boat rental that is experiencing a heavy influx of tourism in its area. This increase is hindering operations of the mom/pop shop that uses paper/pen for most tasks. Students should explore “inefficient processes” the business may have and propose ideas for improvements - in the form of a brief write-up. 

# Expand the codebase from part 2 to include a few jobs, reports, integrity checks, and/or other processes that would be beneficial to the business. Use the data provided in part 1 and expand it to conduct tests and show functionality.

# I want to add:
# Boat repair tracker
# Employee table + dep + salary

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import extract, true
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DECIMAL, DateTime, Integer, String


engine = create_engine("mysql+pymysql://root:123@localhost/sailors", echo=False)
conn = engine.connect()

Session = sessionmaker(bind = engine)
s = Session()

# Set up the table relations
Base = declarative_base()

class Sailors(Base):
    __tablename__ = 'sailors'

    sid     = Column(Integer, primary_key=True)
    sname   = Column(String)
    rating  = Column(Integer)
    age     = Column(Integer)

    def __repr__(self):
        return "(Sailor(id=%s, name='%s', rating=%s))" % (self.sid, self.sname, self.age)

class Boats(Base):
    __tablename__ = 'boats'

    bid = Column(Integer, primary_key=True)
    bname = Column(String)
    color = Column(String)
    length = Column(Integer)

    Reservation = relationship(
                                'Reservations', 
                                backref=backref('boat', cascade='delete'))

    def __repr__(self):
        return "<Boat(id=%s, name='%s', color=%s)>" % (self.bid, self.bname, self.color)

class Reservations(Base):
    __tablename__ = 'reserves'
    __table_args__ = (PrimaryKeyConstraint('sid', 'bid', 'day'), {})

    sid = Column(Integer, ForeignKey('sailors.sid'))
    bid = Column(Integer, ForeignKey('boats.bid'))
    day = Column(DateTime)

    sailor = relationship('Sailors')

    def __repr__(self):
        return "<Reservations(sid=%s, bid=%s, day=%s)>" % (self.sid, self.bid, self.day)

class Repairs(Base):
    __tablename__ = 'repairs'

    rid = Column(Integer, primary_key=True)
    bid = Column(Integer, ForeignKey('boats.bid'))
    day = Column(DateTime)
    cost = Column(DECIMAL)

    def __repr__(self):
        return "<Repairs(rid=%s, bid=%s, day=%s, cost=%s)>" % (self.sid, self.bid, self.day, self.cost)


all_repairs = s.query(Repairs.rid, Repairs.bid, Repairs.day, Repairs.cost)

# Get the boat with the most repair costs
def test_q1():
    expected = [
        (101, Decimal('2482.89'))
    ]

    total_cost = s.query(Repairs.bid, func.sum(Repairs.cost).label("cost"))\
                    .group_by(Repairs.bid)\
                    .subquery()
    
    max_cost = s.query(func.max(total_cost.c.cost)).scalar_subquery()

    orm_query = s.query(total_cost.c.bid, total_cost.c.cost)\
                    .filter(total_cost.c.cost==max_cost)

    assert expected == orm_query.all()

# Get boats that have not needed repairs
def test_q2():
    expected = [(105,)]

    all_boats = s.query(Boats.bid).distinct().subquery()
    boats_repaired = s.query(Repairs.bid).distinct()
    boats_repaired = [bid_tuple[0] for bid_tuple in boats_repaired]

    orm_query = s.query(Boats.bid)\
                    .filter(~Boats.bid.in_(boats_repaired))

    assert expected == orm_query.all()

# Get total repair costs for the October 2000
def test_q3():
    expected = [(Decimal('2031.32'),)]
    orm_query = s.query(func.sum(Repairs.cost))\
                    .filter(
                        extract('year', Repairs.day)==2000, 
                        extract('month', Repairs.day)==10)

    assert expected == orm_query.all()

test_q3()
