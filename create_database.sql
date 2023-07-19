CREATE TABLE user(
    id INTEGER PRIMARY KEY
);

CREATE TABLE birthday_reminder(
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    name TEXT NOT NULL,
    reminder INTEGER
);

ALTER TABLE birthday_reminder
ADD COLUMN user_id INTEGER REFERENCES user(id);

