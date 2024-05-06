-- Table to contain the raw data
CREATE TABLE IF NOT EXISTS scraped_fffrent_listings (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    ran_at TIMESTAMP WITH TIME ZONE,
    data JSONB
);

-- Table to contain the actual processed 444rent listings
CREATE TABLE IF NOT EXISTS fffrent_listings (
    id VARCHAR(64) PRIMARY KEY,
    unit INTEGER
    area VARCHAR
    available_date TIMESTAMP
    management VARCHAR
    den BOOLEAN
    leasing_info JSONB
    description_info TEXT
    building_info JSONB
    suite_info JSONB
    FOREIGN KEY (id) REFERENCES listings(id) ON DELETE CASCADE

);
