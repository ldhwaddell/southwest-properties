-- Table to contain the actual processed listings
CREATE TABLE IF NOT EXISTS listings (
    id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    url VARCHAR,
    source VARCHAR,
    address VARCHAR,
    building VARCHAR,
    price FLOAT,
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_feet FLOAT
);

-- Table to keep track of which listings are active
CREATE TABLE IF NOT EXISTS active_listings (
    id VARCHAR(64) PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES listings(id) ON DELETE CASCADE
);

-- Table to keep track of which listings are inactive
CREATE TABLE IF NOT EXISTS archived_listings (
    id VARCHAR(64) PRIMARY KEY,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES listings(id) ON DELETE CASCADE
);

-- Table to keep track of changes in listings
CREATE TABLE IF NOT EXISTS listings_histories (
    id SERIAL PRIMARY KEY,
    existing_record_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed VARCHAR,
    original TEXT,
    updated TEXT,
    FOREIGN KEY (existing_record_id) REFERENCES listings(id) ON DELETE CASCADE
);
