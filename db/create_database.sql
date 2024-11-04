CREATE TABLE prompt (
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

CREATE TABLE answer (
	prompt_id INTEGER NOT NULL,
	num INTEGER NOT NULL,
	answer TEXT NOT NULL,
	following INTEGER DEFAULT 0,
	FOREIGN KEY(prompt_id) REFERENCES prompt(id)
);
