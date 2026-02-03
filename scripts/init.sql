-- Task Management Database Initialization Script
-- This script creates the tasks table with all required fields

CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') NOT NULL DEFAULT 'pending',
    priority INT NOT NULL DEFAULT 3,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_title (title),
    INDEX idx_created_at (created_at),
    CONSTRAINT chk_priority CHECK (priority >= 1 AND priority <= 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
