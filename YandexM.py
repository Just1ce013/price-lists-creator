from OOP import Ploschadka
import xlsxwriter as xl


class YandexMarket(Ploschadka):
# "uid", "Наименование", "Ссылки на фото", "Описание", "Категория", "Бренд", "Штрихкод", "Артикул", "Цена"    
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
                
                nalichie = 0
                for el in detail["storage"]:
                    amount = str(el["amount"])
                    if amount[0] == "-":
                        continue
                    if amount.find("\xa0") > 0:
                        count = round(float(amount[:amount.find("\xa0")]))
                    else:
                        count = round(float(amount.replace(',','.')))
                    nalichie += count 
                if nalichie == 0:
                    continue
                
                links = self.pic_links(detail["images"])
                
                if links == "":
                    continue
                
                self.data.append([
                    detail["external_id"],
                    detail["title"],
                    links,
                    detail["title"],
                    detail["grouptitle"],
                    detail["grouptitle"],
                    self.create_EAN13(detail["code"]),
                    detail["article"],
                    detail["price"]
                ])
                
            start += limit
        
        super().get_xlsx("YandexMarket")
        
        
    def create_EAN13(self, detail_code):
        EAN13 = ""
        for sign in detail_code:
            if sign.isalpha():
                EAN13 = EAN13 + str(ord(sign))
            else:
                EAN13 = EAN13 + str(sign)
        while len(EAN13) < 11:
            EAN13 = "0" + EAN13
        EAN13 = "1" + EAN13
        index = 0
        chetnie = 0
        nechetnie = 0
        for i in EAN13:
            if index in (1,3,5,7,9,11):
                chetnie += int(i)
            else:
                nechetnie += int(i)
            index += 1
        result = chetnie * 3 + nechetnie
        if result % 10 != 0:
            thirteen_char = 10 - (result % 10)
        else:
            thirteen_char = 0
        EAN13 = EAN13 + str(thirteen_char)
        return EAN13