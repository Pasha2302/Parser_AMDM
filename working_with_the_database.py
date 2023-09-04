# import os
from pathlib import Path
import sqlite3

# import reading_writing_files as rwf
import colorama  # pip install colorama
from colorama import Fore, Style
colorama.init()

path_db = Path("Chords_DB", "chords.db")


def create_table_songs_and_add_data(data_list, name_table='Songs_Data'):
    count_link = 0
    conn = sqlite3.connect(database=path_db)
    print(f'{Fore.GREEN}Запись ссылок песен в базу {name_table}...{Style.RESET_ALL}')

    cur = conn.cursor()
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {name_table}(
        url_song TEXT PRIMARY KEY,
        Title TEXT,
        Performer TEXT,
        Lyrics_Chords TEXT,
        Link_to_Video TEXT,
        Url_Performers TEXT
        );
        """)
    conn.commit()
    for data in data_list:
        for data_song in data['data_songs']:
            try:
                cur.execute(f"INSERT INTO {name_table} VALUES (?,?,?,?,?,?)", (
                    data_song['url_song'], data_song['title'], data['name'], 'None', 'None', data['url']))
                count_link += 1
            except sqlite3.IntegrityError:
                pass
                # print(f"{Fore.BLUE}Эти данные уже существуют в базе...{Style.RESET_ALL}\n")
                # print(data)
                # print('==' * 40)

            except Exception as err0:
                print(data.keys())
                raise TypeError(err0)

    print(f'{Fore.GREEN}Количество ссылок на песни добавлено в базу {name_table}: {count_link}...{Style.RESET_ALL}')
    conn.commit()
    conn.close()


def add_data_lyrics_chords(data_list, name_table):
    conn = sqlite3.connect(database=path_db)
    print(f'{Fore.GREEN}Запись аккордов и ссылок youtube в базу...{Style.RESET_ALL}')

    cur = conn.cursor()

    for data in data_list:
        sql_update_query = f"""UPDATE {name_table} SET Lyrics_Chords = ?, Link_to_Video = ? WHERE url_song LIKE ?"""
        data = (data['lyric_chord'], data['link_to_video'], data['url_song'])
        cur.execute(sql_update_query, data)

    conn.commit()
    conn.close()


def replace_tags_in_lyrics(name_table):
    conn = sqlite3.connect(database=path_db)
    cur = conn.cursor()

    print(f'{Fore.GREEN}Идет проверка тегов в текстах песен. Таблица: {name_table}.{Style.RESET_ALL}')
    query = f"UPDATE {name_table} SET Lyrics_Chords = REPLACE(REPLACE(Lyrics_Chords, '<span>', '<b>'), '</span>', '</b>')"
    cur.execute(query)

    conn.commit()
    conn.close()


def get_data_db_lyrics_chords_is_none(name_table):
    conn = sqlite3.connect(database=path_db)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {name_table} WHERE Lyrics_Chords = 'None'")
    result = cur.fetchall()

    conn.close()
    return result
