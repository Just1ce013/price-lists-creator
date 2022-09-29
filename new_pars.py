import requests
from requests.adapters import HTTPAdapter
from datetime import date, datetime
import xlsxwriter as xl
import pandas as pd
import numpy as np
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ElementTree
from xml.dom import minidom
from yandex_market import yandex_new
from OOP import Ploschadka
from Gis import TwoGis
from Drom import Drom
from SPL import SPL
from ZZap import ZZap
from Rees import Rees46
from Avito import Avito
from AA import AA
from Yandex import Yandex
from Cfk import Cfk


category_names = {"ural":"Урал","ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":"УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370",
              "yamz":"ЯМЗ","kamaz":"КАМАЗ","maz":"МАЗ","uaz":"УАЗ","elektrooborudovanie":"Электрооборудование","gaz-gruzovoj":"ГАЗ грузовой",
              "gaz-legkovoj":"ГАЗ легковой","gidrosila":"Гидросила","porschnevaya-gruppa":"Поршневая группа","zil":"ЗИЛ","avtoshiny":"Автошины",
              "cat":"CAT","hitachi":"Hitachi","hyundai":"HYUNDAI","iveco":"IVECO","komatsu":"KOMATSU","avtobusy":"Автобусы","avtokrany-i-kmu":"Автокраны и КМУ",
              "akkumulyatory":"Аккумуляторы","vaz":"ВАЗ","dz-98-dz-180":"ДЗ-98;ДЗ-180","dt-75":"ДТ-75","instrument":"Инструмент",
              "legkovye-inomarkigruzovye-inomarkikommercheskij-transport":"Легковые иномарки","mtz":"МТЗ","pogruzchiki":"Погрузчики",
              "podshipniki":"Подшипники","porschnevaya-gruppa-vaz-motordetal":"Поршневая группа ВАЗ Мотордеталь","porschnevaya-gruppa-urkaina":"Поршневая группа Украина",
              "pricepy":"Прицепы","prochie":"Прочие","radiatory-lrz":"Радиаторы ЛРЗ","rvd":"РВД","t-150":"Т-150","t-170":"Т-170","t-40":"Т-40",
              "filtry-i-komplekty-prokladok-motordetal":"Фильтры и комплекты прокладок МОТОРДЕТАЛЬ","shaaz":"ШААЗ","ekskavator":"Экскаватор",
              "yumz":"ЮМЗ","rasprodazha":"Распродажа"}
fail_articles = ["34А-71-11611", "353398917с (16284016)", "ШД 1,2 (15972146)", "ПП (15972167)", "ТСС-140 392440 (15592572)", "ТСС-100 392400 (15592415)", "СВ000011441 (15548235)", "3ЕВ-04-32410", "А810180/LA810180", "195-78-21331 НХ", "34А-28-00110", "КГК №7"]
category_ids = {"Автобусы": 1, "Автокраны и КМУ": 2, "Автошины": 3, "Аккумуляторы": 4, "ВАЗ": 5, "ГАЗ грузовой": 6, "ГАЗ легковой": 7, "Гидросила": 8, "ДЗ-98;ДЗ-180": 9, "ДТ-75": 10, 
                "ЗИЛ": 11, "Инструмент": 12, "КАМАЗ": 13, "Легковые иномарки": 14, "МАЗ": 15, "МТЗ": 16, "Погрузчики": 17, "Подшипники": 18, "Поршневая группа": 19, "Поршневая группа ВАЗ Мотордеталь": 20, 
                "Поршневая группа Мотордеталь": 21, "Поршневая группа Украина": 22, "Прицепы": 23, "Прочие": 24, "РВД": 25, "Радиаторы ЛРЗ": 26, "Т-150": 27, "Т-170": 28, "Т-40": 29, "УАЗ": 30, 
                "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370": 31, "Урал": 32, "Фильтры и комплекты прокладок МОТОРДЕТАЛЬ": 33, "ШААЗ": 34, "Экскаватор": 35, "Электрооборудование": 36, "ЮМЗ": 37, "ЯМЗ": 38, "CAT": 39, "HYUNDAI": 40, 
                "Hitachi": 41, "IVECO": 42, "KOMATSU": 43}
fields_for_spl = ["Производитель", "Артикул", "Код", "Название", 
                      "Цена для всех складов", "Общее количество деталей в наличии", 
                      "г.Челябинск, ул.Линейная 98", "г.Челябинск, ул.Линейная 98, цена", 
                      "Ссылки на изображения"]
