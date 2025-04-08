DROP TABLE IF EXISTS goals;

CREATE TABLE goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  deadline TEXT NOT NULL,
  category TEXT NOT NULL
);

DROP TABLE IF EXISTS goals_completed;

CREATE TABLE goals_completed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  deadline TEXT NOT NULL,
  completion_date TEXT NOT NULL,
  completed_category TEXT NOT NULL
);
