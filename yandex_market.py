import sqlite3
import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ElementTree
from datetime import date
from xml.dom import minidom
import wget

BASE_URL = 'https://tdbovid.ru'
today = str(date.today()).split('-')
filename = 'tdbovid_' + today[2] + '_' + today[1] + '_' + today[0][2:] + '_2gis.db'
category_ids = {"Автобусы": 1, "Автокраны и КМУ": 2, "Автошины": 3, "Аккумуляторы": 4, "ВАЗ": 5, "ГАЗ грузовой": 6, "ГАЗ легковой": 7, "Гидросила": 8, "ДЗ-98; ДЗ-180": 9, "ДТ-75": 10, 
                "ЗИЛ": 11, "Инструмент": 12, "КАМАЗ": 13, "Легковые иномарки": 14, "МАЗ": 15, "МТЗ": 16, "Погрузчики": 17, "Подшипники": 18, "Поршневая группа": 19, "Поршневая группа ВАЗ Мотордеталь": 20, 
                "Поршневая группа Мотордеталь": 21, "Поршневая группа Украина": 22, "Прицепы": 23, "Прочие ": 24, "РВД": 25, "Радиаторы ЛРЗ": 26, "Т-150": 27, "Т-170": 28, "Т-40": 29, "УАЗ": 30, 
                "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370": 31, "Урал": 32, "Фильтры и комплекты прокладок МОТОРДЕТАЛЬ": 33, "ШААЗ": 34, "Экскаватор": 35, "Электрооборудование": 36, "ЮМЗ": 37, "ЯМЗ": 38, "CAT": 39, "HYUNDAI": 40, 
                "Hitachi": 41, "IVECO": 42, "KOMATSU": 43}
category_names = {"ural":"Урал","ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":"УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370",
              "yamz":"ЯМЗ","kamaz":"КАМАЗ","maz":"МАЗ","uaz":"УАЗ","elektrooborudovanie":"Электрооборудование","gaz-gruzovoj":"ГАЗ грузовой",
              "gaz-legkovoj":"ГАЗ легковой","gidrosila":"Гидросила","porschnevaya-gruppa":"Поршневая группа","zil":"ЗИЛ","avtoshiny":"Автошины",
              "cat":"CAT","hitachi":"Hitachi","hyundai":"HYUNDAI","iveco":"IVECO","komatsu":"KOMATSU","avtobusy":"Автобусы","avtokrany-i-kmu":"Автокраны и КМУ",
              "akkumulyatory":"Аккумуляторы","vaz":"ВАЗ","dz-98-dz-180":"ДЗ-98; ДЗ-180","dt-75":"ДТ-75","instrument":"Инструмент",
              "legkovye-inomarkigruzovye-inomarkikommercheskij-transport":"Легковые иномарки","mtz":"МТЗ","pogruzchiki":"Погрузчики",
              "podshipniki":"Подшипники","porschnevaya-gruppa-vaz-motordetal":"Поршневая группа ВАЗ Мотордеталь","porschnevaya-gruppa-urkaina":"Поршневая группа Украина",
              "pricepy":"Прицепы","prochie":"Прочие ","radiatory-lrz":"Радиаторы ЛРЗ","rvd":"РВД","t-150":"Т-150","t-170":"Т-170","t-40":"Т-40",
              "filtry-i-komplekty-prokladok-motordetal":"Фильтры и комплекты прокладок МОТОРДЕТАЛЬ","shaaz":"ШААЗ","ekskavator":"Экскаватор",
              "yumz":"ЮМЗ","rasprodazha":"Распродажа"}
tree = ElementTree()

