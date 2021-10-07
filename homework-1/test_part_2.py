# Part 2 | Base ORM

# Represent the sailors and boats schema using an ORM - I prefer SQLAlchemy but students have the freedom to choose their own language and ORM. Show that it is fully functional by writing tests with a testing framework using the data from part 1 (writing the queries for the questions in Part 1) - I prefer pytest but students are have the freedom to choose their own testing framework.

# Manually write the correct/expected results for each Q in part 1 for the testing 

# Run this file with 
# py -m pytest ./test_part_1.py 
# to ensure that we're running with python3
from decimal import Decimal
from typing import AsyncGenerator
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.elements import or_
from sqlalchemy.sql.expression import bindparam, select
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.selectable import Select, subquery
from sqlalchemy.sql.sqltypes import DECIMAL, DateTime, String
from sqlalchemy.orm import backref, relationship, Query
from sqlalchemy import create_engine, text, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

# Connect the engine to the existing mysql db
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
    
# pytest will go through every function that starts with a "test_" prefix.
# These functions end with an assertion and will be how pytest knows if
# something has failed or passed.

# Each boat, number of times reserved (non-zero)
def test_q1(): 
    expected = [
                (101,'Interlake',2),
                (102,'Interlake',3),
                (103,'Clipper',3),
                (104,'Clipper',5),
                (105,'Marine',3),
                (106,'Marine',3),
                (109,'Driftwood',4),
                (112,'Sooney',1),
                (110,'Klapser',3),
                (107,'Marine',1),
                (111,'Sooney',1),
                (108,'Driftwood',1),
                ]

    orm_query = s.query(Boats.bid, Boats.bname, func.count(Reservations.bid))\
                    .filter(Reservations.bid == Boats.bid)\
                    .group_by(Boats.bid)
    
    assert expected == orm_query.all()

# List sailors that rsvd every read boat
# This is probably wrong.... Fix it

def test_q2():
    expected = []

    # Subquery for a column of all Red Boat Bids
    rbb = s.query(Boats.bid)\
            .filter(Boats.color=='red')\
            .subquery()

    # Scalar value for total number of red boats
    red_count = s.query(func.count(Boats.bid))\
                    .filter(Boats.color=='red')\
                    .scalar()

    orm_query = s.query(Sailors.sid, Sailors.sname)\
                    .filter(Sailors.sid==Reservations.sid, Reservations.bid==rbb.c.bid)\
                    .group_by(Reservations.bid)\
                    .having( func.count(Reservations.bid)==red_count)
    
    assert expected==orm_query.all()

def test_q3():
    expected = [
        (23, 'emilio'),
        (24, 'scruntus'),
        (35, 'figaro'),
        (61, 'ossola'),
        (62, 'shaun')
    ]

    # Subquery for sailors that have rsvd Green or Blue boats
    gob_sailors = s.query(Reservations.sid)\
                    .filter(Reservations.bid==Boats.bid, or_(Boats.color=='green', Boats.color=='blue'))
    
    # Convert this to a list of ints, because otherwise its tuples.
    # Tuples dont work with Table.col.in_([...]) filtering
    gob_sailors = [ id_tuple[0] for id_tuple in gob_sailors.all() ]
    

    main_query = s.query(Sailors.sid, Sailors.sname)\
                    .filter(~Reservations.sid.in_(gob_sailors), Sailors.sid==Reservations.sid)\
                    .distinct()

    assert expected == main_query.all()

def test_q4():
    expected = [(104, 'Clipper', 5)]

    # Scalar for most reservations
    most_rsvs = s.query(func.count(Reservations.bid))\
                    .group_by(Reservations.bid)\
                    .order_by(func.count(Reservations.bid))\
                    .all()[-1][0]

    main_query = s.query(Reservations.bid, Boats.bname, func.count(Reservations.bid))\
                    .filter(Reservations.bid==Boats.bid)\
                    .group_by(Reservations.bid)\
                    .having(func.count(Reservations.bid)==most_rsvs)
    
    assert expected == main_query.all()

