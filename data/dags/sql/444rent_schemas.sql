-- Table to contain the raw data
CREATE TABLE IF NOT EXISTS scraped_fffrent_listings (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    ran_at TIMESTAMP WITH TIME ZONE,
    data JSONB
);

-- Table to contain the actual processed applications
-- CREATE TABLE IF NOT EXISTS applications (
--     id VARCHAR(64) PRIMARY KEY,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     url VARCHAR,
--     title TEXT,
--     summary TEXT,
--     last_updated TIMESTAMP WITH TIME ZONE,
--     update_notice TEXT,
--     request TEXT,
--     proposal TEXT,
--     process TEXT,
--     status TEXT,
--     documents_submitted_for_evaluation TEXT,
--     contact_info JSONB
-- );

-- -- Table to keep track of which applications are active
-- CREATE TABLE IF NOT EXISTS active_applications (
--     id VARCHAR(64) PRIMARY KEY,
--     FOREIGN KEY (id) REFERENCES applications(id) ON DELETE CASCADE
-- );

-- -- Table to keep track of which applications are inactive
-- CREATE TABLE IF NOT EXISTS archived_applications (
--     id VARCHAR(64) PRIMARY KEY,
--     archived_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (id) REFERENCES applications(id) ON DELETE CASCADE
-- );

-- -- Table to keep track of changes in applications
-- CREATE TABLE IF NOT EXISTS application_histories (
--     id SERIAL PRIMARY KEY,
--     existing_record_id VARCHAR(64) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     changed VARCHAR,
--     original TEXT,
--     updated TEXT,
--     FOREIGN KEY (existing_record_id) REFERENCES applications(id) ON DELETE CASCADE
-- );
