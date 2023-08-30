from pathlib import Path
import sqlite3

path_db = Path("Chords_DB", "chords.db")


def update_data():
    conn = sqlite3.connect(database=path_db)
    cur = conn.cursor()

    sql_update_query = """UPDATE Songs_Data SET Lyrics_Chords = 'None'"""
    cur.execute(sql_update_query)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    update_data()
