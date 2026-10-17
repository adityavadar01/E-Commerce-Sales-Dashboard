CREATE DATABASE ganesh_nashta;

USE ganesh_nashta;

USE ganesh_nashta;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE menu_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    available_quantity INT
);

INSERT INTO menu_items
(item_name, category, price, cost_price, available_quantity)
VALUES
('Poha', 'Breakfast', 40, 20, 50),
('Misal Pav', 'Breakfast', 80, 35, 40),
('Vada Pav', 'Snacks', 25, 12, 100),
('Upma', 'Breakfast', 40, 18, 40),
('Tea', 'Beverage', 15, 5, 150),
('Coffee', 'Beverage', 25, 8, 100),
('Sabudana Khichdi', 'Breakfast', 60, 30, 40);

SELECT * FROM menu_items;