import re


regx_find_brackets = re.compile(r"\(.+\)")
regx_punctuation_mark = re.compile(r"[- .,'\"]")


def format_name_songs(name_song: str) -> str:
    name_f = re.sub(regx_find_brackets, '', name_song)
    name_f = re.sub(regx_punctuation_mark, '', name_f)
    return name_f.strip().lower()


def get_unique_songs(table_block):
    list_info_songs = []

    rows = table_block.find_all("tr")
    rows = rows[1:]
    # print(f"\nВсего песен: {len(rows)}")

    for row in rows:
        return_cycle = False

        check_tag = False
        title: str = row.find('a').text.strip()
        url_song = row.find('a').get('href')
        views: str = row.find('td', {'class': 'number hidden-phone'}).text
        views: int = int(views.strip().replace(',', ''))

        if row.find('span', {'class': 'fa fa-check-circle tooltip'}):
            check_tag = True

        if list_info_songs:
            for t, check_data in enumerate(list_info_songs):
                if format_name_songs(check_data['title']) == format_name_songs(title):

                    if check_data['check_tag']:
                        return_cycle = True
                        break

                    elif check_tag or views > check_data['views']:
                        del list_info_songs[t]
                        break

                    elif views < check_data['views']:
                        return_cycle = True

        if return_cycle:
            continue

        list_info_songs.append({'title': title, 'url_song': url_song, 'views': views, 'check_tag': check_tag})

    new_list_info_songs = []
    for data_dict_song in list_info_songs:
        del data_dict_song['views']
        del data_dict_song['check_tag']
        new_list_info_songs.append(data_dict_song)

    return new_list_info_songs
