postgresql://postgres:postgres@localhost:5432/postgres
postgresql://postgres:postgres@localhost:5432/dvdrental
sqlite:///test.db
sqlite:///C:\Users\mithi\projects\test.db
mysql://mysql:mysql@localhost/testDB
mysql://admin:mysql@localhost/testDB
postgresql://jctsfujq:7oXX0GQxPfB_bidhtWBY0rEbISobWwLr@arjuna.db.elephantsql.com/jctsfujq

### Postgres -

select * from accounts;
insert into accounts values(2, 'abcd');

### SQLite

CREATE TABLE persons (
	contact_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL
);
insert into Persons VALUES (4, 'tom', 'nom');
select * from Persons;

### MySQL

select * from persons;
insert into persons values (1, 'mithil');
delete from persons;

CREATE TABLE Persons (
    PersonID int,
    LastName varchar(255),
    FirstName varchar(255)
);

mysqld
\sql
\connect root@localhost
