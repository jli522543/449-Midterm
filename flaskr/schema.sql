DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS product;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  price FLOAT NOT NULL
);

INSERT INTO product (name, price) VALUES ('keyboard', 100.4);
INSERT INTO product (name, price) VALUES ('mouse', 50.2);

