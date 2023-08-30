import aiohttp
import os
import reading_writing_files as rwf
import asyncio
import headers_cookies as hc
# from pathlib import Path
from bs4 import BeautifulSoup as BS
from random import randint

from filtering_repeated_song_names import get_unique_songs
import working_with_the_database as working_db


def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def get_url_songs(session: aiohttp.client.ClientSession, performer_data):
    tags_url_song = None
    count_err = 0
    count_no_block_songs = 0
    performer_data['data_songs'] = []

    while True:
        try:
            response = await session.get(url=performer_data['url'], cookies=hc.cookies, headers=hc.headers)
            response_text = await response.text()

            soup = BS(response_text, 'lxml', multi_valued_attributes=None)
            check_tag = soup.find("body").text

            if 'Too Many Requests..' in check_tag or '502 Bad Gateway' in check_tag:
                rwf.save_txt_data(data_txt=response_text, path_file='Erorr_Html_2.html')
                await asyncio.sleep(randint(2, 6))
                continue

            block_songs = soup.find("table", attrs={"id": "tablesort"})

            try:
                tags_url_song = block_songs.find_all("a", attrs={"class": "g-link"})
            except Exception as err_html:
                print('\n[43] get_url_songs:', err_html)
                count_no_block_songs += 1
                error_txt = f"[get_url_songs] count no block {count_no_block_songs}, Url Song: {performer_data['url']}"
                rwf.save_txt_data_add(data_txt=error_txt, path_file="No_block_songs.txt")
                if count_no_block_songs == 3:
                    rwf.save_txt_data(data_txt=response_text, path_file='No_block_songs.html')
                    break
                await asyncio.sleep(randint(2, 6))

            if tags_url_song:
                performer_data['data_songs'] = get_unique_songs(block_songs)

            break

        except Exception as err1:
            print(f'\n[56] err1 <{count_err}>', err1)
            if count_err > 4:
                print('>', end='')
                raise TypeError({'[41] ERROR': err1})
            count_err += 1
            await asyncio.sleep(6)
            continue

    print('>', end='')
    return performer_data


async def create_a_task_request(request_data, sess):
    data_list = []
    tasks_list = []
    exception_check = []

    for data in request_data:
        tasks_list.append(get_url_songs(sess, performer_data=data))

    res = await asyncio.gather(*tasks_list, return_exceptions=True)

    for data_validation in res:
        if not isinstance(data_validation, dict):
            exception_check.append(data_validation)
        else:
            data_list.append(data_validation)
    return data_list, exception_check


async def start_get_url_songs(session):
    name_table_songs = 'Songs_Data'
    name_table_main_categories = 'Songs_Data_Main_Categories'
    main_categories: list[str] = [url_data['url_cat'] for url_data in rwf.download_json_data('main_categories.json')]

    main_categories.append('https://amdm.ru/akkordi/avtorskie_pesni/')
    print(f"\n{main_categories=}")

    if os.path.isfile('stop_index_url_songs.txt'):
        check_index_songs = int(rwf.download_txt_data('stop_index_url_songs.txt'))
    else:
        check_index_songs = 0
    count_slice = 50

    performers_data_list = rwf.download_json_data(path_file='Performers_Data.json')
    request_data_slice = performers_data_list[check_index_songs:]
    count_total_data = len(performers_data_list)

    print("\n\n<<================= Идут запросы на получение ссылок на аккорды песен... =================>>")
    for data in split_list(request_data_slice, count_slice):
        res, exception_check = await create_a_task_request(request_data=data, sess=session)

        if exception_check:
            print('\nОшибки:')
            print(exception_check)
            return 0
        else:
            print('\nДанные получены')
            list_data_songs_main_categories = []
            other_songs = []
            for data_songs in res:
                if data_songs['url'] in main_categories:
                    list_data_songs_main_categories.append(data_songs)
                else:
                    other_songs.append(data_songs)

            if list_data_songs_main_categories:
                working_db.create_table_songs_and_add_data(
                    data_list=list_data_songs_main_categories, name_table=name_table_main_categories
                )

            working_db.create_table_songs_and_add_data(data_list=other_songs, name_table=name_table_songs)
            res.clear()
            other_songs.clear()
            list_data_songs_main_categories.clear()
            # ---------------------------------------------------------------------------------------------------------
            check_index_songs += len(data)
            rwf.save_txt_data(data_txt=check_index_songs, path_file='stop_index_url_songs.txt')
            print(f"Запросов Выполнено: {check_index_songs} из {count_total_data}")
            print('==' * 40)
