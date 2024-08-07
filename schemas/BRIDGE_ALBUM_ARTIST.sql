CREATE TABLE BRIDGE_ALBUM_ARTIST (
    album_artist_map_wid INT AUTO_INCREMENT PRIMARY KEY
    , album_wid INT DEFAULT NULL
    , artist_wid INT DEFAULT NULL
    , UNIQUE KEY album_artist_map (album_wid, artist_wid)
)