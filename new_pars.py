import requests
from requests.adapters import HTTPAdapter
from datetime import date
import xlsxwriter as xl
from yandex_market import yandex_new

categories = {"ural":"Урал","ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":"УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370",
              "yamz":"ЯМЗ","kamaz":"КАМАЗ","maz":"МАЗ","uaz":"УАЗ","elektrooborudovanie":"Электрооборудование","gaz-gruzovoj":"ГАЗ грузовой",
              "gaz-legkovoj":"ГАЗ легковой","gidrosila":"Гидросила","porschnevaya-gruppa":"Поршневая группа","zil":"ЗИЛ","avtoshiny":"Автошины",
              "cat":"CAT","hitachi":"Hitachi","hyundai":"HYUNDAI","iveco":"IVECO","komatsu":"KOMATSU","avtobusy":"Автобусы","avtokrany-i-kmu":"Автокраны и КМУ",
              "akkumulyatory":"Аккумуляторы","vaz":"ВАЗ","dz-98-dz-180":"ДЗ-98;ДЗ-180","dt-75":"ДТ-75","instrument":"Инструмент",
              "legkovye-inomarkigruzovye-inomarkikommercheskij-transport":"Легковые иномарки","mtz":"МТЗ","pogruzchiki":"Погрузчики",
              "podshipniki":"Подшипники","porschnevaya-gruppa-vaz-motordetal":"Поршневая группа ВАЗ Мотордеталь","porschnevaya-gruppa-urkaina":"Поршневая группа Украина",
              "pricepy":"Прицепы","prochie":"Прочие","radiatory-lrz":"Радиаторы ЛРЗ","rvd":"РВД","t-150":"Т-150","t-170":"Т-170","t-40":"Т-40",
              "filtry-i-komplekty-prokladok-motordetal":"Фильтры и комплекты прокладок МОТОРДЕТАЛЬ","shaaz":"ШААЗ","ekskavator":"Экскаватор",
              "yumz":"ЮМЗ","rasprodazha":"Распродажа"}
fields_for_spl = ["Производитель", "Артикул", "Код", "Название", 
                      "Цена для всех складов", "Общее количество деталей в наличии", 
                      "г.Челябинск, ул.Линейная 98", "г.Челябинск, ул.Линейная 98, цена", 
                      "Ссылки на изображения"]
stop_categories = ["Автошины", "ВАЗ", "УАЗ", "ГАЗ легковой", "Инструмент", 
                           "Легковые иномарки", "Поршневая группа", "Поршневая группа ВАЗ Мотордеталь", 
                           "Поршневая группа Мотордеталь", "Поршневая группа Украина", "Прочие", "Распродажа"]
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
URL = 'https://tdbovid.ru/katalog_zapchastej'
BASE_URL = 'https://tdbovid.ru'
today = str(date.today()).split('-')
tdbovid_adapter = HTTPAdapter(max_retries=5)
session = requests.Session()
session.mount(BASE_URL, tdbovid_adapter)              
        

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
    spl_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_spl_test.xlsx")
    spl_worksheet = spl_workbook.add_worksheet()
    gis_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_2gis_test.xlsx")
    gis_worksheet = gis_workbook.add_worksheet()
    drom_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_drom_test.xlsx")
    drom_worksheet = drom_workbook.add_worksheet()
    avito_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_avito_test.xlsx")
    avito_worksheet = avito_workbook.add_worksheet()
    zzap_workbook = xl.Workbook("D:/parsing/tdbovid_" + today[2] + '_' + today[1] + '_' + today[0][2:] + "_zzap_test.xlsx")
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
            if detail["code"] == None or detail["code"] == "":
                continue
            if len(detail["storage"]) == 0:
                continue 
            
            category = detail["uri"].split('/')[1]
            #Проверка spl
            if category in categories.keys():
                if categories[category] in stop_categories:
                    spl_check = False
            
            nalichie_lineynaya = 0
            store = {}
            nalichie_obzhee = 0
            for el in detail["storage"]:
                #Проверка для ZZap и spl
                if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
                    if el["amount"][0] != "-":
                        if el["amount"].find("\xa0") > 0:
                            nalichie_lineynaya = round(float(el["amount"][:el["amount"].find("\xa0")]))
                            store[el["namestorage"]] = nalichie_lineynaya
                            nalichie_obzhee += nalichie_lineynaya
                        else:
                            nalichie_lineynaya = round(float(el["amount"].replace(",",".")))
                            store[el["namestorage"]] = nalichie_lineynaya
                            nalichie_obzhee += nalichie_lineynaya
                #Для Drom и 2gis
                else:
                    if el["amount"][0] == "-":
                        store[el["namestorage"]] = 0
                        continue
                    if el["amount"].find("\xa0") > 0:
                        count = round(float(el["amount"][:el["amount"].find("\xa0")]))
                        store[el["namestorage"]] = count
                    else:
                        count = round(float(el["amount"].replace(',','.')))
                        store[el["namestorage"]] = count
                    nalichie_obzhee += count    
            
            if nalichie_lineynaya == 0:
                spl_check = False
                zzap_check = False
            
            if nalichie_obzhee == 0:
                drom_check = False
                gis_check = False
                
            if category in categories.keys() and spl_check: 
                data_for_spl.append([
                    categories[category],
                    detail["article"],
                    detail["code"],
                    detail["title"],
                    detail["price"],
                    nalichie_lineynaya,
                    nalichie_lineynaya,
                    detail["price"],
                    pic_links(detail["images"])
                ])
                
            if category in categories.keys() and gis_check: 
                data_for_2gis.append([
                    str(date.today()),
                    categories[category],
                    detail["article"],
                    BASE_URL + '/' + detail["uri"],
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
                    pic_links(detail["images"])    
                ])
    
            if category in categories.keys() and drom_check: 
                data_for_drom.append([
                    categories[category],
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
                    pic_links(detail["images"])
                ])
            
            #Проверка для avito
            if detail["price"] <= 500:
                avito_check = False                    
            replace_values = ['*', '(', ')', '.', ',', ';', '№', '/', '–', '#', '=', '"', '-']
            a = detail["article"]
            for rv in replace_values:
                a = a.replace(rv, ' ') 
            if category in categories.keys() and avito_check: 
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
                    pic_links(detail["images"])
                ])    
             
            if category in categories.keys() and zzap_check: 
                data_for_zzap.append([
                    categories[category],
                    detail["article"],
                    detail["title"],
                    detail["price"],
                    count,
                    "0 дней",
                    pic_links(detail["images"])
                ])
            
        start += limit                        


def main():
    obzhee()
    print("Общий метод завершил работу")
    yandex_new(session)
    print("Yandex метод завершил работу")   

def test():
    a = "/katalog-zapchastej/ural-63685-636746563-dorozhnaya-gamma-i-ural-6370/amortizator-kabiny-perednij-30-5001010-3374122070"
    b = list(filter(None, a.split('/')))
    for el in b:
        print(str(b.index(el)) + " " + el)
        
if __name__ == "__main__":
    main()    
    
    
    
    
    
    
    
    
    
    
    