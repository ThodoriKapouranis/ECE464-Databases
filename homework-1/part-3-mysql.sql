CREATE TABLE repairs (
    rid int PRIMARY KEY,
    bid int,
    day date,
    cost DECIMAL(10,2)
);

-- INSERT INTO repairs values ()
INSERT INTO repairs values (1,101,"2000-10-08",432.2);
INSERT INTO repairs values (2,101,"2000-10-09",50.50);
INSERT INTO repairs values (3,102,"2000-10-10",1002.2);
INSERT INTO repairs values (4,104,"2000-10-11",432.30);
INSERT INTO repairs values (5,108,"2000-10-22",114.12);
INSERT INTO repairs values (6,109,"2000-11-6",774.55);
INSERT INTO repairs values (7,110,"2000-11-14",25.75);
INSERT INTO repairs values (8,112,"2000-11-18",64.77);
INSERT INTO repairs values (9,101,"2000-11-28",1777.20);
INSERT INTO repairs values (10,103,"2000-12-01",543.51);
INSERT INTO repairs values (11,111,"2000-12-04",243.99);
INSERT INTO repairs values (12,101,"2000-12-08",222.99);
INSERT INTO repairs values (13,107,"2000-12-15",432.99);
INSERT INTO repairs values (14,106,"2000-12-20",1050.99);
