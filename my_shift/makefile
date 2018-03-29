eway.db:
	sqlite3 my_shift.db 'CREATE TABLE settings ( dayreq INTEGER(4) )'
	sqlite3 my_shift.db 'CREATE TABLE users ( name VARCHAR(64) primary key, id INTEGER(4) unique not null )'
	sqlite3 my_shift.db 'CREATE TABLE clock_data ( user_id INTEGER(4) not null, in_out INTEGER(1) not null, time INTEGER(6) not null, unique ( user_id, time ) )'
