import asyncio
import aiohttp
from random import randint
import re
from bs4 import BeautifulSoup as BS

import headers_cookies as hc
import reading_writing_files as rwf


async def get_chords(session: aiohttp.client.ClientSession, data_song):
    count_err = 0
    result_data_dict = dict()
    result_data_dict['url_song'] = data_song[0]
    result_data_dict['title'] = data_song[1]
    result_data_dict['performer'] = data_song[2]
    result_data_dict['lyric_chord'] = data_song[3]
    result_data_dict['link_to_video'] = data_song[4]
    result_data_dict['url_performer'] = data_song[5]

    while True:
        try:
            response = await session.get(url=result_data_dict['url_song'], cookies=hc.cookies, headers=hc.headers)
            response_text = await response.text()

            soup = BS(response_text, 'lxml', multi_valued_attributes=None)
            check_tag = soup.find("body").text

            if 'Too Many Requests..' in check_tag:
                rwf.save_txt_data(data_txt=response_text, path_file='Erorr_Html_3.html')
                await asyncio.sleep(randint(2, 6))
                continue

            block_chord = soup.find("pre", attrs={"itemprop": "chordsBlock"})
            if block_chord:
                block_chord_f = re.sub(r"<pre.+?>", '', str(block_chord)).replace('</pre>', '')
                block_chord_f = re.sub(r"<div.+?>", '', block_chord_f).replace('</div>', '')
                result_data_dict['lyric_chord'] = block_chord_f
            else:
                rwf.save_txt_data(data_txt=response_text, path_file='No_data_block_chord.html')

            link_youtube = soup.find("iframe", attrs={"src": re.compile(r"https://www\.youtube\.com")})
            if link_youtube:
                result_data_dict['link_to_video'] = link_youtube.get('src')
            else:
                if 'Всего два аккорда' in result_data_dict['title']:
                    rwf.save_txt_data(data_txt=response_text, path_file='No_data_link_to_video.html')

            break

        except Exception as err1:
            print(f'\n[52] err1 <{count_err}>', err1)
            if count_err > 4:
                print('>', end='')
                raise TypeError({'[41] ERROR': err1})
            count_err += 1
            await asyncio.sleep(6)
            continue

    print('>', end='')
    return result_data_dict
