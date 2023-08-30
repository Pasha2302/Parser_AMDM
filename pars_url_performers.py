import os
from pathlib import Path
import re

from bs4 import BeautifulSoup as BS
import reading_writing_files as rwf


def number_in_html_file_title(html_file_title):
    return int(re.search(r"\d+", html_file_title).group())


def get_url_perf():
    list_datas = []

    path_html_perf = str(Path("Html_Performers"))
    list_name_files = os.listdir(path_html_perf)
    list_name_files.sort(key=number_in_html_file_title)

    for t, file_name in enumerate(list_name_files, start=1):
        print(file_name)

        path_data = str(Path(path_html_perf, file_name))
        text_html = rwf.download_txt_data(path_file=path_data)
        soup = BS(text_html, 'lxml')
        data_name_url = [
            {"name": url.text.strip(), "url": url.get('href')} for url in soup.find_all("a", attrs={"class": "artist"})
        ]
        list_datas.extend(data_name_url)

    new_file_len = len(list_datas)
    rwf.save_json_data(json_data=list_datas, path_file='Performers_Data.json')
    print('==' * 40)
    print(f"Всего исполнителей: {new_file_len}")


if __name__ == '__main__':
    get_url_perf()
