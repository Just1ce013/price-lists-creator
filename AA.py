from OOP import Ploschadka
import xlsxwriter as xl


class AA(Ploschadka):
    
    fail_articles = ["34А-71-11611", "353398917с (16284016)", "ШД 1,2 (15972146)", 
                     "ПП (15972167)", "ТСС-140 392440 (15592572)", "ТСС-100 392400 (15592415)", 
                     "СВ000011441 (15548235)", "3ЕВ-04-32410", "А810180/LA810180", "195-78-21331 НХ", 
                     "34А-28-00110", "КГК №7"]

    def __init__(self, filename, fields):
        self.__filename = filename
        self.__fields = fields
        self.data = []
        
    def get_xlsx(self):
        start = 0
        limit = 1000
        workbook = xl.Workbook(self.__filename)
        worksheet = workbook.add_worksheet()
        self.write_column_names(worksheet, self.__fields)
        while True:
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
            if len(details) == 0:
                self.write_data(worksheet, 1, self.data, len(self.__fields))
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
                if vendor_in_url in self.category_names.keys():
                    vendor = self.category_names[vendor_in_url]
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
                        nalichie += storage["amount"]
                if nalichie == 0:
                    continue
                if detail["article"] in self.fail_articles:
                    continue
                if vendor == "Урал" or vendor == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370":
                    vendor = "УРАЛАЗ"
                if vendor == "ГАЗ грузовой" or vendor == "ГАЗ легковой":
                    vendor = "ГАЗ"
                self.data.append([
                    vendor,
                    detail["article"],
                    title,
                    detail["price"],
                    nalichie
                    ])
            
            start += limit
        
        super().get_xlsx("Autopiter/Armtek")