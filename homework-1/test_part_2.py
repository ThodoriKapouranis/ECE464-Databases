# Part 2 | Base ORM

# Represent the sailors and boats schema using an ORM - I prefer SQLAlchemy but students have the freedom to choose their own language and ORM. Show that it is fully functional by writing tests with a testing framework using the data from part 1 (writing the queries for the questions in Part 1) - I prefer pytest but students are have the freedom to choose their own testing framework.

# Manually write the correct/expected results for each Q in part 1 for the testing 

# Run this file with 
# py -m pytest ./test_part_1.py 
# to ensure that we're running with python3
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime, String
from sqlalchemy.orm import backref, relationship, Query
from sqlalchemy import create_engine, text, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

# Connect the engine to the existing mysql db
engine = create_engine("mysql+pymysql://root:123@localhost/sailors", echo=False)

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


def test_q2():
    expected = []

def test_q3():
    expected = [
        (23, 'emilio'),
        (24, 'scruntus'),
        (35, 'figaro'),
        (61, 'ossola'),
        (62, 'shaun')
    ]

def test_q4():
    expected = [(104, 'Clipper', 5)]

def test_q5():
    expected = [
        (95,'bob'),
        (90,'vin'),
        (85,'art'),
        (74,'horati'),
        (71,'zorba'),
        (60,'jit'),
        (58,'rusty'),
        (32,'andy'),
        (29,'brutus')
    ]


def test_q6():
    expected = [35]

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
        (0, 58, 'rusty', 35),
        (0, 60, 'jit', 35),
        (0, 62, 'shaun', 35),
        (0, 71, 'zorba', 35)
    ]

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