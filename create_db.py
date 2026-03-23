import sqlite3
from pathlib import Path

DB_PATH = Path("szotanulo.db")


def create_database(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                hungarian TEXT NOT NULL,
                part_of_speech TEXT,
                source TEXT NOT NULL DEFAULT 'wiktionary',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(english, hungarian, part_of_speech)
            );

            CREATE INDEX IF NOT EXISTS idx_dictionary_english
                ON dictionary(english);

            CREATE INDEX IF NOT EXISTS idx_dictionary_hungarian
                ON dictionary(hungarian);

            CREATE INDEX IF NOT EXISTS idx_dictionary_english_lower
                ON dictionary(lower(english));

            CREATE INDEX IF NOT EXISTS idx_dictionary_hungarian_lower
                ON dictionary(lower(hungarian));
            """
        )

        conn.commit()
        print(f"Adatbázis létrehozva: {db_path.resolve()}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()