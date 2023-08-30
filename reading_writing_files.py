import json
import os
# import openpyxl.worksheet.worksheet
# from openpyxl import load_workbook


def save_txt_data(data_txt, path_file):
    with open(path_file, 'w', encoding='utf-8') as f:
        f.write(str(data_txt))


def save_txt_data_add(data_txt, path_file):
    with open(path_file, 'a', encoding='utf-8') as f:
        f.write(str(data_txt) + '\n')


def download_txt_data(path_file):
    with open(path_file, encoding='utf-8') as f:
        return f.read()


def save_json_complementing(json_data, path_file, ind=False):
    indent = None
    if ind:
        indent = 4
    if os.path.isfile(path_file):
        # File exists
        with open(path_file, 'a', encoding='utf-8') as outfile:
            outfile.seek(outfile.tell() - 1, os.SEEK_SET)
            outfile.truncate()
            outfile.write(',\n')
            json.dump(json_data, outfile, ensure_ascii=False, indent=indent)
            outfile.write(']')
    else:
        # Create file
        with open(path_file, 'w', encoding='utf-8') as outfile:
            array = [json_data]
            json.dump(array, outfile, ensure_ascii=False, indent=indent)


def save_json_data(json_data, path_file):
    with open(path_file, 'w', encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)


def download_json_data(path_file) -> list[dict] | dict:
    with open(path_file, encoding="utf-8") as f:
        return json.load(f)


# def download_xlsx_data(path_file) -> iter:
#     wb = load_workbook(path_file)
#     sheet: openpyxl.worksheet.worksheet.Worksheet = wb.active
#     row_generator = sheet.iter_rows(min_row=0, values_only=True)
#     return row_generator
