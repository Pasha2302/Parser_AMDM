import aiohttp
import reading_writing_files as rwf
import asyncio
import headers_cookies as hc
from pathlib import Path
from bs4 import BeautifulSoup as BS
from random import randint


async def get_main_categories(session: aiohttp.client.ClientSession):
    url = 'https://amdm.ru/'
    path_file = 'main_categories.json'
    count_err = 0

    while True:
        try:
            response = await session.get(url=url, cookies=hc.cookies, headers=hc.headers)

            response_text = await response.text()

            soup = BS(response_text, 'lxml', multi_valued_attributes=None)
            check_tag = soup.find("body").text
            if 'Too Many Requests..' in check_tag:
                rwf.save_txt_data(data_txt=response_text, path_file='Erorr_Html_categories.html')
                await asyncio.sleep(randint(5, 10))
                continue

            block_categories = soup.find('div', {'class': 'b-index-artist-tematika g-padding'})
            list_tags_categories = block_categories.find_all(
                'span', {'class': 'b-artist-tematika-item__description'}
            )

            list_categories = []
            for data_tag_cat in list_tags_categories:
                name_cat = data_tag_cat.find('a').text.strip()
                url_cat = data_tag_cat.find('a').get('href').strip()
                list_categories.append(
                    {'name_cat': name_cat, 'url_cat': url_cat}
                )

            rwf.save_json_data(json_data=list_categories, path_file=path_file)
            break

        except Exception as err1:
            print('\n[30] err1', err1)
            if count_err > 4:
                raise TypeError(f'\n[47] get_main_categories() ERROR:\n{err1}')
            count_err += 1
            await asyncio.sleep(6)
            continue

    return 1


async def get_html_performers(session: aiohttp.client.ClientSession, url, path_file):
    count_err = 0

    while True:
        try:
            response = await session.get(url=url, cookies=hc.cookies, headers=hc.headers)

            response_text = await response.text()

            soup = BS(response_text, 'lxml', multi_valued_attributes=None)
            check_tag = soup.find("body").text
            if 'Too Many Requests..' in check_tag:
                rwf.save_txt_data(data_txt=response_text, path_file='Erorr_Html.html')
                await asyncio.sleep(randint(5, 10))
                continue

            rwf.save_txt_data(data_txt=response_text, path_file=path_file)
            break

        except Exception as err2:
            print('\n[75] get_html_performers() err2:', err2)
            if count_err > 4:
                raise TypeError(f'\n[77] get_html_performers() ERROR:\n{err2}')
            count_err += 1
            await asyncio.sleep(6)
            continue

    print('>', end='')
    return 1


async def start_get_html_performers(session):
    tasks_list = []
    exception_check = []

    await get_main_categories(session)
    print("\n\n<<================= Идут запросы на получение ссылок Исполнителей... =================>>")
    for pag in range(1, 55):
        url = f"https://amdm.ru/chords/{pag}"
        path_file = Path('Html_Performers', f'HtmlPerformers_{pag}.html')
        tasks_list.append(get_html_performers(session, url=url, path_file=path_file))

    res = await asyncio.gather(*tasks_list, return_exceptions=True)

    for data_validation in res:
        if data_validation != 1:
            exception_check.append(data_validation)

    if exception_check:
        print('\nОшибки:')
        print(exception_check)

    if res:
        print('\nДанные получены')
