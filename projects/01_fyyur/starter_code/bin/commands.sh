# connect to db
PGPASSWORD=password psql fyyurapp postgres

# db migration for flask with 
    # db = SQLAlchemy(app)
    # migrate = Migrate(app, db)
flask db init
flask db migrate
flask db upgrade
flask db downgrade

# manipulate db directlly
PGPASSWORD=password psql fyyurapp postgres # to login to db
# then use psql command \dt etc to perform sql actions on tables
# insert into venues table
insert into venues(id, name, city, state, address, phone, image_link, facebook_link, genres, seeking_description, seeking_talent, website) 
values (2, 'cityhall', 'sg', 'sg', 'raffles road 123', '987654321', 'https://test_image_link_2', 'https://test_facebook_link_2', 'rock, funk', null, False, 'https://test_website_2');
# insert into artists tables
insert into artists(id, name, city, state, phone, genres, website, image_link, facebook_link, seeking_venue, seeking_description)
values (1, 'zx', 'sg', 'sg', '12345678', 'country, pop', 'https://zx.com', 'https://zx_image_link', 'https://zx_facebook_link_1', True, 'look for a place for me');
values (2, 'sam', 'sg', 'sg', '3335532', ', blues', 'https://sam.com', 'https://sam_image_link', 'https://sam_facebook_link_1', True, 'look for a place for sam');
# insert into shows table
insert into shows(id, start_time, artist_id, venue_id) values(1, '2019-05-21T21:30:00.000Z', 1, 1);
insert into shows(id, start_time, artist_id, venue_id) values(2, '2031-05-21T21:30:00.000Z', 1, 1);
insert into shows(id, start_time, artist_id, venue_id) values(3, '2012-04-22T21:30:00.000Z', 1, 2);
insert into shows(id, start_time, artist_id, venue_id) values(4, '2022-06-22T21:30:00.000Z', 2, 2);

