/* The main listings table */
CREATE TABLE IF NOT EXISTS apartments_dot_com_listings (
    id VARCHAR(7) PRIMARY KEY,
    available BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    url VARCHAR,
    address VARCHAR,
    building VARCHAR,
    monthly_rent VARCHAR,
    bedrooms VARCHAR,
    bathrooms VARCHAR,
    square_feet FLOAT,
    about TEXT,
    description TEXT,
    amenities TEXT,
    fees TEXT
);

/* The intermediate listings the scraped entries get dumped into */
CREATE TABLE IF NOT EXISTS scraped_apartments_dot_com_listings (
    id VARCHAR(7) PRIMARY KEY,
    available BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    url VARCHAR,
    address VARCHAR,
    building VARCHAR,
    monthly_rent VARCHAR,
    bedrooms VARCHAR,
    bathrooms VARCHAR,
    square_feet FLOAT,
    about TEXT,
    description TEXT,
    amenities TEXT,
    fees TEXT
);

/* The table that holds changes make to listings in the main listings table */
CREATE TABLE IF NOT EXISTS apartments_dot_com_listings_histories (
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(7) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed VARCHAR,
    original TEXT,
    updated TEXT,
    FOREIGN KEY (listing_id) REFERENCES apartments_dot_com_listings(id) ON DELETE CASCADE
);
