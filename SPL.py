from OOP import Ploschadka
import xlsxwriter as xl


class SPL(Ploschadka):
    
    stop_categories = ["Автошины", "ВАЗ", "УАЗ", "ГАЗ легковой", "Инструмент", 
                           "Легковые иномарки", "Поршневая группа", "Поршневая группа ВАЗ Мотордеталь", 
                           "Поршневая группа Мотордеталь", "Поршневая группа Украина", "Прочие", "Распродажа"]
    
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
                
                category = list(filter(None, detail["uri"].split('/')))[1]
                if category not in self.category_names.keys():
                    continue
                if self.category_names[category] in self.stop_categories:
                    continue
                
                store = {}
                nalichie = 0
                for el in detail["storage"]:
                    amount = str(el["amount"])
                    if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
                        if amount[0] != "-":
                            if amount.find("\xa0") > 0:
                                nalichie += round(float(amount[:amount.find("\xa0")]))
                                store[el["namestorage"]] = nalichie
                            else:
                                nalichie += round(float(amount.replace(",",".")))
                                store[el["namestorage"]] = nalichie
                if nalichie == 0:
                    continue
                
                links = self.pic_links(detail["images"])
                
                self.data.append([
                    self.category_names[category],
                    detail["article"],
                    detail["code"],
                    detail["title"],
                    detail["price"],
                    nalichie,
                    nalichie,
                    detail["price"],
                    links
                ])
                
            start += limit
        
        super().get_xlsx("SPL")