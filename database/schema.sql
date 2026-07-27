-- ColorVibe database schema (MySQL)
-- Run this once to create the database and tables:
--   mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS colorvibe
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE colorvibe;

-- ------------------------------------------------------------------
-- users: registered accounts. Passwords are stored as salted hashes
-- (werkzeug.security), never in plain text.
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(120) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------
-- palettes: saved color palettes belonging to a user.
-- colors is stored as a JSON array of hex strings, e.g.
--   ["#1B1B1F", "#E3A542", "#2F6F63", "#C4573F", "#F7F4EE"]
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS palettes (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(80) NOT NULL,
    colors      JSON NOT NULL,
    harmony     VARCHAR(30) NOT NULL DEFAULT 'random',
    is_public   TINYINT(1) NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_palettes_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_palettes_user_id ON palettes(user_id);
CREATE INDEX idx_palettes_public ON palettes(is_public);
