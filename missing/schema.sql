DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS role;

CREATE TABLE role (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT NOT NULL
);

INSERT INTO role (name, description) VALUES ('admin', 'Administrator');
INSERT INTO role (name, description) VALUES ('user', 'Regular User');

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  finder_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  finder_location TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role_id INTEGER NOT NULL,
  FOREIGN KEY (role_id) REFERENCES role (id)
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  finder_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  missed_name TEXT NOT NULL,
  since TEXT NOT NULL,
  missing_from TEXT NOT NULL,
  gender TEXT NOT NULL,
  age TEXT NOT NULL,
  call_on TEXT NOT NULL,
  additional_info TEXT NOT NULL,
  photo_url TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  FOREIGN KEY (finder_id) REFERENCES user (id)
);
