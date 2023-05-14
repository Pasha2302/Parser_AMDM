import reading_writing_files as rwf
from pathlib import Path
import re
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

aio_sess = acs.AiohttpSession()


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
    check_index_main = 0
    count_slice = 50

    if not os.path.isfile('Performers_Data.json'):
        await hp.start_get_html_performers(session)
        pup.get_url_perf()

    await url_songs.start_get_url_songs(session)
    # -------------------------------------------------------------------

    request_data = working_db.get_data_db_lyrics_chords_is_none()
    if not request_data:
        print("Все Аккорды Найдены...")
        return 0

    count_total_data = len(request_data)
    print("\n\n<<================= Идут запросы на получение Аккордов... =================>>")
    for data in split_list(request_data, count_slice):
        res, exception_check = await create_a_task_request(request_data=data)

        if exception_check:
            print('\nОшибки:')
            print(exception_check)
            break

        if res:
            print('\nДанные получены')
            working_db.add_data_lyrics_chords(res)

        check_index_main += len(data)
        print(f"Выполнено {check_index_main} из {count_total_data}")
        print('==' * 40)
        break

    await session.close()
    time.sleep(.25)


# Html_Performers
# Сhords_DB
if __name__ == '__main__':
    if not os.path.exists('Html_Performers'):
        os.makedirs('Html_Performers')
    if not os.path.exists('Сhords_DB'):
        os.makedirs('Сhords_DB')

    loop = asyncio.new_event_loop()
    session: aiohttp.client.ClientSession = loop.run_until_complete(aio_sess.create_session())

    try:
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(close_func())
        loop.close()
        print("\n\n<<================= Программа Завершена... =================>>")
