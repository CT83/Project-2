postgresql://postgres:postgres@localhost:5432/postgres
postgresql://user:pass@localhost:5432/my_db

### Postgres -

select role_name from roles where role_id = 4;
select * from accounts;
insert into roles (role_id, role_name) VALUES (9, 'voice actor');

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
