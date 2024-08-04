CREATE TABLE DIM_SONG (
    song_wid INT AUTO_INCREMENT PRIMARY KEY
    , song_id VARCHAR(62) NOT NULL UNIQUE
    , album_wid INT
    , disc_number INT
    , duration_ms LONG NOT NULL
    , explicit BOOLEAN
    , is_local BOOLEAN
    , name TEXT NOT NULL
    , preview_url TEXT
    , track_number INT
    , type VARCHAR(50)
    , isrc_id VARCHAR(100)
)