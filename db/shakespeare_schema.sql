CREATE TABLE IF NOT EXISTS words (
    word VARCHAR NOT NULL,
    PRIMARY KEY (word)
);

CREATE TABLE IF NOT EXISTS rhymes (
    word1 VARCHAR NOT NULL,
    word2 VARCHAR NOT NULL,
    PRIMARY KEY (word1, word2),
    FOREIGN KEY (word1) REFERENCES words (word),
    FOREIGN KEY (word2) REFERENCES words (word)
);