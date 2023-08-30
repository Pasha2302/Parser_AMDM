# Parser_AMDM
Parser of chords and lyrics to the database sqlite.
Source: https://amdm.ru

# Описание основных модулей парсера:

- < aiohttp_create_session.py > :
  - Возвращает объект сессии для выполнения асинхронных запросов.


- < html_performers.py > :
  - Проходит по алфавиту и собирает странички HTML с исполнителями
  - Сохраняет странички в папку [Html_Performers]

  
- < pars_url_performers.py > :
  - Загружает странички из папки [Html_Performers],
  - Собирает - Name и Url исполнителя (или категории)


- < url_songs.py > :
  - Проходит по списку Url исполнителей (категорий)
  - Собирает ссылки (url) на песни и название песен (title)
  - Записывает данные в базу данных, разделяя на две таблицы:
    - Таблица Songs_Data - Таблица песен исполнителей.
    - Таблица Songs_Data_Main_Categories - Таблица песен основных категорий сайта.
  - Структура двух таблиц одинаковая:
    - url_song TEXT PRIMARY KEY,
    - Title TEXT,
    - Performer TEXT,
    - Lyrics_Chords TEXT,
    - Link_to_Video TEXT,
    - Url_Performers TEXT


- < < main.py > > :
  - Точка входа. Запуск парсера. >
  - Запускает основной цикл парсера, берет из базы все песни из двух таблиц.
  - Выбирает только те песни у которых не определено поле Lyrics_Chords (аккорды) и Link_to_Video (ссылка на видео youtube)
  - Проходит по Url адресам песен, добавляя в таблицу данные Lyrics_Chords, Link_to_Video.


# Особенности работы парсера:
- Парсер не начнет новый сбор песен, пока не пройдет полный цикл по списку,
  ранее собранных песен.

