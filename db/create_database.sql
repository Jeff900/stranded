CREATE TABLE IF NOT EXISTS island (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS area (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	island_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	FOREIGN KEY(id) REFERENCES island(id)
);

CREATE TABLE IF NOT EXISTS story (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt (
	island INTEGER NOT NULL,
	area INTEGER NOT NULL,
	story_type TEXT NOT NULL,
	story INTEGER NOT NULL,
	id INTEGER NOT NULL,
	person INTEGER DEFAULT 0,
	prompt TEXT NOT NULL,
	has_answers INTEGER DEFAULT 0,
	following INTEGER
);

CREATE TABLE IF NOT EXISTS item (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	descr TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS answer (
	prompt_id INTEGER NOT NULL,
	num INTEGER NOT NULL,
	answer TEXT NOT NULL,
	following INTEGER DEFAULT 0,
	item_id INTEGER DEFAULT 0,
	FOREIGN KEY(prompt_id) REFERENCES prompt(id),
	FOREIGN KEY(item_id) REFERENCES item(id)
);


CREATE TABLE IF NOT EXISTS inventory (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	item_id INTEGER	NOT NULL,
	FOREIGN KEY(item_id) REFERENCES item(id)
);