def get_data_from_base():
    conn = sqlite3.connect('D:/parsing/dbs/' + filename)
    c = conn.cursor()
    c.execute('PRAGMA encoding = "UTF-8"')
    for_yandex = 'SELECT name, artikl, item_url, price, category, pic_link, baza_store, uid, kod FROM tdbovid where price > 0 and baza_store != 0'
    # for_avito = 'SELECT uid, name, price, artikl FROM tdbovid WHERE price >= 500 AND (baza_store is not NULL OR tr_tr_store is not NULL) AND (artikl NOT LIKE "%#(%" ESCAPE "#" OR artikl NOT LIKE "%#*%" ESCAPE "#" OR artikl NOT LIKE "%#.%" ESCAPE "#" OR artikl NOT LIKE "%#,%" ESCAPE "#"  OR artikl NOT LIKE "%#;%" ESCAPE "#" OR artikl NOT LIKE "%#–%" ESCAPE "#" OR artikl NOT LIKE "%#№%" ESCAPE "#" OR artikl NOT LIKE "%#=%" ESCAPE "#" OR artikl NOT LIKE "%#/%" ESCAPE "#" OR artikl NOT LIKE "%##%" ESCAPE "#" OR artikl NOT LIKE "%""%")'
    c.execute(for_yandex)
    yandex = c.fetchall()
    print("Запчастей " + str(len(yandex)) + " шт.")
    conn.commit()
    conn.close()
    return yandex


def yandex_old(from_db):
    yml_catalog = et.Element('yml_catalog')
    yml_catalog.set("date", str(date.today()))
    shop = et.SubElement(yml_catalog, 'shop')
    name = et.SubElement(shop, 'name')
    name.text = 'Торговый Дом "БОВИД"'
    company = et.SubElement(shop, 'company')
    company.text = 'АО "Торговый Дом "БОВИД"'
    url = et.SubElement(shop, 'url')
    url.text = "https://tdbovid.ru"
    platform = et.SubElement(shop, 'platform')
    platform.text = "MODX Revo"
    version = et.SubElement(shop, 'version')
    version.text = "2.8.1"
    agency = et.SubElement(shop, 'agency')
    agency.text = 'Торговый Дом "БОВИД"'
    email = et.SubElement(shop, 'email')
    email.text = "zakaz@bovid.ru"
    currencies = et.SubElement(shop, 'currencies')
    RUR = et.SubElement(currencies, 'currency')
    RUR.set('id', "RUR")
    RUR.set('rate', '1')
    categories = et.SubElement(shop, 'categories')
    
    for c in category_ids:
        category = et.SubElement(categories, 'category')
        category.set('id', str(category_ids[c]))
        category.text = c
    
    offers = et.SubElement(shop, 'offers')
    
    for el in from_db:
        if el[6] > 0:
            offer = et.SubElement(offers, 'offer')
            offer.set("id", el[7].replace("-","")[:20])
            name = et.SubElement(offer, 'name')
            name.text = el[0]
            vendorCode = et.SubElement(offer, 'vendorCode')
            vendorCode.text = str(el[1])
            url = et.SubElement(offer, 'url')
            url.text = el[2]
            price = et.SubElement(offer, 'price')
            if el[3] == 0 or el[3] == 0.0:
                price.text = "Уточняйте у продавца"
            else:    
                price.text = str(el[3])
            currencyId = et.SubElement(offer, 'currencyId')
            currencyId.text = "RUR"
            categoryId = et.SubElement(offer, 'categoryId')
            categoryId.text = str(category_ids[el[4]])
            if el[4] == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370" or el[4] == "Урал" or el[4] == "КАМАЗ" or el[4] == "ЯМЗ":
                country_of_origin = et.SubElement(offer, 'country_of_origin')
                country_of_origin.text = "Россия"
            
            pic_links = list(filter(None, el[5].split(",")))
            i = 0
            if len(pic_links) > 0:           
                for pic in pic_links:
                    if i <= 9:
                        if os.stat("D:/parsing/pic/" + el[7] + "_" + str(i) + ".jpeg").st_size/(1024*1024) < 5:
                            picture = et.SubElement(offer, 'picture')
                            picture.text = pic
                        elif os.stat("D:/parsing/pic/" + el[7] + "_" + str(i) + ".jpeg").st_size/(1024*1024) >= 5 and len(pic_links) == 1:
                            picture = et.SubElement(offer, 'picture') 
                    i += 1 
            else:
                picture = et.SubElement(offer, 'picture') 
            
            pickup = et.SubElement(offer, 'pickup')
            pickup.text = "true"
            delivery = et.SubElement(offer, 'delivery')
            delivery.text = "true"
            store = et.SubElement(offer, 'store')
            store.text = "true"
            sposobi_oplati = et.SubElement(offer, 'sales_notes')
            sposobi_oplati.text = "Наличные, онлайн-оплата на сайте или платеж по счету."
            dostavka = et.SubElement(offer, "sales_notes")
            dostavka.text = "Доставка оплачивается отдельно."
            sroki_dostavki = et.SubElement(offer, "sales_notes")
            sroki_dostavki.text = "Доставим за 4 часа или отправим по всей России."
            sposobi_dostavki = et.SubElement(offer, "sales_notes")
            sposobi_dostavki.text = "Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др."
            predoplata = et.SubElement(offer, 'sales_notes')
            predoplata.text = "Необходима предоплата 100%."
            description = et.SubElement(offer, "description")
            description.text = """<p>Компания ТД БОВИД являемся одним из крупнейших поставщиков в России и официальным дилером АО «Автомобильный завод «УРАЛ», ПАО</p>
            <p>«КАМАЗ», ПАО «Автодизель», АО «ЯЗДА», ООО «УАЗ», ООО</p><p>«ИВЕКО-АМТ», ООО «Автоцентр ОСВАР», АО «Гидросила М»,</p>
            <p>представителем 35 отечественных заводов-изготовителей, а также</p>
            <p>IVECO, VOLVO, RENAULT TRUCKS и спецтехнике KOMATSU, HITACHI, </p><p>CATERPILLAR.</p>"""
            proizvoditel = et.SubElement(offer, "param")
            proizvoditel.set("name", "Производитель")
            proizvoditel.text = el[4]
            if len(el[1]) > 1:
                artikul = et.SubElement(offer, "param")
                artikul.set("name", "Артикул")
                artikul.text = el[1]
            kod = et.SubElement(offer, "param")
            kod.set("name", "Код")
            kod.text = el[8]
            count = et.SubElement(offer, 'count')
            count.text = str(el[6])
    f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
    tree._setroot(et.fromstring(f_str))
    tree.write("yandex с сайта.xml", encoding = "UTF-8", xml_declaration = True)


