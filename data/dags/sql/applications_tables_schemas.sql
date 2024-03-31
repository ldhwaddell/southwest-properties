CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(64) PRIMARY KEY,
    active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    url VARCHAR,
    title TEXT,
    summary TEXT,
    last_updated TIMESTAMP WITH TIME ZONE,
    update_notice TEXT,
    request TEXT,
    proposal TEXT,
    process TEXT,
    status TEXT,
    documents_submitted_for_evaluation TEXT,
    contact_info TEXT
);

CREATE TABLE IF NOT EXISTS application_histories (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed VARCHAR,
    original TEXT,
    updated TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);
