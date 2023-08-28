create table if not exists users(
    id integer primary key autoincrement, name, email unique, password, is_admin default false, is_banned default false
);

create view if not exists goodboys as select * from users where is_banned = false;
create view if not exists admins as select * from users where is_admin = true;

create table if not exists venues(
    id integer primary key autoincrement, name, description, image, city, address
);

create table if not exists shows(
    id integer primary key autoincrement, name, description, image, tags
);

create table if not exists allocations(
    id integer primary key autoincrement, venue_id, show_id, time, capacity,
    base_price, max_multiplier,
    foreign key(venue_id) references venues(id), foreign key(show_id) references shows(id)
);

create view if not exists bookable_allocations as select * from allocations where time > current_timestamp;

create table if not exists bookings(
    id integer primary key autoincrement, allocation_id, user_id, 
    time default current_timestamp, quantity, gross_price, review, rating
);

-- indices
create index if not exists venues_city on venues(city);
create index if not exists fk_allocations_venues on allocations(venue_id);
create index if not exists fk_allocations_shows on allocations(show_id);

-- fts
create virtual table if not exists venues_fts using fts5(
    name, description, address, city,
    content=venues, content_rowid=id, tokenize="trigram"
);
create virtual table if not exists shows_fts using fts5(
    name, description, tags,
    content=shows, content_rowid=id, tokenize="trigram"
);

create trigger if not exists venues_ai after insert on venues
begin
    insert into venues_fts(name, description, address)
    values (new.name, new.description, new.address);
end;

create trigger if not exists venues_ad after delete on venues
begin
    insert into venues_fts(venues_fts, name, description, address)
    values('delete', old.name, old.description, old.address);
end;

create trigger if not exists venues_au after update on venues
begin
    insert into venues_fts(venues_fts, name, description, address)
    values('delete', old.name, old.description, old.address);

    insert into venues_fts(name, description, address)
    values (new.name, new.description, new.address);
end;

create trigger if not exists shows_ai after insert on shows
begin
    insert into shows_fts(name, description, tags)
    values (new.name, new.description, new.tags);
end;

create trigger if not exists shows_ad after delete on shows
begin
    insert into shows_fts(shows_fts, name, description, tags)
    values('delete', old.name, old.description, old.tags);
end;

create trigger if not exists shows_au after update on shows
begin
    insert into shows_fts(shows_fts, name, description, tags)
    values('delete', old.name, old.description, old.tags);

    insert into shows_fts(name, description, tags)
    values (new.name, new.description, new.tags);
end;