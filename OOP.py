import requests
from requests.adapters import HTTPAdapter
from datetime import date
from xml.etree.ElementTree import ElementTree
import wget

class Ploschadka:
    
    URL = 'https://tdbovid.ru/katalog_zapchastej'
    BASE_URL = 'https://tdbovid.ru'
    today = str(date.today()).split('-')
    tdbovid_adapter = HTTPAdapter(max_retries=5)
    session = requests.Session()
    session.mount(BASE_URL, tdbovid_adapter)              
    tree = ElementTree()
    category_names = {"ural":"Урал","ural-63685-636746563-dorozhnaya-gamma-i-ural-6370":"УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370",
              "yamz":"ЯМЗ","kamaz":"КАМАЗ","maz":"МАЗ","uaz":"УАЗ","elektrooborudovanie":"Электрооборудование","gaz-gruzovoj":"ГАЗ грузовой",
              "gaz-legkovoj":"ГАЗ легковой","gidrosila":"Гидросила","porschnevaya-gruppa":"Поршневая группа","zil":"ЗИЛ","avtoshiny":"Автошины",
              "cat":"CAT","hitachi":"Hitachi","hyundai":"HYUNDAI","iveco":"IVECO","komatsu":"KOMATSU","avtobusy":"Автобусы","avtokrany-i-kmu":"Автокраны и КМУ",
              "akkumulyatory":"Аккумуляторы","vaz":"ВАЗ","dz-98-dz-180":"ДЗ-98;ДЗ-180","dt-75":"ДТ-75","instrument":"Инструмент",
              "legkovye-inomarkigruzovye-inomarkikommercheskij-transport":"Легковые иномарки","mtz":"МТЗ","pogruzchiki":"Погрузчики",
              "podshipniki":"Подшипники","porschnevaya-gruppa-vaz-motordetal":"Поршневая группа ВАЗ Мотордеталь","porschnevaya-gruppa-urkaina":"Поршневая группа Украина",
              "pricepy":"Прицепы","prochie":"Прочие","radiatory-lrz":"Радиаторы ЛРЗ","rvd":"РВД","t-150":"Т-150","t-170":"Т-170","t-40":"Т-40",
              "filtry-i-komplekty-prokladok-motordetal":"Фильтры и комплекты прокладок МОТОРДЕТАЛЬ","shaaz":"ШААЗ","ekskavator":"Экскаватор",
              "yumz":"ЮМЗ","rasprodazha":"Распродажа"}
    
    
    def __init__(self, filename = "", fields = []):
        self.__filename = filename
        self.__fields = fields
        
                
    @property
    def filename(self):
        return self.__filename
                
    @property
    def fields(self):
        return self.__fields
            
            
    def get_xlsx(self, name):
        print(f"{name} XLSX created")
        
        
    def get_xml(self, name):
        print(f"{name} XML created")
    
        
    def write_column_names(self, worksheet, names):
        for j in range(0, len(names)):
            worksheet.write(0, j, names[j])


    def write_data(self, worksheet, current_row, data, columns_count):
        for i in range(current_row, current_row + len(data)):
            for j in range(0, columns_count):
                worksheet.write(i, j, data[i - current_row][j])        

        
    def pic_links(self, imgs):
        pic_links = ""
        if len(imgs) > 0:
            for el in imgs:
                if el["url"].find("small") == -1 and el["url"].find("medium") == -1:
                    if pic_links == "":
                        url = self.BASE_URL + el["url"]
                        pic_links += url
                    else:
                        url = self.BASE_URL + el["url"]
                        pic_links += ", " + url
        return pic_links     
    
    
    def get_published_count(self):
        start = 0
        limit = 1000
        count = 0
        count_with_pics = 0
        while True:
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
            if len(details) == 0:
                break
            for detail in details:
                if detail["searchable"] == 0 or detail["published"] == 0:
                    continue
                else:
                    count += 1
                if len(detail["images"]) > 0:
                    count_with_pics += 1
            start += limit
        print("Общее количество карточек на сайте - " + str(count) + "; с картинками - " + str(count_with_pics) + ".")
        
        
    def download_images(self):
        start = 0
        limit = 1000
        count = 0
        while True:
            details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
            if len(details) == 0:
                break
            for detail in details:
                if detail["searchable"] == 0 or detail["published"] == 0:
                    continue
                else:
                    pic_links = list(filter(None, self.pic_links(detail["images"]).split(',')))
                    for pic in pic_links:
                        strip_pic = pic.strip()
                        print(self.BASE_URL + pic)
                        wget.download(strip_pic, 'D:/parsing/update_pic/' + detail["external_id"] + '_' + str(pic_links.index(pic)) + '.jpeg')
                        count += 1
            start += limit
        print("Картинки загружены")