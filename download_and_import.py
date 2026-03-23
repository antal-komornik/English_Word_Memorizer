import gzip
import json
import sqlite3
import urllib.request
from pathlib import Path

DB_PATH = Path("szotanulo.db")
DOWNLOAD_URL = "https://kaikki.org/dictionary/raw-wiktextract-data.jsonl.gz"
GZ_PATH = Path("raw-wiktextract-data.jsonl.gz")


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def ensure_db_exists(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
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
    finally:
        conn.close()


def download_file(url: str, target_path: Path) -> None:
    if target_path.exists():
        print(f"A fájl már létezik, letöltés kihagyva: {target_path}")
        return

    print("Letöltés indul...")
    with urllib.request.urlopen(url) as response, open(target_path, "wb") as out_file:
        chunk_size = 1024 * 1024
        downloaded = 0

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            print(f"\rLetöltve: {downloaded / (1024 * 1024):.1f} MB", end="")

    print("\nLetöltés kész.")


def extract_hungarian_translations(entry: dict) -> set[tuple[str, str | None]]:
    results: set[tuple[str, str | None]] = set()

    word = entry.get("word")
    if not isinstance(word, str) or not word.strip():
        return results

    lang_code = entry.get("lang_code")
    lang = entry.get("lang")

    # Csak angol szócikkekből dolgozunk
    if lang_code not in ("en", None) and lang != "English":
        return results

    pos = entry.get("pos")

    # Top-level translations
    translations = entry.get("translations", [])
    if isinstance(translations, list):
        for tr in translations:
            if not isinstance(tr, dict):
                continue
            if tr.get("lang_code") == "hu":
                hu_word = tr.get("word")
                if isinstance(hu_word, str) and hu_word.strip():
                    results.add((normalize_text(hu_word), pos))

    # Sense-level translations
    senses = entry.get("senses", [])
    if isinstance(senses, list):
        for sense in senses:
            if not isinstance(sense, dict):
                continue

            sense_translations = sense.get("translations", [])
            if not isinstance(sense_translations, list):
                continue

            for tr in sense_translations:
                if not isinstance(tr, dict):
                    continue
                if tr.get("lang_code") == "hu":
                    hu_word = tr.get("word")
                    if isinstance(hu_word, str) and hu_word.strip():
                        results.add((normalize_text(hu_word), pos))

    return results


def import_data(db_path: Path, gz_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    total_lines = 0
    inserted = 0
    invalid_json = 0

    try:
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            batch = []

            for line in f:
                total_lines += 1
                line = line.strip()

                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    invalid_json += 1
                    continue

                english_word = entry.get("word")
                if not isinstance(english_word, str) or not english_word.strip():
                    continue

                english_word = normalize_text(english_word)
                translations = extract_hungarian_translations(entry)

                for hungarian_word, pos in translations:
                    batch.append((english_word, hungarian_word, pos, "wiktionary"))

                if len(batch) >= 5000:
                    cursor.executemany(
                        """
                        INSERT OR IGNORE INTO dictionary
                            (english, hungarian, part_of_speech, source)
                        VALUES (?, ?, ?, ?)
                        """,
                        batch,
                    )
                    inserted += cursor.rowcount if cursor.rowcount != -1 else 0
                    conn.commit()
                    batch.clear()

                    if total_lines % 50000 < 5000:
                        print(f"Feldolgozott sorok: {total_lines}")

            if batch:
                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO dictionary
                        (english, hungarian, part_of_speech, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    batch,
                )
                inserted += cursor.rowcount if cursor.rowcount != -1 else 0
                conn.commit()

    finally:
        conn.close()

    print("Import kész.")
    print(f"Feldolgozott sorok: {total_lines}")
    print(f"Hibás JSON sorok: {invalid_json}")
    print(f"Beszúrt rekordok (becsült): {inserted}")


def main() -> None:
    ensure_db_exists(DB_PATH)
    download_file(DOWNLOAD_URL, GZ_PATH)
    import_data(DB_PATH, GZ_PATH)


if __name__ == "__main__":
    main()