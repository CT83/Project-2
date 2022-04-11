postgresql://postgres:postgres@localhost:5432/postgres
postgresql://postgres:postgres@localhost:5432/dvdrental
sqlite:///test.db
sqlite:///C:\Users\mithi\projects\test.db
mysql://mysql:mysql@localhost/testDB
mysql://admin:mysql@localhost/testDB


### Postgres -

select * from accounts;
insert into accounts values(2, 'abcd');

### SQLite

insert into Persons VALUES (4, 'tom', 35);
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

