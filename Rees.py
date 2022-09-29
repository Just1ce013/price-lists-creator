from OOP import Ploschadka
from datetime import date, datetime
import xml.etree.ElementTree as et
from xml.dom import minidom


class Rees46(Ploschadka):
    
    category_ids = {"Автобусы": 1, "Автокраны и КМУ": 2, "Автошины": 3, "Аккумуляторы": 4, "ВАЗ": 5, "ГАЗ грузовой": 6, "ГАЗ легковой": 7, "Гидросила": 8, "ДЗ-98;ДЗ-180": 9, "ДТ-75": 10, 
                "ЗИЛ": 11, "Инструмент": 12, "КАМАЗ": 13, "Легковые иномарки": 14, "МАЗ": 15, "МТЗ": 16, "Погрузчики": 17, "Подшипники": 18, "Поршневая группа": 19, "Поршневая группа ВАЗ Мотордеталь": 20, 
                "Поршневая группа Мотордеталь": 21, "Поршневая группа Украина": 22, "Прицепы": 23, "Прочие": 24, "РВД": 25, "Радиаторы ЛРЗ": 26, "Т-150": 27, "Т-170": 28, "Т-40": 29, "УАЗ": 30, 
                "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370": 31, "Урал": 32, "Фильтры и комплекты прокладок МОТОРДЕТАЛЬ": 33, "ШААЗ": 34, "Экскаватор": 35, "Электрооборудование": 36, "ЮМЗ": 37, "ЯМЗ": 38, "CAT": 39, "HYUNDAI": 40, 
                "Hitachi": 41, "IVECO": 42, "KOMATSU": 43}
    addresses = ["г.Челябинск, ул.Линейная, 98", "г.Челябинск, Троицкий тр., 66",
             "г.Магнитогорск, ул.Заводская, 1/2", "г.Магнитогорск, ул.Кирова, 100", 
             "г.Красноярск, ул. 2-я Брянская, 34, стр. 2", "г. Алдан, ул. Комсомольская, 19Б",
             "Склад IVECO автосервис", "г.Бодайбо, ул. Артема Сергеева, 9А"]
    
    def __init__(self, filename):
        self.__filename = filename
    
    def get_xml(self):
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
        for c in self.category_ids:
            category = et.SubElement(categories, 'category')
            category.set('id', str(self.category_ids[c]))
            category.text = c
        # Для Rees46
        locations = et.SubElement(shop, 'locations')
        for address in self.addresses:
            location = et.SubElement(locations, 'location')
            location.set('id', str(self.addresses.index(address) + 1))
            location.set('type', "store")
            location.set('name', address)
        offers = et.SubElement(shop, 'offers')
        while True:
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
            if len(details) == 0:
                break
            for detail in details:
                if detail["code"] == None or detail["code"] == "":
                    continue
                if len(detail["storage"]) == 0:
                    continue
                if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
                    continue
                store = {}
                nalichie = 0
                for storage in detail["storage"]:
                    amount = str(storage["amount"])
                    if amount[0] == "-":
                        store[storage["namestorage"]] = 0
                        continue
                    if amount.find("\xa0") > 0:
                        count = round(float(amount[:amount.find("\xa0")]))
                        store[storage["namestorage"]] = count
                    else:
                        count = round(float(amount.replace(',','.')))
                        store[storage["namestorage"]] = count
                    nalichie += count    
                if nalichie == 0 or nalichie == 0.0 or str(nalichie) == "":
                    continue
                splited_url = list(filter(None, detail["uri"].split('/')))
                if splited_url[1] in self.category_names.keys():
                    detail_category = self.category_names[splited_url[1]]
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
                detail_url.text = self.BASE_URL + detail["uri"]
                detail_name = et.SubElement(offer, 'name')
                detail_name.text = detail["title"]
                price = et.SubElement(offer, 'price')
                price.text = str(detail["price"])
                categoryId = et.SubElement(offer, 'categoryId')
                categoryId.text = str(self.category_ids[detail_category])
                detail_locations = et.SubElement(offer, 'locations')
                for key in store.keys():
                    detail_location = et.SubElement(detail_locations, 'location')
                    detail_location.set('id', str(self.addresses.index(key) + 1))
                    stock_quantity = et.SubElement(detail_location, 'stock_quantity')
                    stock_quantity.text = str(store.get(key))
                pic_linki = list(filter(None, self.pic_links(detail["images"]).split(',')))
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
                    
            start += limit
        f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
        self.tree._setroot(et.fromstring(f_str))
        self.tree.write(self.__filename, encoding = "UTF-8", xml_declaration = True)     
        
        super().get_xml("Rees46")