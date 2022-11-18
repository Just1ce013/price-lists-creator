from OOP import Ploschadka
from datetime import date
import xml.etree.ElementTree as et
from xml.dom import minidom
import wget
import os
from PIL import Image


class Yandex(Ploschadka):
    
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
    
    def get_xml(self, without_space_pic):
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
        
        for c in self.category_ids:
            category = et.SubElement(categories, 'category')
            category.set('id', str(self.category_ids[c]))
            category.text = c
        
        offers = et.SubElement(shop, 'offers')
        
        while True:
            #el[0] - name, el[1] - artikl, el[2] - item_url, el[3] - price, el[4] - category, 
            #el[5] - pic_link, el[6] - baza_store, el[7] - uid, el[8] - kod
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
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
                    if el["namestorage"] == "г.Челябинск, ул.Линейная, 98" or el["namestorage"] == "г. Челябинск, ул.Линейная, 98":
                        str_amount = str(el["amount"])
                        if str_amount != "-":
                            if str_amount.find("\xa0") > 0:
                                amount = round(float(str_amount[:str_amount.find("\xa0")]))
                            else:
                                amount = round(float(str_amount.replace(",",".")))
                if amount == 0:
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
                pic_links = list(filter(None, self.pic_links(detail["images"]).split(',')))
                external_id = detail["external_id"]
                if without_space_pic and len(pic_links) == 0:
                    continue
                links = {"correct": "", "uncorrect": ""}
                for pic in pic_links:
                    i = pic_links.index(pic)
                    pic = pic.strip()
                    if not os.path.exists("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg"):
                        wget.download(pic, "D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg")
                    image = Image.open("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg")
                    if image.width < 600 or image.height < 600 or pic.find(".bmp") != -1 or image.width > 2560 or image.height > 2560:
                        if links["uncorrect"] == "":
                            links["uncorrect"] = pic
                        else:
                            links["uncorrect"] += "," + pic
                    else:
                        if links["correct"] == "":
                            links["correct"] = pic
                        else:
                            links["correct"] += "," + pic
                if links["correct"] == "":
                    continue
                correct_links = list(filter(None, links["correct"].split(',')))    
                
                offer = et.SubElement(offers, 'offer')
                if without_space_pic:
                    split_link = pic_links[0].split("/")
                    offer.set('id', split_link[6])
                else:
                    offer.set('id', external_id.replace("-","")[:20])
                offer.set('available', "true")
                name = et.SubElement(offer, 'name')
                name.text = detail["title"]
                vendorCode = et.SubElement(offer, 'vendorCode')
                vendorCode.text = str(detail["article"])
                url = et.SubElement(offer, 'url')
                url.text = self.BASE_URL + "/" + detail["uri"]
                price = et.SubElement(offer, 'price')
                price.text = str(detail["price"])
                currencyId = et.SubElement(offer, 'currencyId')
                currencyId.text = "RUR"
                categoryId = et.SubElement(offer, 'categoryId')
                categoryId.text = str(self.category_ids[detail_category])
                if detail_category == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370" or detail_category == "Урал" or detail_category == "КАМАЗ" or detail_category == "ЯМЗ":
                    country_of_origin = et.SubElement(offer, 'country_of_origin')
                    country_of_origin.text = "Россия"
                
                i = 0
                if len(pic_links) > 0:
                    if without_space_pic:
                        for link in correct_links:
                            link = link.strip()
                            picture = et.SubElement(offer, 'picture')
                            picture.text = link
                    else:
                        for pic in pic_links:
                            pic = pic.strip()
                            if i <= 9:
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
                if without_space_pic:
                    sales_note = et.SubElement(offer, 'sales_notes')
                    sales_note.text = "Наличные, онлайн-оплата на сайте или платеж по счету. Доставка оплачивается отдельно. Доставим за 4 часа или отправим по всей России. Доставка по регионам любой ТК: СДЭК, ПЭК, КИТ и др. Необходима предоплата 100%."
                else:
                    sposobi_oplati = et.SubElement(offer, 'sales_notes')
                    sposobi_oplati.text = "Наличные, онлайн-оплата на сайте или платеж по счету."
                    dostavka = et.SubElement(offer, 'sales_notes')
                    dostavka.text = "Доставка оплачивается отдельно."
                    sroki_dostavki = et.SubElement(offer, 'sales_notes')
                    sroki_dostavki.text = "Доставим за 4 часа или отправим по всей России."
                    sposobi_dostavki = et.SubElement(offer, 'sales_notes')
                    sposobi_dostavki.text = "Доставка по регионам любой ТК: СДЭК, ПЭК, КИТ и др."
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
                if without_space_pic:
                    continue
                count = et.SubElement(offer, 'count')
                count.text = str(amount)
            
            start += limit
        f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
        self.tree._setroot(et.fromstring(f_str))
        self.tree.write(self.__filename, encoding = "UTF-8", xml_declaration = True)     
        
        super().get_xml("Yandex")