from OOP import Ploschadka
import xlsxwriter as xl


class Cfk(Ploschadka):
    
    data2 = []
    
    def __init__(self, filename, filename2, fields, fields2):
        self.__filename = filename
        self.__fields = fields
        self.__filename2 = filename2
        self.__fields2 = fields2
        self.data = []
        
    def get_xlsx(self):
        start = 0
        limit = 1000
        workbook = xl.Workbook(self.__filename)
        worksheet = workbook.add_worksheet()
        workbook2 = xl.Workbook(self.__filename2)
        worksheet2 = workbook2.add_worksheet()
        self.write_column_names(worksheet, self.__fields)
        self.write_column_names(worksheet2, self.__fields2)
        while True:
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
            if len(details) == 0:
                self.write_data(worksheet, 1, self.data, len(self.__fields))
                self.write_data(worksheet2, 1, self.data2, len(self.__fields2))
                workbook.close()
                workbook2.close()
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
                if vendor == "Распродажа":
                    continue
                if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
                    continue 
                for store in detail["storage"]:
                    if store["codestorage"] == "00006":
                        nalichie = store["amount"]
                if nalichie == 0:
                    continue
                self.data2.append([
                    detail["code"],
                    detail["title"],
                    "00006",
                    nalichie,
                    "45"
                    ])
                self.data.append([
                    detail["code"],
                    detail["title"],
                    detail["price"],
                    "20",
                    round(detail["price"] * 1.2, 2),
                    "643",
                    "796"
                    ])
                
            start += limit
        
        super().get_xlsx("Cfk")