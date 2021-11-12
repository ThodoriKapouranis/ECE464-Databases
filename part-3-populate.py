from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine("mysql+pymysql://root:123@localhost/sailors", echo=False)

Session = sessionmaker(bind = engine)
session = Session()

""""
CREATE TABLE repairs (
    rid int,
    bid int,
    day date,
    cost DECIMAL(10,2),
        PRIMARY KEY (rid, bid)
);
"""

repairs = [
    (1,101,"2000-10-08",432.20),
]

session.commit