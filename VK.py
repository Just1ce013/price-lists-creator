from OOP import Ploschadka
import xlsxwriter as xl


class VK(Ploschadka):
# "Название", "Цена", "Описание", "Фото"    
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
                    detail["title"],
                    detail["price"],
                    detail["title"],
                    links
                ])
                
            start += limit
        
        super().get_xlsx("VK")