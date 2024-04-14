/* The main listings table */
CREATE TABLE IF NOT EXISTS fourfourfourrent_listings (
    id VARCHAR(64) PRIMARY KEY,
    available BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    management VARCHAR,
    url VARCHAR,
    address VARCHAR,
    building VARCHAR,
    unit VARCHAR,
    location VARCHAR,
    square_feet FLOAT,
    available_date VARCHAR,
    price FLOAT,
    rooms VARCHAR,
    leasing_info TEXT,
    description_info TEXT,
    building_info TEXT,
    suite_info TEXT
);

/* The intermediate listings the scraped entries get dumped into */
CREATE TABLE IF NOT EXISTS scraped_fourfourfourrent_listings (
    id VARCHAR(64) PRIMARY KEY,
    available BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    management VARCHAR,
    url VARCHAR,
    address VARCHAR,
    building VARCHAR,
    unit VARCHAR,
    location VARCHAR,
    square_feet FLOAT,
    available_date VARCHAR,
    price FLOAT,
    rooms VARCHAR,
    leasing_info TEXT,
    description_info TEXT,
    building_info TEXT,
    suite_info TEXT
);

/* The table that holds changes make to listings in the main listings table */
CREATE TABLE IF NOT EXISTS fourfourfourrent_listings_histories (
    id SERIAL PRIMARY KEY,
    existing_record_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed VARCHAR,
    original TEXT,
    updated TEXT,
    FOREIGN KEY (existing_record_id) REFERENCES fourfourfourrent_listings(id) ON DELETE CASCADE
);
