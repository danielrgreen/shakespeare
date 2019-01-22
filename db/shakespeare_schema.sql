CREATE TABLE IF NOT EXISTS words (
    word VARCHAR NOT NULL,
    datamuse_rhymes_populated INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (word)
);

CREATE TABLE IF NOT EXISTS datamuse_rhymes (
    word1 VARCHAR NOT NULL,
    word2 VARCHAR NOT NULL,
    num_syllables INTEGER NOT NULL,
    score INTEGER NOT NULL,
    PRIMARY KEY (word1, word2),
    FOREIGN KEY (word1) REFERENCES words (word),
    FOREIGN KEY (word2) REFERENCES words (word)
);