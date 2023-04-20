import requests
from requests.adapters import HTTPAdapter
import sqlite3
import re
import time
import wget
import os
import shutil
import with_sales
import yandex_market
import xlsxwriter as xl
import traceback
import random
from bs4 import BeautifulSoup as bs
from multiprocess.dummy import Pool as ThreadPool
from datetime import datetime, date


URL = 'https://tdbovid.ru/katalog_zapchastej'
BASE_URL = 'https://tdbovid.ru'
today = str(date.today()).split('-')
filename = 'tdbovid_' + today[2] + '_' + today[1] + '_' + today[0][2:] + '_2gis.db'
tdbovid_adapter = HTTPAdapter(max_retries=50)
session = requests.Session()
session.mount(BASE_URL, tdbovid_adapter)
addresses = ["г.Челябинск,ул.Линейная,98", "г.Челябинск,Троицкийтр.,66",
             "г.Магнитогорск,ул.Заводская,1/2", "г.Магнитогорск,ул.Кирова,100", 
             "г.Красноярск,ул.2-яБрянская,34,стр.2", "г.Алдан,ул.Комсомольская,19Б",
             "СкладIVECOавтосервис", "г.Бодайбо,ул.АртемаСергеева,9А"]

def pic_link(links):
    length = len(links)
    result = ""
    if length == 1:
        return BASE_URL + links[0] if links[0] is not None else None
    for el in links:
        if links.index(el) < length-1:
            result += BASE_URL + el + ','
        else:
            result += BASE_URL + el
    return result


def get_page(url):
    time = datetime.strftime(datetime.now(), "%H.%M.%S")
    print(time, ' - ', url)
    page = bs(session.get(url, timeout=10).text, 'lxml')
    return page


def get_catalog(page):
    catalog_item = page.find_all(class_="cart-cat")
    catalog = []
    for i in catalog_item:
        catalog.append({
            'url' : BASE_URL + i.parent.get('href'),
            'category' : i.find('p').text
        })
    return catalog


