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
    status VARCHAR(10),
    flow_duration INT,
    protocol INT,
    total_fwd_packets INT,
    total_backward_packets INT
);

SELECT * from packet_data; 

ALTER table packet_data DROP flow_duration;

