postgresql://postgres:postgres@localhost:5432/postgres
postgresql://postgres:postgres@localhost:5432/dvdrental
postgresql://user:pass@localhost:5432/my_db

sqlite:///test.db

mysql://root:@localhost:3306

### Postgres -

select * from accounts;
insert into accounts values(2, 'abcd');

### SQLite

insert into Persons VALUES (4, 'tom', 35);
select * from Persons;

### MySQL

select * from Persons;
insert into Persons VALUES (1, 'Poojary', 'Mithil');

CREATE TABLE Persons (
    PersonID int,
    LastName varchar(255),
    FirstName varchar(255)
);

### MariaDB
