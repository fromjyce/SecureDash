CREATE DATABASE securedash;

use securedash;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE users ADD COLUMN name VARCHAR(255) NOT NULL;
ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL UNIQUE;

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

