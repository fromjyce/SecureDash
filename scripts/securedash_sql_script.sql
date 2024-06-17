CREATE DATABASE securedash;

use securedash;

CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(255) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL,
name VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE packet_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    timestamp DATETIME,
    protocol INT,
    total_fwd_packets INT,
    total_backward_packets BIGINT,
	status VARCHAR(10)
);

SELECT * from packet_data; 

INSERT INTO users (username, password, name, email)
VALUES ("admin", "admin1234#", "Noob", "noob123@gmail.com");

SELECT * from users;

