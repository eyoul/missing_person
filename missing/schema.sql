DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  finder_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  finder_location TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  finder_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  missed_name TEXT NOT NULL,
  since TEXT NOT Null,
  missing_from TEXT NOT NULL,
  gender TEXT NOT NULL,
  age TEXT NOT NULL,
  call_on TEXT NOT NULL,
  addtional_info TEXT NOT NULL,
  photo_url TEXT NOT NULL,
  FOREIGN KEY (finder_id) REFERENCES user (id)
);