stop_categories = ["Автошины", "ВАЗ", "УАЗ", "ГАЗ легковой", "Инструмент", 
                           "Легковые иномарки", "Поршневая группа", "Поршневая группа ВАЗ Мотордеталь", 
                           "Поршневая группа Мотордеталь", "Поршневая группа Украина", "Прочие", "Распродажа"]
fields_for_autopiter = ["Производитель", "Артикул", "Наименование", "Цена", "Остатки"]
fields_for_cfk_price = ["IDТовара", "Наименование", "ЦенаБезНДС", "СтавкаНДС", "ЦенаСНДС", "КодВалюты", "КодЕдиницыИзмерения"]
fields_for_cfk_leftover = ["IDТовара", "Наименование", "IDСклада", "ОстатокНаСкладе", "СрокПоставки"]
fields_for_zzap = ["Производитель", "Номер производителя", "Наименование", "Цена", "Количество", "Срок поставки", "Ссылка на фото запчасти"]
fields_for_avito = ["Id", "ListingFree", "AdStatus", "AllowEmail", "ManagerName", "ContactPhone", 
                        "Address", "DisplayAreas", "Category", "TypeId", "AdType", "Title", "Description", 
                        "Price", "Condition", "OEM","ImageUrls"]  
fields_for_drom = ["marka", "artikl", "description", "kod", "name", "price", 
                        "nalichie", "baza_store", "tr_tr_store", "m_kir_store", 
                        "m_zav_store", "kr_store", "pic_link"]
fields_for_2gis = ["date", "category", "artikl", "item_url", "description", "kod", 
                       "uid", "name", "price", "nalichie", "baza_store", "tr_tr_store", 
                       "m_kir_store", "m_zav_store", "kr_store", "pic_link"]
addresses = ["г.Челябинск, ул.Линейная, 98", "г.Челябинск, Троицкий тр., 66",
             "г.Магнитогорск, ул.Заводская, 1/2", "г.Магнитогорск, ул.Кирова, 100", 
             "г.Красноярск, ул. 2-я Брянская, 34, стр. 2", "г. Алдан, ул. Комсомольская, 19Б",
             "Склад IVECO автосервис", "г.Бодайбо, ул. Артема Сергеева, 9А"]  
URL = 'https://tdbovid.ru/katalog_zapchastej'
BASE_URL = 'https://tdbovid.ru'
today = str(date.today()).split('-')
tdbovid_adapter = HTTPAdapter(max_retries=5)
session = requests.Session()
session.mount(BASE_URL, tdbovid_adapter)              
tree = ElementTree()       

def write_column_names(worksheet, names):
    for j in range(0, len(names)):
        worksheet.write(0, j, names[j])


def write_data(worksheet, current_row, data, columns_count):
    for i in range(current_row, current_row + len(data)):
        for j in range(0, columns_count):
            worksheet.write(i, j, data[i - current_row][j])        

        
def pic_links(imgs):
    pic_links = ""
    if len(imgs) > 0:
        count = len(imgs)/3
        for el in imgs:
            if el["url"].find("small") == -1 and el["url"].find("medium") == -1:
                url = BASE_URL + el["url"]
                pic_links += url
                if count > 1:
                    pic_links += ", "
                    count = count - 1
    return pic_links


