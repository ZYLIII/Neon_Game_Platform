CREATE TABLE `user` (
    `userid` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `contact_number` VARCHAR(20) NOT NULL
);

CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    revenue DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    downloads INT NOT NULL DEFAULT 0
);

INSERT INTO games (name, category, price, revenue, downloads) VALUES
('game01', 'Free', 0.00, 500.00, 1000),
('game02', 'Free', 0.00, 300.00, 800),
('game03', 'Free', 0.00, 200.00, 600),
('game04', 'Free', 0.00, 100.00, 400),
('game05', 'Free', 0.00, 50.00, 200),
('game06', 'Paid', 1.99, 600.00, 300),
('game07', 'Paid', 2.99, 900.00, 300),
('game08', 'Paid', 3.99, 1200.00, 300),
('game09', 'Paid', 4.99, 1500.00, 300),
('game10', 'Paid', 5.99, 1800.00, 300);

-- Add details column to the games table
ALTER TABLE games ADD COLUMN details TEXT;

-- Update the games with example details
UPDATE games SET details='game01 detail' WHERE game_id=1;
UPDATE games SET details='game02 detail' WHERE game_id=2;
UPDATE games SET details='game03 detail' WHERE game_id=3;
UPDATE games SET details='game04 detail' WHERE game_id=4;
UPDATE games SET details='game05 detail' WHERE game_id=5;
UPDATE games SET details='game06 detail' WHERE game_id=6;
UPDATE games SET details='game07 detail' WHERE game_id=7;
UPDATE games SET details='game08 detail' WHERE game_id=8;
UPDATE games SET details='game09 detail' WHERE game_id=9;
UPDATE games SET details='game10 detail' WHERE game_id=10;


CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    game_id INT,
    FOREIGN KEY (user_id) REFERENCES user(userid),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE user_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    game_id INT,
    FOREIGN KEY (user_id) REFERENCES user(userid),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

ALTER TABLE `user` ADD COLUMN wallet_balance DECIMAL(10, 2) DEFAULT 0.00;
