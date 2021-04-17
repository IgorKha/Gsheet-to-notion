import gspread
import pandas as pd
import time
import pickle
from notion.client import NotionClient
import notio

token = ''
client = NotionClient(token_v2=token)
notion_url = ''
gc = gspread.service_account(filename='credentials.json')

while True:
    # Читаем гугл таблицу
    sh = gc.open("test")  # Открываем файл по названию
    worksheet = sh.worksheet('sheet')  # Указываем лист внутри файла

    df = pd.DataFrame(
        # Собираем DataFrame pandas и (ниже) переименовываем столбцы в названия которые соответстуют названиям полей
        # в notion
        worksheet.get_all_records())
    df.columns = ['Date', 'Name', 'Email', 'OpenLand', 'Telegram', 'Team_to_help', 'Competence', 'Task', 'Profit',
                  'Why_we', 'work_hour', 'timezone', 'About_me', 'otkuda_uznal', 'CV', 'first_status',
                  'Interview', 'Result']
    df = df.astype(
        str)  # Конвертируем все значения в строковые чтобы не было ошибок в при записи ячеек в которых только цифры
    df = pd.DataFrame.to_dict(df, orient='records')  # Преобразовывем в список словарей

    # Notion, Access a database using the URL of the database page or the inline block
    cv = client.get_collection_view(notion_url)

    # with open('db.pickle', 'wb') as handle:
    #     pickle.dump(df, handle)

    with open('db.pickle', 'rb') as handle:
        db = pickle.load(handle)
        handle.close()

    time_check = []
    for i in db:
        time_check.append(i['Date'])

    # Сверяем DataFrame с Файлом по ключу 'Date' и складываем весь словарь result
    result = []
    for i in df:
        if i['Date'] not in time_check:
            result.append(i)
            i.update({'Status': 'Новая'})
    print(f"Результат {result}")

    # Пишем в Notion из result
    for i in result:
        row = cv.collection.add_row()
        row.name = i['Name']
        row.Date = i['Date']
        row.Email = i['Email']
        row.OpenLand = i['OpenLand']
        row.Telegram = i['Telegram']
        row.Team_to_help = i['Team_to_help']
        row.Competence = i['Competence']
        row.Task = i['Task']
        row.Profit = i['Profit']
        row.Why_we = i['Why_we']
        row.work_hour = i['work_hour']
        row.timezone = i['timezone']
        row.About_me = i['About_me']
        row.otkuda_uznal = i['otkuda_uznal']
        row.CV = i['CV']
        row.first_status = i['first_status']
        row.Interview = i['Interview']
        row.Result = i['Result']
        row.Status = i['Status']

    with open('db.pickle', 'ab+') as handle:
        pickle.dump(result, handle)
        handle.close()

    time.sleep(300)
