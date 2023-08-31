import time
import datetime
from pathlib import Path
import sqlite3
import re
import reading_writing_files as rwf

import shutil
from tqdm import tqdm
import colorama  # pip install colorama
from colorama import Fore, Style

colorama.init()

path_db = Path("Chords_DB", "chords.db")

re_pattern_cords = re.compile(r"(?<=<span>).*?(?=</span>)")
good_chords = [gch.strip() for gch in rwf.download_txt_data(path_file='goldoutput.txt').split('\n') if gch]
count_checked = 0
index_url = 0
index_chord = 3
name_table = ''

conn: sqlite3.Connection | None = None
cur: sqlite3.Cursor | None = None


def get_formatted_datetime():
    now = datetime.datetime.now()
    formatted_date = now.strftime("%d-%m-%Y_%H:%M:%S")
    return formatted_date


def get_data_db():
    try:
        cur.execute(f"ALTER TABLE {name_table} ADD COLUMN Check_Chords TEXT DEFAULT '';")
    except sqlite3.OperationalError:
        pass
    cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS url_song_index ON {name_table} (url_song);")
    conn.commit()
    cur.execute(f"SELECT * FROM {name_table} WHERE Check_Chords = '' AND Lyrics_Chords != 'None';")


def delete_song(value_to_search):
    delete_query = f"DELETE FROM {name_table} WHERE url_song = ?"
    data = (value_to_search,)
    cur.execute(delete_query, data)


def add_check_chord(*update_data_check_chord):
    sql_update_query = f"""UPDATE {name_table} SET Check_Chords = ? WHERE url_song = ?"""
    data = (update_data_check_chord[0], update_data_check_chord[1])
    cur.execute(sql_update_query, data)


def entry_check(row: tuple[str]):  # row - кортеж строк из базы данных sqlite3
    global count_checked
    check_bad_chords = 0
    chords_songs = re.findall(re_pattern_cords, row[index_chord])

    if not chords_songs:
        delete_song(row[index_url])
        count_checked += 1
        return 0

    for chord_song in chords_songs:
        if chord_song.strip() not in good_chords:
            delete_song(row[index_url])
            check_bad_chords = 1
            break
    if check_bad_chords == 0:
        add_check_chord('Checked', row[index_url])
        count_checked += 1
        if count_checked % 5000 == 0:
            conn.commit()


def start_chord_check():
    global conn
    global cur
    global name_table

    current_date = get_formatted_datetime()
    target_db_path = Path("Chords_DB", f"chords_copy_{current_date}.db")
    # Создание копии файла базы данных
    shutil.copyfile(path_db, target_db_path)

    conn = sqlite3.connect(database=path_db)
    cur = conn.cursor()

    tables = ['Songs_Data_Main_Categories', 'Songs_Data']
    print(f"\nКол-во Хороших Аккордов: {len(good_chords)}")

    for i in tables:
        name_table = i
        print(f"\n<<===== Проверка таблицы: {name_table} =====>>\n")

        try:
            cur.execute(f"ALTER TABLE {name_table} DROP COLUMN Check_Chords;")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        get_data_db()
        data_songs = tuple(cur.fetchall())
        count_total_data_db = len(data_songs)

        for row_db in tqdm(
                data_songs,
                total=count_total_data_db,
                desc=f"{Fore.GREEN}[Таблица: <{name_table}>] Удаление песен с 'плохими' аккордами...{Style.RESET_ALL}"
        ):
            entry_check(row=row_db)

        conn.commit()

    time.sleep(2)
    cur.close()
    conn.close()
    time.sleep(1)


if __name__ == '__main__':
    start_chord_check()