def obzhee():
    start = 0
    limit = 1000
    spl_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_spl.xlsx")
    spl_worksheet = spl_workbook.add_worksheet()
    gis_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_2gis.xlsx")
    gis_worksheet = gis_workbook.add_worksheet()
    drom_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_drom.xlsx")
    drom_worksheet = drom_workbook.add_worksheet()
    avito_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_avito.xlsx")
    avito_worksheet = avito_workbook.add_worksheet()
    zzap_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_zzap.xlsx")
    zzap_worksheet = zzap_workbook.add_worksheet()
    write_column_names(spl_worksheet, fields_for_spl)
    write_column_names(gis_worksheet, fields_for_2gis)
    write_column_names(drom_worksheet, fields_for_drom)
    write_column_names(avito_worksheet, fields_for_avito)
    write_column_names(zzap_worksheet, fields_for_zzap)
    data_for_spl = [] 
    data_for_2gis = [] 
    data_for_drom = [] 
    data_for_avito = [] 
    data_for_zzap = []
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            write_data(spl_worksheet, 1, data_for_spl, len(fields_for_spl))
            write_data(gis_worksheet, 1, data_for_2gis, len(fields_for_2gis))
            write_data(drom_worksheet, 1, data_for_drom, len(fields_for_drom))
            write_data(avito_worksheet, 1, data_for_avito, len(fields_for_avito))
            write_data(zzap_worksheet, 1, data_for_zzap, len(fields_for_zzap))
            spl_workbook.close()
            gis_workbook.close()
            drom_workbook.close()
            avito_workbook.close()
            zzap_workbook.close()
            break;
        
        for detail in details:
            spl_check = True
            gis_check = True
            drom_check = True
            avito_check = True
            zzap_check = True
            #Общие проверки
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            if len(detail["storage"]) == 0:
                continue 
            
            category = list(filter(None, detail["uri"].split('/')))[1]
            #Проверка spl
            if category in category_names.keys():
                if category_names[category] in stop_categories:
                    spl_check = False
            else:
                continue
            
            nalichie_lineynaya = 0
            store = {}
            nalichie_obzhee = 0
            for el in detail["storage"]:
                #Проверка для ZZap и spl
                amount = str(el["amount"])
                if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
                    if amount[0] != "-":
                        if amount.find("\xa0") > 0:
                            nalichie_lineynaya += round(float(amount[:amount.find("\xa0")]))
                            store[el["namestorage"]] = nalichie_lineynaya
                        else:
                            nalichie_lineynaya += round(float(amount.replace(",",".")))
                            store[el["namestorage"]] = nalichie_lineynaya
                #Для Drom и 2gis
                else:
                    if amount[0] == "-":
                        store[el["namestorage"]] = 0
                        continue
                    if amount.find("\xa0") > 0:
                        count = round(float(amount[:amount.find("\xa0")]))
                        if el["namestorage"] in store.keys():
                            store[el["namestorage"]] += count
                        else:
                            store[el["namestorage"]] = count
                    else:
                        count = round(float(amount.replace(',','.')))
                        if el["namestorage"] in store.keys():
                            store[el["namestorage"]] += count
                        else:
                            store[el["namestorage"]] = count
                    nalichie_obzhee += count    
                
                nalichie_obzhee += nalichie_lineynaya
            
            if nalichie_lineynaya == 0:
                spl_check = False
                zzap_check = False
            
            if nalichie_obzhee == 0:
                drom_check = False
                gis_check = False
                avito_check = False
            
            links = pic_links(detail["images"])
            
            if spl_check: 
                data_for_spl.append([
                    category_names[category],
                    detail["article"],
                    detail["code"],
                    detail["title"],
                    detail["price"],
                    nalichie_lineynaya,
                    nalichie_lineynaya,
                    detail["price"],
                    links
                ])
                
            if gis_check: 
                data_for_2gis.append([
                    str(date.today()),
                    category_names[category],
                    detail["article"],
                    BASE_URL + detail["uri"],
                    detail["title"],
                    detail["code"],
                    detail["external_id"],
                    detail["title"],
                    detail["price"],
                    nalichie_obzhee,
                    store.get("г.Челябинск, ул.Линейная, 98", 0),
                    store.get("г.Челябинск, Троицкий тр., 66", 0),
                    store.get("г.Магнитогорск, ул.Кирова, 100", 0),
                    store.get("г.Магнитогорск, ул.Заводская, 1/2", 0),
                    store.get("г.Красноярск, ул. 2-я Брянская, 34, стр. 2", 0),
                    links    
                ])
    
            if drom_check: 
                data_for_drom.append([
                    category_names[category],
                    detail["article"],
                    '<p>Запчасти для грузовиков и спецтехники в наличии более 150 000 наименований.</p><br><p>Оплата: наличными, онлайн-оплата на сайте или платеж по счету.</p><p>Купон AVITO5 на скидку 5% при заказе с сайта tdbovid.</p><br><p>Доставим за 4 часа или отправим по всей России.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><br><p>Самовывоз со склада по адресам:</p><ul><li>г. Челябинск ул. Линейная, 98;</li><li>г. Челябинск, ул.Троицкий тракт, 66.</li></ul><br><p>Если в нашем магазине на Авито не нашлась нужная запчасть, комплект, машинокомплект, то это не значит, что ее нет на наших складах. Запчастей для грузовиков более 150 000 наименований. Методов их подбора много. Просто позвоните или напишите нам, мы обязательно подберем нужную запчасть быстро и по привлекательной цене.</p><br><p>Компания ТД БОВИД являемся одним из крупнейших поставщиков в России и официальным дилером АО «Автомобильный завод «УРАЛ», ПАО</p><p>«КАМАЗ», ПАО «Автодизель», АО «ЯЗДА», ООО «УАЗ», ООО</p><p>«ИВЕКО-АМТ», ООО «Автоцентр ОСВАР», АО «Гидросила М»,</p><p>представителем 35 отечественных заводов-изготовителей, а также</p><p>IVECO, VOLVO, RENAULT TRUCKS и спецтехнике KOMATSU, HITACHI, </p><p>CATERPILLAR.</p></ul>',
                    detail["code"],
                    detail["title"],
                    detail["price"],
                    nalichie_obzhee,
                    store.get("г.Челябинск, ул.Линейная, 98", 0),
                    store.get("г.Челябинск, Троицкий тр., 66", 0),
                    store.get("г.Магнитогорск, ул.Кирова, 100", 0),
                    store.get("г.Магнитогорск, ул.Заводская, 1/2", 0),
                    store.get("г.Красноярск, ул. 2-я Брянская, 34, стр. 2", 0),
                    links
                ])
            
            #Проверка для avito
            if detail["price"] <= 500:
                avito_check = False                    
            replace_values = ['*', '(', ')', '.', ',', ';', '№', '/', '–', '#', '=', '"', '-']
            a = detail["article"]
            for rv in replace_values:
                a = a.replace(rv, ' ') 
            if avito_check: 
                data_for_avito.append([
                    detail["external_id"],
                    'Package',
                    'Free',
                    'Да',
                    'Светлана Жданова',
                    '+7 (351) 200-27-46',
                    'Россия, Челябинская область, Челябинск, Линейная улица, 98',
                    'Москва и Московская область | Москва и Московская область, Москва | Санкт-Петербург и Ленинградская область | Санкт-Петербург и Ленинградская область, Санкт-Петербург | Башкортостан | Башкортостан, Уфа | Курганская область | Курганская область, Курган | Оренбургская область | Оренбургская область, Оренбург | Пермский край | Пермский край, Пермь | Самарская область, Самара | Самарская область | Свердловская область | Свердловская область, Екатеринбург | Татарстан | Татарстан, Казань | Тюменская область | Тюменская область, Тюмень | Челябинская область | Челябинская область, Челябинск | Челябинская область, Агаповка | Челябинская область, Аргаяш | Челябинская область, Аша | Челябинская область, Бакал | Челябинская область, Бердяуш | Челябинская область, Бобровка | Челябинская область, Бреды | Челябинская область, Бродокалмак | Челябинская область, Варна | Челябинская область, Верхнеуральск | Челябинская область, Верхний Уфалей | Челябинская область, Вишневогорск | Челябинская область, Долгодеревенское | Челябинская область, Еманжелинка | Челябинская область, Еманжелинск | Челябинская область, Еткуль | Челябинская область, Зауральский | Челябинская область, Златоуст | Челябинская область, Канашево | Челябинская область, Карабаш | Челябинская область, Карталы | Челябинская область, Касли | Челябинская область, Катав-Ивановск | Челябинская область, Кизильское | Челябинская область, Коелга | Челябинская область, Копейск | Челябинская область, Коркино | Челябинская область, Красногорский | Челябинская область, Кропачево | Челябинская область, Кунашак | Челябинская область, Куса | Челябинская область, Кыштым | Челябинская область, Локомотивный | Челябинская область, Магнитка | Челябинская область, Магнитогорск | Челябинская область, Межевой | Челябинская область, Межозерный | Челябинская область, Миасс | Челябинская область, Миасское | Челябинская область, Миньяр | Челябинская область, Новогорный | Челябинская область, Новосинеглазовский | Челябинская область, Нязепетровск | Челябинская область, Озерск | Челябинская область, Октябрьское | Челябинская область, Первомайский | Челябинская область, Пласт | Челябинская область, Полетаево | Челябинская область, Роза | Челябинская область, Рощино | Челябинская область, Сатка | Челябинская область, Сим | Челябинская область, Снежинск | Челябинская область, Тимирязевский | Челябинская область, Трехгорный | Челябинская область, Троицк | Челябинская область, Тургояк | Челябинская область, Тюбук | Челябинская область, Увельский | Челябинская область, Уйское | Челябинская область, Усть-Катав | Челябинская область, Фершампенуаз | Челябинская область, Чебаркуль | Челябинская область, Чесма | Челябинская область, Южноуральск | Челябинская область, Юрюзань',
                    'Запчасти и аксессуары',
                    '6-406',
                    'Товар от производителя',
                    detail["title"],
                    '<p>Запчасти для грузовиков и спецтехники в наличии более 150 000 наименований.</p><br><p>Оплата: наличными, онлайн-оплата на сайте или платеж по счету.</p><p>Купон AVITO5 на скидку 5% при заказе с сайта tdbovid.</p><br><p>Доставим за 4 часа или отправим по всей России.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><p>Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др.</p><br><p>Самовывоз со склада по адресам:</p><ul><li>г. Челябинск ул. Линейная, 98;</li><li>г. Челябинск, ул.Троицкий тракт, 66.</li></ul><br><p>Если в нашем магазине на Авито не нашлась нужная запчасть, комплект, машинокомплект, то это не значит, что ее нет на наших складах. Запчастей для грузовиков более 150 000 наименований. Методов их подбора много. Просто позвоните или напишите нам, мы обязательно подберем нужную запчасть быстро и по привлекательной цене.</p><br><p>Компания ТД БОВИД являемся одним из крупнейших поставщиков в России и официальным дилером АО «Автомобильный завод «УРАЛ», ПАО</p><p>«КАМАЗ», ПАО «Автодизель», АО «ЯЗДА», ООО «УАЗ», ООО</p><p>«ИВЕКО-АМТ», ООО «Автоцентр ОСВАР», АО «Гидросила М»,</p><p>представителем 35 отечественных заводов-изготовителей, а также</p><p>IVECO, VOLVO, RENAULT TRUCKS и спецтехнике KOMATSU, HITACHI, </p><p>CATERPILLAR.</p></ul>',
                    detail["price"],
                    'Новое',
                    a,
                    links
                ])    
             
            if zzap_check: 
                data_for_zzap.append([
                    category_names[category],
                    detail["article"],
                    detail["title"],
                    detail["price"],
                    nalichie_lineynaya,
                    "0 дней",
                    links
                ])
            
        start += limit                        