def get_item(elem):
    page = get_page(elem['url'])
    catalog_item_pos = page.find_all(class_="productrow2")
    item = []
    for i in catalog_item_pos:
        # список на случай нескольких картинок на странице
        imgs = []
        item_url = BASE_URL + i.find('a').get('href')
        item_page = get_page(item_url)
        name = i.find('a', class_="col-lg-3").text.strip()
        try:
            uid = item_page.find('meta', attrs={'name':'uid'}).get('content')
        except Exception:
            print(str(item_url) + " ошибка с uid!")
            uid = name
        pics = item_page.find_all('a',href=re.compile('jpg'))
        for pic in pics:
            imgs.append(pic.get('href'))              
        
        print("Количество изображений - " + str(len(imgs)))
        
        if len(imgs) > 0:
            for el in imgs:
                if el is not None and el.split('/')[-1] == '_noimage_300x300_3dd.jpg':
                    el = None
            
        download = []
        start = 0
        
        if not os.path.exists('D:/parsing/pics/' + uid + '_0.jpeg') and len(imgs) > 0:
            # if len(imgs) > 0:
            for el in imgs:
                download.append(el)
        elif len(imgs) > 1:
            start = 1
            for e in range(1, len(imgs)):
                if os.path.exists('D:/parsing/pics/' + uid + '_' + str(e) + '.jpeg'):
                    if imgs[e] != imgs[len(imgs)-1]:
                        start += 1
                    else:
                        start = 999    
                else:
                    break                   
        else:
            start = 999
           
        if start < 999:
            for k in range(start, len(imgs)):
                #download.append(imgs[k])
                print(BASE_URL + imgs[k])
                wget.download(BASE_URL + imgs[k], 'D:/parsing/pics/' + uid + '_' + str(k) + '.jpeg')
        
        for el in download:
            print(BASE_URL + el)
            wget.download(BASE_URL + el, 'D:/parsing/pics/' + uid + '_' + str(download.index(el)) + '.jpeg') 
                    
        # получаем список складов с остатками
        try:
            item_stores = item_page.find('table').find_all('tr')
        except Exception:
            item_stores = []
            print(str(item_url) + " - косяк с табличкой наличия!")    
        stores = {}
        nalichie = 0.0
        if len(item_stores) > 0:
            for j in item_stores:
                print(j.find_all('td')[0].text.strip())
                print(j.find_all('td')[1].text.replace('шт.', '').strip())
                try:
                    stores[j.find_all('td')[0].text.strip()] = int(j.find_all('td')[1].text.replace('шт.', '').strip())              
                    nalichie += float(j.find_all('td')[1].text.replace('шт.', '').replace(",", ".").strip())
                except Exception:
                    print(str(item_url) + " косяк с наличием")
        else:
            stores["г.Челябинск, ул.Линейная, 98"] = 0
            stores["г.Челябинск, Троицкий тр., 66"] = 0
            stores["г.Магнитогорск, ул.Кирова, 100"] = 0
            stores["г.Магнитогорск, ул.Заводская, 1/2"] = 0
            stores["г.Красноярск, ул. 2-я Брянская, 34, стр. 2"] = 0
        # Добавлены поля item_url и description. В description "копируется" поле name. Поле marka переименовано в category.
        item.append({
                    'category': elem['category'],
                    'artikl': i.find('a', class_="col-lg-2").text.strip(),
                    'item_url': item_url,
                    'description': i.find('a', class_="col-lg-3").text.strip(),
                    'kod': i.find('a', class_="col-lg-1").text.strip(),
                    'uid': uid,
                    'name': name,
                    'price': None if  i.find('span').text.strip().replace(' ', '') == 'Уточняйтеуменеджера' else float(i.find('span').text.strip().replace(' ', '').replace('₽', '')),
                    'nalichie': nalichie if nalichie > 0.0 else "Уточняйтеуменеджера",
                    'baza_store' : stores.get('г.Челябинск, ул.Линейная, 98'),
                    'tr_tr_store' : stores.get('г.Челябинск, Троицкий тр., 66'),
                    'm_kir_store' : stores.get('г.Магнитогорск, ул.Кирова, 100'),
                    'm_zav_store' : stores.get('г.Магнитогорск, ул.Заводская, 1/2'),
                    'kr_store' : stores.get('г.Красноярск, ул. 2-я Брянская, 34, стр. 2'),
                    'pic_link' : pic_link(imgs),
                })  
        
    conn = sqlite3.connect('D:/parsing/dbs/' + filename)
    c = conn.cursor()
    c.execute('PRAGMA encoding = "UTF-8"')
    while True:
        try:
            c.execute("CREATE TABLE IF NOT EXISTS tdbovid(date DATE, category VARCHAR(255), artikl VARCHAR(255), item_url VARCHAR(255), description VARCHAR(255), kod VARCHAR(255), name VARCHAR(255), price REAL, nalichie INT, baza_store INT, tr_tr_store INT, m_kir_store INT, m_zav_store INT, kr_store INT, pic_link VARCHAR(255))")
            break
        except:
            time.sleep(random.randint(3, 20))
            
    for i in item:
        try:
            c.execute('INSERT INTO tdbovid VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (datetime.now().date(), i['category'], i['artikl'], i['item_url'], i['description'], i['kod'], i['name'], i['price'], i['nalichie'], i[ 'baza_store'], i['tr_tr_store'], i['m_kir_store'], i['m_zav_store'], i['kr_store'], i['pic_link']))
            conn.commit()
        except Exception as err:
            print('Ошибка!')
            # print('uid - ', i['uid'])
            print(err)
    
    conn.close()

    if page.find('a', class_='next page-numbers'):
        next_page = page.find('a', class_='next page-numbers').get('href')
        print(next_page)
    else:
        next_page = None
    if next_page:
        new_link = BASE_URL+next_page
        new_elem = {'url': new_link, 'category': elem['category']}
        get_item(new_elem)
     

def update_database():
    conn = sqlite3.connect('D:/parsing/dbs/' + filename)
    c = conn.cursor()
    columns = ["price", "baza_store", "tr_tr_store","m_kir_store", "m_zav_store", "kr_store", "pic_link", "sales"]
    sales = "ALTER TABLE tdbovid ADD COLUMN sales BOOLEAN"    
    try:
        c.execute(sales)
    except Exception:
        conn.close()
        conn = sqlite3.connect('D:/parsing/dbs/' + filename)
        c = conn.cursor()
        c.execute(sales)
    
    for el in columns:
        if el == "sales":
            upd = f"UPDATE tdbovid SET {el} = True where category = 'Распродажа'"
        elif el == "pic_link":
            upd = f"UPDATE tdbovid SET {el} = '' where {el} IS NULL;"
        else:
            upd = f"UPDATE tdbovid SET {el} = 0 where {el} IS NULL;"
        c.execute(upd)   
    c.execute("UPDATE tdbovid SET sales = False where sales IS NULL")
    conn.commit()
    c.execute("DELETE FROM tdbovid where sales is True")
    final_count = c.execute("select count(*) from tdbovid").fetchall()[0][0]
    print("Количество номенклатуры - "+ str(final_count) + " шт.")
    conn.commit()
    conn.close()
    

def copy_databases():
    _2gis_filepath = "D:/parsing/dbs/" + filename
    avito_filepath = "D:/parsing/dbs/" + filename.replace("2gis.db", "avito.db")
    drom_filepath = "D:/parsing/dbs/" + filename.replace("2gis.db", "drom.db")
    spl_filepath = "D:/parsing/dbs/" + filename.replace("2gis.db", "spl.db")
    try:
        shutil.copyfile(_2gis_filepath, avito_filepath)
        shutil.copyfile(_2gis_filepath, drom_filepath)
    except:
        print(traceback.format_exc())
    filepaths = {"2gis": _2gis_filepath, "avito": avito_filepath, "drom": drom_filepath, "spl": spl_filepath}
    return filepaths
    

def final_databases(filepaths):
    conn = sqlite3.connect(filepaths.get("2gis"))
    c = conn.cursor()
    c.execute("ALTER TABLE tdbovid DROP COLUMN sales")
    conn.commit()
    conn.close()
    try:
        conn = sqlite3.connect(filepaths.get("avito"))
        c = conn.cursor()
        c.execute("ALTER TABLE tdbovid DROP COLUMN description")
        c.execute("ALTER TABLE tdbovid DROP COLUMN item_url")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN category TO marka")
        conn.commit()
        conn.close()
    except:
        print(traceback.format_exc())
    try:
        conn = sqlite3.connect(filepaths.get("drom"))
        c = conn.cursor()
        c.execute("CREATE TABLE tdbovid_2 AS SELECT * FROM tdbovid WHERE 0")
        c.execute("INSERT INTO tdbovid_2 SELECT * FROM tdbovid")
        c.execute("ALTER TABLE tdbovid RENAME TO old_tdbovid")
        c.execute("ALTER TABLE tdbovid_2 RENAME TO tdbovid")
        c.execute("DROP TABLE old_tdbovid")
        c.execute("UPDATE tdbovid SET description = '<p>Запчасти для грузовиков и спецтехники в наличии более 150 000 наименований.</p><br><p>Оплата: наличными, онлайн-оплата на сайте или платеж по счету.</p><br><p>Доставим за 4 часа или отправим по всей России.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><br><p>Самовывоз со склада по адресам:</p><ul><li>г. Челябинск ул. Линейная, 98;</li><li>г. Челябинск, ул.Троицкий тракт, 66.</li></ul><br><p>Если в нашем магазине не нашлась нужная запчасть, комплект, машинокомплект, то это не значит, что ее нет на наших складах. Запчастей для грузовиков более 150 000 наименований. Методов их подбора много. Просто позвоните или напишите нам, мы обязательно подберем нужную запчасть быстро и по привлекательной цене.</p><br><p>Компания ТД БОВИД являемся одним из крупнейших поставщиков в России и официальным дилером АО «Автомобильный завод «УРАЛ», ПАО</p><p>«КАМАЗ», ПАО «Автодизель», АО «ЯЗДА», ООО «УАЗ», ООО</p><p>«ИВЕКО-АМТ», ООО «Автоцентр ОСВАР», АО «Гидросила М»,</p><p>представителем 35 отечественных заводов-изготовителей, а также</p><p>IVECO, VOLVO, RENAULT TRUCKS и спецтехнике KOMATSU, HITACHI, </p><p>CATERPILLAR.</p></ul>'")
        c.execute("ALTER TABLE tdbovid DROP COLUMN item_url")
        c.execute("ALTER TABLE tdbovid DROP COLUMN date")
        c.execute("ALTER TABLE tdbovid DROP COLUMN sales")
        # c.execute("ALTER TABLE tdbovid DROP COLUMN uid")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN category TO marka")
        conn.commit()
        conn.close()
    except:
        print(traceback.format_exc())
    try:
        shutil.copyfile(filepaths.get("drom"), filepaths.get("spl"))
    except:
        print(traceback.format_exc())
    
    try:
        conn = sqlite3.connect(filepaths.get("spl"))
        c = conn.cursor()
        c.execute("ALTER TABLE tdbovid RENAME COLUMN marka TO Производитель")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN artikl TO Артикул")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN kod TO Код")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN name TO Название")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN price TO 'Цена для всех складов'")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN baza_store TO 'г.Челябинск, ул.Линейная 98'")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN nalichie TO 'Общее количество деталей в наличии'")
        c.execute("ALTER TABLE tdbovid RENAME COLUMN pic_link TO 'Ссылки на изображения'")
        c.execute("ALTER TABLE tdbovid ADD COLUMN 'г.Челябинск, ул.Линейная 98, цена' REAL")
        c.execute("""DELETE FROM tdbovid 
                    where tdbovid.Производитель = "Автошины" 
                    or tdbovid.Производитель = "ВАЗ" 
                    or tdbovid.Производитель = "УАЗ" 
                    or tdbovid.Производитель = "ГАЗ легковой" 
                    or tdbovid.Производитель = "Инструмент" 
                    or tdbovid.Производитель = "Легковые иномарки" 
                    or tdbovid.Производитель = "Поршневая группа" 
                    or tdbovid.Производитель = "Поршневая группа ВАЗ Мотордеталь" 
                    or tdbovid.Производитель = "Поршневая группа Мотордеталь" 
                    or tdbovid.Производитель = "Поршневая группа Украина" 
                    or tdbovid.Производитель = "Mitsubishi L200" 
                    or tdbovid.Производитель = "Прочие"  
                    or tdbovid."Общее количество деталей в наличии" < 5""")
        conn.commit()
        c.execute("CREATE TABLE tdbovid_2 AS SELECT * FROM tdbovid WHERE 0")
        c.execute("INSERT INTO tdbovid_2 SELECT * FROM tdbovid")
        conn.commit()
        if len(c.execute("SELECT * FROM tdbovid_2").fetchall()) > 1:
            c.execute("""UPDATE tdbovid SET "г.Челябинск, ул.Линейная 98, цена" = (SELECT tdbovid_2."Цена для всех складов"
                                                                                   FROM tdbovid_2 WHERE Артикул = tdbovid.Артикул 
                                                                                   AND Код = tdbovid.Код 
                                                                                   AND Название = tdbovid.Название)""")
        c.execute("DROP TABLE tdbovid_2")
        conn.commit()
        c.execute("""CREATE TABLE tdbovid_2 
                    AS SELECT tdbovid.Производитель, tdbovid.Артикул, 
                    tdbovid.Код, tdbovid.Название, tdbovid."Цена для всех складов", 
                    tdbovid."Общее количество деталей в наличии", 
                    tdbovid."г.Челябинск, ул.Линейная 98", 
                    tdbovid."г.Челябинск, ул.Линейная 98, цена", 
                    tdbovid."Ссылки на изображения"
                    FROM tdbovid;""")
        c.execute("ALTER TABLE tdbovid RENAME TO old_tdbovid")
        c.execute("ALTER TABLE tdbovid_2 RENAME TO tdbovid")
        c.execute("DROP TABLE old_tdbovid")
        conn.commit()
        conn.close()
    except:
        print(traceback.format_exc())
        

