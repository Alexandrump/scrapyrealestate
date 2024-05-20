-- init.sql

CREATE DATABASE IF NOT EXISTS scrapyrealestate;

USE scrapyrealestate;

CREATE TABLE IF NOT EXISTS sr_connections (
    id VARCHAR(255) PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    group_name VARCHAR(255),
    time_refresh INT,
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    urls TEXT,
    so VARCHAR(255),
    host_name VARCHAR(255),
    connections INT,
    first_connection DATETIME,
    last_connection DATETIME
);

CREATE TABLE IF NOT EXISTS sr_flats (
    id INT PRIMARY KEY,
    price DECIMAL(10, 2),
    m2 DECIMAL(10, 2),
    rooms INT,
    floor VARCHAR(255),
    town VARCHAR(255),
    neighbour VARCHAR(255),
    street VARCHAR(255),
    number VARCHAR(255),
    title VARCHAR(255),
    href TEXT,
    type VARCHAR(255),
    site VARCHAR(255),
    online BOOLEAN,
    datetime DATETIME
);
