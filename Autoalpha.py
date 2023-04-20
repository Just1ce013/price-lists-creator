from OOP import Ploschadka
import xlsxwriter as xl


class AutoAlpha(Ploschadka):
    
    category_names = {"ural":"Урал","ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":"УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370",
              "yamz":"ЯМЗ","kamaz":"КАМАЗ"}
    
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
                category_in_url = list(filter(None, detail["uri"].split('/')))[1]
                if category_in_url not in self.category_names.keys():
                    continue
                else:
                    category = self.category_names[category_in_url]
                nalichie = 0
                for storage in detail["storage"]:
                    if storage["codestorage"] == "00006" or storage["codestorage"] == "00008":
                        nalichie += storage["amount"]
                if nalichie == 0:
                    continue
                
                if category_in_url == "kamaz":
                    self.data.append([
                        category,
                        detail["article"],
                        detail["title"],
                        round(detail["price"] * 0.9, 2),
                        nalichie
                    ])
                if category_in_url == "ural" or category_in_url == "yamz" or category_in_url == "ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":
                    self.data.append([
                        category,
                        detail["article"],
                        detail["title"],
                        round(detail["price"] * 0.85, 2),
                        nalichie
                    ])
                
            start += limit
        
        super().get_xlsx("AutoAlpha")