def rees46_xml():
    start = 0
    limit = 1000
    yml_catalog = et.Element('yml_catalog')
    now = str(date.today()) + " " + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute)
    yml_catalog.set('date', now)
    shop = et.SubElement(yml_catalog, 'shop')
    name = et.SubElement(shop, 'name')
    name.text = 'Торговый Дом "БОВИД"'
    company = et.SubElement(shop, 'company')
    company.text = 'АО "Торговый Дом "БОВИД"'
    url = et.SubElement(shop, 'url')
    url.text = "https://tdbovid.ru"
    currencies = et.SubElement(shop, 'currencies')
    RUR = et.SubElement(currencies, 'currency')
    RUR.set('id', "RUR")
    RUR.set('rate', '1')
    categories = et.SubElement(shop, 'categories')
    for c in category_ids:
        category = et.SubElement(categories, 'category')
        category.set('id', str(category_ids[c]))
        category.text = c
    # Для Rees46
    locations = et.SubElement(shop, 'locations')
    for address in addresses:
        location = et.SubElement(locations, 'location')
        location.set('id', str(addresses.index(address) + 1))
        location.set('type', "store")
        location.set('name', address)
    offers = et.SubElement(shop, 'offers')
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            break
        for detail in details:
            if detail["code"] == None or detail["code"] == "":
                continue
            if len(detail["storage"]) == 0:
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            # Для возвращения на Сбер
            # for el in detail["storage"]:
            #     str_amount = str(el["amount"])
            #     if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
            #         if str_amount[0] != "-":
            #             if str_amount.find("\xa0") > 0:
            #                 nalichie += round(float(str_amount[:str_amount.find("\xa0")]))
            #             else:
            #                 nalichie += round(float(str_amount.replace(",",".")))
            # Для Rees46
            store = {}
            nalichie = 0
            for storage in detail["storage"]:
                amount = str(storage["amount"])
                if amount[0] == "-":
                    store[storage["namestorage"]] = 0
                    continue
                if amount.find("\xa0") > 0:
                    count = round(float(amount[:amount.find("\xa0")]))
                    if storage["namestorage"] in store.keys():
                        store[storage["namestorage"]] += count
                    else:
                        store[storage["namestorage"]] = count
                else:
                    count = round(float(amount.replace(',','.')))
                    if storage["namestorage"] in store.keys():
                        store[storage["namestorage"]] += count
                    else:
                        store[storage["namestorage"]] = count
                nalichie += count    
            if nalichie == 0 or nalichie == 0.0 or str(nalichie) == "":
                continue
            splited_url = list(filter(None, detail["uri"].split('/')))
            if splited_url[1] in category_names.keys():
                detail_category = category_names[splited_url[1]]
            else:
                continue
            if detail_category == "Распродажа":
                continue
            if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                continue                 
            external_id = detail["external_id"]
            offer = et.SubElement(offers, 'offer')
            offer.set('id', external_id.replace("-","")[:20])
            offer.set('available', "true")
            auto = et.SubElement(offer, 'auto')
            detail_url = et.SubElement(offer, 'url')
            detail_url.text = BASE_URL + detail["uri"]
            detail_name = et.SubElement(offer, 'name')
            detail_name.text = detail["title"]
            price = et.SubElement(offer, 'price')
            price.text = str(detail["price"])
            categoryId = et.SubElement(offer, 'categoryId')
            categoryId.text = str(category_ids[detail_category])
            detail_locations = et.SubElement(offer, 'locations')
            for key in store.keys():
                detail_location = et.SubElement(detail_locations, 'location')
                detail_location.set('id', str(addresses.index(key) + 1))
                stock_quantity = et.SubElement(detail_location, 'stock_quantity')
                stock_quantity.text = str(store.get(key))
            pic_linki = list(filter(None, pic_links(detail["images"]).split(',')))
            if len(pic_linki) > 0:
                for pic in pic_linki:
                    pic = pic.strip()
                    picture = et.SubElement(offer, 'picture')
                    picture.text = pic
            vendor = et.SubElement(offer, 'vendor')
            vendor.text = detail_category
            vendor_code = et.SubElement(offer, 'vendorCode')
            vendor_code.text = detail["article"]
            description = et.SubElement(offer, 'description')
            description.text = detail["title"]
            # Для сбера
            # outlets = et.SubElement(offer, 'outlets')
            # outlet = et.SubElement(outlets, 'outlet')
            # outlet.set('id', "1")
            # outlet.set('instock', str(nalichie))
            # if len(detail["article"]) > 1:
            #     artikul = et.SubElement(offer, "param")
            #     artikul.set("name", 'Артикул')
            #     artikul.text = str(detail["article"])
            # kod = et.SubElement(offer, 'param')
            # kod.set("name", 'Код')
            # kod.text = str(detail["code"])
            # if detail_category == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370" or detail_category == "Урал" or detail_category == "КАМАЗ" or detail_category == "ЯМЗ":
            #     country_of_origin = et.SubElement(offer, 'param')
            #     country_of_origin.set('name', "Страна-изготовитель")
            #     country_of_origin.text = "Россия"
                
        start += limit
    f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
    tree._setroot(et.fromstring(f_str))
    tree.write("Rees46.xml", encoding = "UTF-8", xml_declaration = True)            
                

