CREATE TABLE Spotify_db.DIM_USER (
    user_wid INT,
    display_name STRING,
    type STRING,
    country STRING,
    product STRING,
    spotify_url STRING,
    profile_pic STRING
);


CREATE TABLE Spotify_db.BRIDGE_ALBUM_ARTIST (
    album_artist_map_wid INT
    , album_wid INT
    , artist_wid INT
);

CREATE TABLE Spotify_db.DIM_ALBUM (
    album_wid INT 
    , album_id STRING
    , album_type STRING 
    , album_name STRING
    , release_date STRING
    , release_date_precision STRING
    , total_tracks INT
    , cover_image_url STRING
);

CREATE TABLE Spotify_db.DIM_ARTIST (
    artist_wid INT
    , spotify_id STRING
    , artist_name STRING
    , artist_type STRING
);

CREATE TABLE Spotify_db.DIM_SONG (
    song_wid INT
    , song_id STRING
    , album_wid INT
    , disc_number INT
    , duration_ms BIGINT
    , explicit BOOLEAN
    , is_local BOOLEAN
    , name STRING
    , preview_url STRING
    , track_number INT
    , type STRING
    , isrc_id STRING
);

CREATE TABLE Spotify_db.FACT_PLAY (
    play_wid INT
    , song_wid INT
    , played_at TIMESTAMP 
    , context_playlist STRING
)