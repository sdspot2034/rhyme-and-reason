CREATE TABLE DIM_ARTIST (
    artist_wid INT AUTO_INCREMENT PRIMARY KEY
    , spotify_id VARCHAR(62) NOT NULL UNIQUE
    , artist_name TEXT NOT NULL
    , artist_type VARCHAR(50) NULL
)