def test_q5():
    expected = [
        (29,'brutus'),
        (32,'andy'),
        (58,'rusty'),
        (60,'jit'),
        (71,'zorba'),
        (74,'horatio'),
        (85,'art'),
        (90,'vin'),
        (95,'bob')
    ]

    # subquery for Sailors that have reserved at least one red boat 
    red_sailors = s.query(Sailors.sid)\
                    .filter(Sailors.sid==Reservations.sid, Reservations.bid==Boats.bid, Boats.color=='red')\
                    .distinct()
    
    red_sailors = [id_tuple[0] for id_tuple in red_sailors]

    main_query = s.query(Sailors.sid, Sailors.sname)\
                    .filter(~Sailors.sid.in_(red_sailors))\
                    .order_by(Sailors.sid)
    
    assert expected == main_query.all()


def test_q6():
    expected = 35

    main_query = s.query(func.avg(Sailors.age))\
                    .filter(Sailors.rating==10)

    assert expected == main_query.all()[0][0] # get the scalar value

def test_q7():
    expected = [
        (1, 24, 'scruntus', 33),
        (1, 29, 'brutus', 33),
        (3, 85, 'art', 25),
        (3, 89, 'dye', 25),
        (7, 61, 'ossola', 16),
        (7, 64, 'horatio', 16),
        (8, 32, 'andy', 25),
        (8, 59, 'stum', 25),
        (9, 74, 'horatio', 25),
        (9, 88, 'dan', 25),
        (10, 58, 'rusty', 35),
        (10, 60, 'jit', 35),
        (10, 62, 'shaun', 35),
        (10, 71, 'zorba', 35)
    ]

    # Subquery for getting the youngest age of a sailor grouped by the rating
    yng_per = s.query( Sailors.rating, func.min(Sailors.age).label('min'))\
                .group_by(Sailors.rating)\
                .subquery()

    main_query = s.query(Sailors.rating, Sailors.sid, Sailors.sname, Sailors.age)\
                    .filter(Sailors.rating==yng_per.c.rating, Sailors.age==yng_per.c.min)\
                    .order_by(Sailors.rating)

    assert expected == main_query.all()

def test_q8():
    expected = [
        ('Interlake', 101, 'dusting', 22, 1),
        ('Interlake', 101, 'horatio', 64, 1),
        ('Interlake', 102, 'dusting', 22, 1),
        ('Interlake', 102, 'lubber', 31, 1),
        ('Interlake', 102, 'horatio', 64, 1),
        ('Clipper', 103, 'dusting', 22, 1),
        ('Clipper', 103, 'lubber', 31, 1),
        ('Clipper', 103, 'horatio', 74, 1),
        ('Clipper', 104, 'dusting', 22, 1),
        ('Clipper', 104, 'emilio', 23, 1),
        ('Clipper', 104, 'scruntus', 24, 1),
        ('Clipper', 104, 'lubber', 31, 1),
        ('Clipper', 104, 'figaro', 35, 1),
        ('Marine', 105, 'emilio', 23, 1),
        ('Marine', 105, 'figaro', 35, 1),
        ('Marine', 105, 'stum', 59, 1),
        ('Marine', 106, 'jit', 60, 2),
        ('Marine', 107, 'dan', 88, 1),
        ('Driftwood', 108, 'dye', 89, 1),
        ('Driftwood', 109, 'stum', 59, 1),
        ('Driftwood', 109, 'jit', 60, 1),
        ('Driftwood', 109, 'dye', 89, 1),
        ('Driftwood', 109, 'vin', 90, 1),
        ('Klapser', 110, 'dan', 88, 2),
        ('Sooney', 111, 'dan', 88, 1),
        ('Sooney', 112, 'ossola', 61, 1)
    ]