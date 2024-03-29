from OOP import Ploschadka
import xlsxwriter as xl
from datetime import date


class TwoGis(Ploschadka):
    
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
                if len(detail["storage"]) == 1:
                    if detail["storage"][0]["idstorage"] == "":
                        continue
                category = list(filter(None, detail["uri"].split('/')))[1]
                if category not in self.category_names.keys():
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
                
                self.data.append([
                    str(date.today()),
                    self.category_names[category],
                    detail["article"],
                    self.BASE_URL + detail["uri"],
                    detail["title"],
                    detail["code"],
                    detail["external_id"],
                    detail["title"],
                    detail["price"],
                    nalichie,
                    links    
                ])
                
            start += limit
        
        super().get_xlsx("2Gis")