def sberMarket_xls():
    fields = ["id", "Доступность товара", "Категория", "Производитель", "Артикул", "Модель", "Название", "Цена", "Остаток", "НДС", "Ссылки на картинки"]
    start = 0
    limit = 1000
    workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_sber.xlsx")
    worksheet = workbook.add_worksheet()
    write_column_names(worksheet, fields)
    data_for_sber = []
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            write_data(worksheet, 1, data_for_sber, len(fields))
            workbook.close()   
            break
        for detail in details:
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            if len(detail["storage"]) == 0:
                continue 
            vendor_in_url = list(filter(None, detail["uri"].split('/')))[1]
            if vendor_in_url in category_names.keys():
                vendor = category_names[vendor_in_url]
            else:
                continue
            nalichie = 0
            title = detail["title"]
            if title.find("...") > 0:
                title = title.replace("...", "")
            if vendor == "Распродажа":
                continue
            if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                continue 
            for el in detail["storage"]:
                amount = str(el["amount"])
                if el["codestorage"] == "00006" or el["codestorage"] == "00008":
                    if amount[0] != "-":
                        if amount.find("\xa0") > 0:
                            count = round(int(amount[:amount.find("\xa0")]))
                            nalichie += count
                        else:
                            nalichie += el["amount"]
            if nalichie == 0:
                continue
            price = detail["price"] * 1.05
            links = pic_links(detail["images"])
            # if links == "":
            #     continue
            data_for_sber.append([
                    detail["code"],
                    "Доступен",
                    "Автозапчасти для грузовиков",
                    vendor,
                    detail["article"],
                    title,
                    title,
                    price,
                    nalichie,
                    20,
                    links
                ])
        start += limit
        

