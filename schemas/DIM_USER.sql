CREATE TABLE DIM_USER (
    user_wid INT AUTO_INCREMENT PRIMARY KEY,
    display_name VARCHAR(255),
    type VARCHAR(50),
    country VARCHAR(50),
    product VARCHAR(50),
    spotify_url TEXT,
    profile_pic TEXT
)