def save_to_xlsx(base):
    workbook_name = base.replace(".db", ".xlsx")
    workbook_name = workbook_name.replace("dbs/", "")
    workbook = xl.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()
    conn = sqlite3.connect(base)
    c = conn.cursor()
    columns = c.execute("pragma table_info(tdbovid)").fetchall()
    data = c.execute("select * from tdbovid").fetchall()
    for i in range(0, len(data) + 1):
        for j in range(0, len(columns)):
            if i == 0:
                worksheet.write(i, j, columns[j][1])
            else:
                worksheet.write(i, j, data[i-1][j])
    workbook.close()
    print("Файл " + workbook_name + " готов")
       

def main():    
    start = datetime.now()
    all_links = get_catalog(get_page(URL))
    print(all_links)
    print(len(all_links))        
    with ThreadPool(15) as pool:
        pool.map(get_item, all_links)
    update_database()
    # filepaths = copy_databases()
    # xlsx_bases = ["2gis", "drom", "spl"]
    # final_databases(filepaths) 
    # for el in xlsx_bases:
    #     save_to_xlsx(filepaths.get(el))
    # with_sales.main()
    # yandex_market.main()
    obzhee = (datetime.now() - start).total_seconds()
    print("Общее время - " + str(int(obzhee//3600)) + ":" + str(int((obzhee % 3600)//60)) + ":" + str(round(obzhee % 60)))

    
def test():
    all_links = get_catalog(get_page(URL))        
    with ThreadPool(15) as pool:
        pool.map(download_images, all_links)
    print("Всё готово")
    

def download_images(elem):
    page = get_page(elem['url'])
    catalog_item_pos = page.find_all(class_="productrow2")
    for i in catalog_item_pos:
        item_url = BASE_URL + i.find('a').get('href')
        item_page = get_page(item_url)
        try:
            uid = item_page.find('meta', attrs={'name':'uid'}).get('content')
        except Exception:
            print(item_url)
            
        pics = item_page.find_all('a',href=re.compile('jpg'))             
        print("Количество изображений - " + str(len(pics)))
        for pic in pics:
            print(BASE_URL + pic.get('href'))
            wget.download(BASE_URL + pic.get('href'), 'D:/parsing/update_pic/' + uid + '_' + str(pics.index(pic)) + '.jpeg')         
        
    if page.find('a', class_='next page-numbers'):
        next_page = page.find('a', class_='next page-numbers').get('href')
        print(next_page)
    else:
        next_page = None
    if next_page:
        new_link = BASE_URL+next_page
        new_elem = {'url': new_link, 'category': elem['category']}
        download_images(new_elem)
    
    
if __name__ == "__main__":
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    main()