def sber_shablon():
    start = 0
    limit = 1000
    data = []
    fields = ["Offer_id", "GTIN", "Name", "Vendor", "Code", "URL main photo", 
              "URL photo 2", "URL photo 3", "URL photo 4", "URL photo 5", 
              "URL photo 6", "URL photo 7", "URL photo 8", "URL photo 9", 
              "URL photo 10", "Article"]
    workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_sberShablon.xlsx")
    worksheet = workbook.add_worksheet()
    write_column_names(worksheet, fields)
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            write_data(worksheet, 1, data, len(fields))
            workbook.close()
            break
        for detail in details:
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            if len(detail["storage"]) == 0:
                continue 
            vendor_in_url = list(filter(None, detail["uri"].split('/')))[1]
            if vendor_in_url in category_names.keys():
                vendor = category_names[vendor_in_url]
            else:
                continue
            nalichie = 0
            title = detail["title"]
            if title.find("...") > 0:
                title = title.replace("...", "")
            if vendor == "Распродажа":
                continue
            if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                continue 
            for el in detail["storage"]:
                amount = str(el["amount"])
                if el["codestorage"] == "00006" or el["codestorage"] == "00008":
                    if amount[0] != "-":
                        if amount.find("\xa0") > 0:
                            count = round(int(amount[:amount.find("\xa0")]))
                            nalichie += count
                        else:
                            nalichie += el["amount"]
            if nalichie == 0:
                continue
            main_photo = ""
            other_photos = []
            for pic in detail["images"]:
                if pic["parent"] == 0 and pic["url"].find("small") == -1 and pic["url"].find("medium") == -1:
                    main_photo = BASE_URL + pic["url"]
                elif pic["url"].find("small") == -1 and pic["url"].find("medium") == -1:
                    other_photos.append(BASE_URL + pic["url"])
            while len(other_photos) < 9:
                other_photos.append("")
            data.append([
                detail["id"],
                create_EAN13(str(detail["id"])),
                title,
                vendor,
                detail["code"],
                main_photo,
                other_photos[0],
                other_photos[1],
                other_photos[2],
                other_photos[3],
                other_photos[4],
                other_photos[5],
                other_photos[6],
                other_photos[7],
                other_photos[8],
                detail["article"]
                ])
        start += limit            
            
    