def yandex_new(session):
    start = 0
    limit = 1000
    yml_catalog = et.Element('yml_catalog')
    yml_catalog.set("date", str(date.today()))
    shop = et.SubElement(yml_catalog, 'shop')
    name = et.SubElement(shop, 'name')
    name.text = 'Торговый Дом "БОВИД"'
    company = et.SubElement(shop, 'company')
    company.text = 'АО "Торговый Дом "БОВИД"'
    url = et.SubElement(shop, 'url')
    url.text = "https://tdbovid.ru"
    platform = et.SubElement(shop, 'platform')
    platform.text = "MODX Revo"
    version = et.SubElement(shop, 'version')
    version.text = "2.8.1"
    agency = et.SubElement(shop, 'agency')
    agency.text = 'Торговый Дом "БОВИД"'
    email = et.SubElement(shop, 'email')
    email.text = "zakaz@bovid.ru"
    currencies = et.SubElement(shop, 'currencies')
    RUR = et.SubElement(currencies, 'currency')
    RUR.set('id', "RUR")
    RUR.set('rate', '1')
    categories = et.SubElement(shop, 'categories')    
    
    for c in category_ids:
        category = et.SubElement(categories, 'category')
        category.set('id', str(category_ids[c]))
        category.text = c
    
    offers = et.SubElement(shop, 'offers')
    
    while True:
        #el[0] - name, el[1] - artikl, el[2] - item_url, el[3] - price, el[4] - category, 
        #el[5] - pic_link, el[6] - baza_store, el[7] - uid, el[8] - kod
        details = session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
        if len(details) == 0:
            break;
        for detail in details:
            amount = 0
            if detail["searchable"] == 0 or detail["published"] == 0:
                continue
            if detail["code"] == None or detail["code"] == "":
                continue
            if len(detail["storage"]) == 0:
                continue
            if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                continue
            for el in detail["storage"]:
                if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
                    str_amount = str(el["amount"])
                    if str_amount != "-":
                        if str_amount.find("\xa0") > 0:
                            amount = round(float(str_amount[:str_amount.find("\xa0")]))
                        else:
                            amount = round(float(str_amount.replace(",",".")))
            if amount == 0:
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
            name = et.SubElement(offer, 'name')
            name.text = detail["title"]
            vendorCode = et.SubElement(offer, 'vendorCode')
            vendorCode.text = str(detail["article"])
            url = et.SubElement(offer, 'url')
            url.text = BASE_URL + "/" + detail["uri"]
            price = et.SubElement(offer, 'price')
            price.text = str(detail["price"])
            currencyId = et.SubElement(offer, 'currencyId')
            currencyId.text = "RUR"
            categoryId = et.SubElement(offer, 'categoryId')
            categoryId.text = str(category_ids[detail_category])
            if detail_category == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370" or detail_category == "Урал" or detail_category == "КАМАЗ" or detail_category == "ЯМЗ":
                country_of_origin = et.SubElement(offer, 'country_of_origin')
                country_of_origin.text = "Россия"
            
            pic_links = list(filter(None, pic_link(detail["images"]).split(',')))
            i = 0
            if len(pic_links) > 0:
                for pic in pic_links:
                    pic = pic.strip()
                    if i <= 9:
                        try:
                            pic_size = os.stat("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg").st_size/(1024*1024)
                        except:
                            wget.download(pic, "D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg")
                            pic_size = os.stat("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg").st_size/(1024*1024)
                        if pic_size < 5:
                            picture = et.SubElement(offer, 'picture')
                            picture.text = pic
                        elif pic_size >= 5 and len(pic_links) == 1:
                            picture = et.SubElement(offer, 'picture') 
                    i += 1 
            else:
                picture = et.SubElement(offer, 'picture') 
            
            pickup = et.SubElement(offer, 'pickup')
            pickup.text = "true"
            delivery = et.SubElement(offer, 'delivery')
            delivery.text = "true"
            store = et.SubElement(offer, 'store')
            store.text = "true"
            sposobi_oplati = et.SubElement(offer, 'sales_notes')
            sposobi_oplati.text = "Наличные, онлайн-оплата на сайте или платеж по счету."
            dostavka = et.SubElement(offer, 'sales_notes')
            dostavka.text = "Доставка оплачивается отдельно."
            sroki_dostavki = et.SubElement(offer, 'sales_notes')
            sroki_dostavki.text = "Доставим за 4 часа или отправим по всей России."
            sposobi_dostavki = et.SubElement(offer, 'sales_notes')
            sposobi_dostavki.text = "Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др."
            predoplata = et.SubElement(offer, 'sales_notes')
            predoplata.text = "Необходима предоплата 100%."
            description = et.SubElement(offer, 'description')
            description.text = """<p>Компания ТД БОВИД являемся одним из крупнейших поставщиков в России и официальным дилером АО «Автомобильный завод «УРАЛ», ПАО</p>
            <p>«КАМАЗ», ПАО «Автодизель», АО «ЯЗДА», ООО «УАЗ», ООО</p><p>«ИВЕКО-АМТ», ООО «Автоцентр ОСВАР», АО «Гидросила М»,</p>
            <p>представителем 35 отечественных заводов-изготовителей, а также</p>
            <p>IVECO, VOLVO, RENAULT TRUCKS и спецтехнике KOMATSU, HITACHI, </p><p>CATERPILLAR.</p>"""
            proizvoditel = et.SubElement(offer, 'param')
            proizvoditel.set("name", 'Производитель')
            proizvoditel.text = detail_category
            if len(detail["article"]) > 1:
                artikul = et.SubElement(offer, "param")
                artikul.set("name", 'Артикул')
                artikul.text = detail["article"]
            kod = et.SubElement(offer, 'param')
            kod.set("name", 'Код')
            kod.text = detail["code"]
            count = et.SubElement(offer, 'count')
            count.text = str(amount)
        
        start += limit
    f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
    tree._setroot(et.fromstring(f_str))
    tree.write("yandex.xml", encoding = "UTF-8", xml_declaration = True)
    
def main():
    yandex_old(get_data_from_base())
    print("XML для яндекса готова")
    

def pic_link(imgs):
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
    
    
if __name__ == "__main__":
    main()