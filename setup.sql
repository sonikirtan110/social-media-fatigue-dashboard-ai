CREATE DATABASE IF NOT EXISTS social;
USE social;

CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    age INT NOT NULL,
    social_media_time FLOAT NOT NULL,
    screen_time FLOAT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    prediction FLOAT NOT NULL,
    category VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
