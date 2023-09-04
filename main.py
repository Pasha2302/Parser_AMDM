import os
import time
import asyncio
import aiohttp

import html_performers as hp
import aiohttp_create_session as acs
import pars_url_performers as pup
import url_songs
import data_chords_block as dcb
import working_with_the_database as working_db
import reading_writing_files as rwf
from chord_check import start_chord_check

aio_sess = acs.AiohttpSession()
path_intermediate_state = 'intermediate_state.txt'

name_table_songs = 'Songs_Data'
name_table_main_categories = 'Songs_Data_Main_Categories'


async def close_func():
    await session.close()
    await asyncio.sleep(.35)


def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def create_a_task_request(request_data):
    data_list = []
    tasks_list = []
    exception_check = []

    for data in request_data:
        tasks_list.append(dcb.get_chords(session, data_song=data))

    res = await asyncio.gather(*tasks_list, return_exceptions=True)

    for data_validation in res:
        if not isinstance(data_validation, dict):
            exception_check.append(data_validation)
        else:
            data_list.append(data_validation)
    return data_list, exception_check


async def main():
    if not os.path.isfile(path_intermediate_state):
        intermediate_state = '0'
        rwf.save_txt_data(data_txt='0', path_file=path_intermediate_state)
    else:
        intermediate_state = rwf.download_txt_data(path_file=path_intermediate_state).strip()

    count_slice = 25
    print(f"{intermediate_state=}")
    # -------------------------------------------------------------------
    # Запустить цикл сбора ссылок на исполнителей и их песни, с последующей проверкой ссылок песен на наличие в базе.
    # Если ссылки на песню нет в базе, она добавляется.
    if not os.path.isfile('Performers_Data.json'):
        await hp.start_get_html_performers(session)
        pup.get_url_perf()

    if intermediate_state == '0':
        await url_songs.start_get_url_songs(session)

    intermediate_state = '1'
    rwf.save_txt_data(data_txt=intermediate_state, path_file=path_intermediate_state)

    # ----------------------------------------------------------------------------------------------

    for name_t in [name_table_main_categories, name_table_songs]:
        check_index_main = 0
        request_data = working_db.get_data_db_lyrics_chords_is_none(name_table=name_t)
        if not request_data:
            print(f"\nПо таблице [{name_t}] Все Аккорды Найдены ...")
            continue

        count_total_data = len(request_data)
        print(f"\n\n<<================= Таблица {name_t}. Идут запросы на получение Аккордов... =================>>")
        for data in split_list(request_data, count_slice):
            res, exception_check = await create_a_task_request(request_data=data)

            if exception_check:
                print('\nОшибки:')
                print(exception_check)
                break

            if res:
                print('\nДанные получены')
                working_db.add_data_lyrics_chords(res, name_table=name_t)

            check_index_main += len(data)
            print(f"Выполнено {check_index_main} из {count_total_data}")
            print('==' * 40)

    # =================================================================================================================
    if os.path.isfile('Performers_Data.json'):
        os.remove('Performers_Data.json')
    intermediate_state = '0'
    rwf.save_txt_data(data_txt=intermediate_state, path_file=path_intermediate_state)
    await session.close()
    time.sleep(.25)

    try:
        start_chord_check()
    except Exception as error_check_chord:
        print(f"\n\n !!! [109 Main] error_check_chord:\n{error_check_chord}")

    for name_table in [name_table_songs, name_table_main_categories]:
        working_db.replace_tags_in_lyrics(name_table)

    print("\n\n<<================= Программа Завершена... =================>>")


if __name__ == '__main__':
    # pip freeze > requirements.txt
    # https://amdm.ru/
    if not os.path.exists('Html_Performers'):
        os.makedirs('Html_Performers')
    if not os.path.exists('Chords_DB'):
        os.makedirs('Chords_DB')

    loop = asyncio.new_event_loop()
    session: aiohttp.client.ClientSession = loop.run_until_complete(aio_sess.create_session())

    try:
        pass
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(close_func())
        loop.close()
        time.sleep(.46)