def create_EAN13(detail_id):    
    while len(detail_id) < 11:
        detail_id = "0" + detail_id
    detail_id = "1" + detail_id
    index = 0
    chetnie = 0
    nechetnie = 0
    for i in detail_id:
        if index in (1,3,5,7,9,11):
            chetnie += int(i)
        else:
            nechetnie += int(i)
        index += 1
    result = chetnie * 3 + nechetnie
    if result != 0:
        thirteen_char = 10 - (result % 10)
    else:
        thirteen_char = 0
    detail_id = detail_id + str(thirteen_char)
    return detail_id
    

def cfk():
    #Файл остатки - IDТовара(Код), Наименование, IDСклада(только 00006), ОстатокНаСкладе, СрокПоставки
    #Файл цены - IDТовара(Код), Наименование, ЦенаБезНДС, СтавкаНДС, ЦенаСНДС, КодВалюты, КодЕдиницыИзмерения
    start = 0
    limit = 1000
    pricelist = []
    leftover = [] 
    price_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_cfkPrice.xlsx")
    leftover_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_cfkLeftover.xlsx")
    price_worksheet = price_workbook.add_worksheet()
    leftover_worksheet = leftover_workbook.add_worksheet()
    write_column_names(price_worksheet, fields_for_cfk_price)
    write_column_names(leftover_worksheet, fields_for_cfk_leftover)
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            write_data(price_worksheet, 1, pricelist, len(fields_for_cfk_price))
            write_data(leftover_worksheet, 1, leftover, len(fields_for_cfk_leftover))
            price_workbook.close()
            leftover_workbook.close()
            break
        for detail in details:
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            if len(detail["storage"]) == 0:
                continue 
            vendor_in_url = list(filter(None, detail["uri"].split('/')))[1]
            if vendor_in_url in category_names.keys():
                vendor = category_names[vendor_in_url]
            else:
                continue
            nalichie = 0
            title = detail["title"]
            if title.find("...") > 0:
                title = title.replace("...", "")
            if vendor == "Распродажа":
                continue
            if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                continue 
            for store in detail["storage"]:
                if store["codestorage"] == "00006":
                    nalichie = store["amount"]
            if nalichie == 0:
                continue
            leftover.append([
                detail["code"],
                detail["title"],
                "00006",
                nalichie,
                "45"
                ])
            pricelist.append([
                detail["code"],
                detail["title"],
                detail["price"],
                "20",
                round(detail["price"] * 1.2, 2),
                "643",
                "796"
                ])
            
        start += limit


