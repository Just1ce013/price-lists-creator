from OOP import Ploschadka
import xlsxwriter as xl


class AA(Ploschadka):
    
    fail_articles = ["34А-71-11611", "353398917с (16284016)", "ШД 1,2 (15972146)", 
                     "ПП (15972167)", "ТСС-140 392440 (15592572)", "ТСС-100 392400 (15592415)", 
                     "СВ000011441 (15548235)", "3ЕВ-04-32410", "3ЕВ-04-32410 ", "А810180/LA810180", "195-78-21331 НХ", 
                     "34А-28-00110", "КГК №7", "Лк-00002357 (16084887)", "ПСТ-200 ", 
                     "ПСТ-200", "ТПХ810С", "ТВС-3020К ", "ТВС-3020К", "Z-011 65-95 мм 2900-25 ", "Z-011 65-95 мм 2900-25",
                     "Z-010 R-50R 65-95 мм 2901-25", "Z-010 R-50R 65-95 мм 2901-25 ", "3ЕВ-24-41330", "1/2 * 3/4 L=600мм Ф20мм",
                     "Вороток 3/4* -1* L=600 мм", "М5-М8", "12-16 мм", "10мм 1/2 6гр.", "11мм 1/2 6гр", "14мм 1/2 6 гр",
                     "20мм 1/26гр", "23мм 1/2 6гр", "24мм 1/2 6гр", "26мм 1/2 6гр", "27мм 1/2 6гр", "27мм квадрат 1*ударная",
                     "28мм 1/2 6гр", "30мм 1/2 6гр", "30мм квадрат 3/4 12гр", "32мм квадрат 3/4", "33мм квадрат 1*ударная",
                     "38мм квадрат 1*ударная", "46мм квадрат 3/4", "50мм квадрат 3/4 12гр.", "24 мм 6 граней", "8 мм 6 граней",
                     "10 мм 6 граней", "14 мм 6 граней", "Головка торцевая *22", "Головка торцевая *33", "Головка торцевая *41",
                     "Е 8", "Е 10", "Е 12", "Е 14", "Е 16", "Е 11", "Е 18", "Е 20", "Е 22", "32мм квадрат 3/4", "46мм квадрат 3/4",
                     "Головка торцевая *22", "Головка торцевая *33", "Головка торцевая *41", "КГК 55х55", "КГКУ 38 ц15хр", "КГКУ 55 ц 15 хр",
                     "КГКУ 65 ц 15хр", "КГКУ 70 ц 15хр", "16х18", "КГН 36х41 ц 15хр", "КГК 11*11 CrV", "КГК 23*23 CrV", "КГК 25*25 CrV",
                     "КГК 26*26 CrV", "КГК 38*38", "КГК 60*60", "КГК 8*8 CrV", "КГК 9*9 CrV", "КН 10х12", "15х17", "19х22", "10х11", "8х10",
                     "10х12", "11х13", "12х14", "14х17", "15 мм", "17 мм", "19 мм", "22 мм", "Бычок", "10х10 изогнутый", "13х14 изогнутый",
                     "30х36", "17х19", "М10", "М12", "3ЕВ-36-51180", "ЛГ-16 Ц15 хр.", "КР-24", "М14", "М8", "215 мм", "150мм", "200 мм"]
    
    bad_articles = {"4S00685LHE / 4643580 / SKL46235":"4S00685LHE"}

    def __init__(self, filename, fields):
        self.__filename = filename
        self.__fields = fields
        self.data = []
        
    def get_xlsx(self, komu):
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
                if len(detail["storage"]) == 1:
                    if detail["storage"][0]["idstorage"] == "":
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
                if komu == "AA":
                    if vendor == "Прицепы" or vendor == "Т-40" or vendor == "РВД" or vendor == "ДЗ-98;ДЗ-180" or vendor == "Прочие":
                        continue
                if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                    continue 
                for storage in detail["storage"]:
                    if komu == "AA":
                        if storage["codestorage"] == "00006" or storage["codestorage"] == "00008":
                            nalichie += storage["amount"]
                    if komu == "N":
                        if storage["codestorage"] == "00006" or storage["codestorage"] == "00008" or storage["codestorage"] == "00009" or storage["codestorage"] == "00425":
                            nalichie += storage["amount"]
                if nalichie == 0:
                    continue
                if detail["article"] in self.fail_articles:
                    continue
                # for el in self.fail_articles:
                #     if detail['article'].find(el) > -1:
                #         continue
                if vendor == "Урал" or vendor == "УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370":
                    vendor = "УРАЛАЗ"
                if vendor == "ГАЗ грузовой" or vendor == "ГАЗ легковой":
                    vendor = "ГАЗ"
                end = len(detail["article"])
                if detail["article"].find("(") > -1:
                    end = detail["article"].find("(")
                elif detail["article"].find(")") > -1:
                    end = detail["article"].find(")")
                elif detail["article"].find(",") > -1:
                    end = detail["article"].find(",")
                if komu == "AA":
                    price = detail["price"] * 0.85
                    self.data.append([
                        vendor,
                        detail["article"][:end],
                        title,
                        price,
                        nalichie
                        ])
                if komu == "N":
                    price = detail["price"] * 0.85
                    self.data.append([
                        vendor,
                        detail["article"][:end],
                        title,
                        price,
                        nalichie
                        ])
            
            start += limit
        
        super().get_xlsx("Autopiter/Armtek")