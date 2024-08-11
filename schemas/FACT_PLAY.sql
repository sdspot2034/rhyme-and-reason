CREATE TABLE FACT_PLAY (
    play_wid INT AUTO_INCREMENT PRIMARY KEY
    , song_wid INT NOT NULL
    , played_at TIMESTAMP NOT NULL 
    , context_playlist TEXT NOT NULL
)