def avtopiter_armtek():
    start = 0
    limit = 1000
    avtopiter_fields = ["Производитель", "Артикул", "Наименование", "Цена", "Остатки"]
    avtopiter_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_avtopiter.xlsx")
    avtopiter_worksheet = avtopiter_workbook.add_worksheet()
    write_column_names(avtopiter_worksheet, avtopiter_fields)
    avtopiter_data = []
    while True:
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            write_data(avtopiter_worksheet, 1, avtopiter_data, len(avtopiter_fields))
            avtopiter_workbook.close()
            break
        for detail in details:
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            if len(detail["storage"]) == 0:
                continue 
            vendor_in_url = list(filter(None, detail["uri"].split('/')))[1]
            if vendor_in_url in category_names.keys():
                vendor = category_names[vendor_in_url]
            else:
                continue
            nalichie = 0
            title = detail["title"]
            if title.find("...") > 0:
                title = title.replace("...", "")
            if vendor == "Распродажа" or vendor == "Автошины" or vendor == "Т-150" or vendor == "ЮМЗ" or vendor == "Прицепы" or vendor == "Экскаватор" or vendor == "Радиаторы ЛРЗ" or vendor == "Т-40" or vendor == "Автокраны и КМУ" or vendor == "ДТ-75" or vendor == "РВД" or vendor == "Фильтры и комплекы прокладок МОТОРДЕТАЛЬ" or vendor == "ДЗ-98;ДЗ-180" or vendor == "Автобусы" or vendor == "Подшипники" or vendor == "Легковые иномарки" or vendor == "Прочие" or vendor == "Электрооборудование":
                continue
            if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                continue 
            for storage in detail["storage"]:
                if storage["codestorage"] == "00006" or storage["codestorage"] == "00008":
                    nalichie = storage["amount"]
            if nalichie == 0:
                continue
            if detail["article"] in fail_articles:
                continue
            if vendor == "Урал" or vendor == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370":
                vendor = "УРАЛАЗ"
            if vendor == "ГАЗ грузовой" or vendor == "ГАЗ легковой":
                vendor = "ГАЗ"
            avtopiter_data.append([
                vendor,
                detail["article"],
                title,
                detail["price"],
                nalichie
                ])
        
        start += limit
            
    
def main():
    start = datetime.now()
    obzhee()
    print("Общий метод завершил работу")
    avtopiter_armtek()
    print("Автопитер готов")
    yandex_new(session)
    print("Yandex метод завершил работу")
    # sberMarket_xls()
    # sber_shablon()
    # print("Сбер готов")
    cfk()
    print("Файлы для ЦФК готовы")
    rees46_xml()
    print("XML для Rees46 готова")
    total = (datetime.now() - start).total_seconds()
    print("Общее время - " + str(int(total//3600)) + ":" + str(int((total % 3600)//60)) + ":" + str(round(total % 60)))
    

def test():
    start = datetime.now()
    aa = AA("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_autopiter.xlsx", fields_for_autopiter)
    aa.get_xlsx()    
    gis = TwoGis("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_2gis.xlsx", fields_for_2gis)
    gis.get_xlsx()
    zzap = ZZap("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_zzap.xlsx", fields_for_zzap)
    zzap.get_xlsx()    
    avito = Avito("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_avito.xlsx", fields_for_avito)
    avito.get_xlsx()
    cfk = Cfk("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_cfkPrice.xlsx", 
              "D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_cfkLeftover.xlsx", 
              fields_for_cfk_price, fields_for_cfk_leftover)
    cfk.get_xlsx()
    drom = Drom("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_drom.xlsx", fields_for_drom)
    drom.get_xlsx()
    spl = SPL("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_spl.xlsx", fields_for_spl)
    spl.get_xlsx()  
    rees = Rees46("D:/parsing/Rees46.xml")
    rees.get_xml()
    yandex = Yandex("D:/parsing/yandex.xml")
    yandex.get_xml(False)
    yandex_direct = Yandex("D:/parsing/yandex_direct.xml")
    yandex_direct.get_xml(True)
    yandex.get_published_count()
    yandex.download_images()
    total = (datetime.now() - start).total_seconds()
    print("Общее время - " + str(int(total//3600)) + ":" + str(int((total % 3600)//60)) + ":" + str(round(total % 60)))

          
if __name__ == "__main__":
    test()    


# function foo(){
#     let x = 0;
#     return function() {
#         return x++;
#     }
# }
    
# let bar = foo();
# let baz = foo();
# bar() //0
# bar() //1
# baz() //0
# bar() //2
# baz() //1
    
    
    
    
    
    
    