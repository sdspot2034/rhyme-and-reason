CREATE TABLE DIM_ALBUM (
    album_wid INT AUTO_INCREMENT PRIMARY KEY
    , album_id VARCHAR(62) NOT NULL UNIQUE
    , album_type VARCHAR(20) NOT NULL 
    , album_name TEXT NOT NULL
    , release_date DATE
    , release_date_precision VARCHAR(20) 
    , total_tracks INT
    , cover_image_url TEXT
)

ALTER TABLE DIM_ALBUM
MODIFY COLUMN release_date VARCHAR(50)