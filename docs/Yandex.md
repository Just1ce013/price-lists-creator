# Yandex
[[Класс-родитель]]
## Поля и методы
`Поля`
Имя | Описание
------ | ------
category_ids | Словарь, который жестко фиксирует id для категорий
addresses | Адреса, на которых могут находиться запчасти
`Методы`
### Метод get_xml
Сначала присвоить `start` и `limit` переменным значения `0` и `1000` (`limit` вообще можно было бы сделать константой, так как она неизменна, а `start` можно было бы передавать в качестве параметра методов, но пока и так сойдет). Далее в ElementTree добавляем тэг **yml_catalog** с параметром *date*, дочерним элементом к которому добавляем **shop**. Для магазина нужно указать тэги *name*, *company*, *url*, *platform*, *version*, *agency*, *email*, currencies, *categories*, *offers*.
В **currencies** добавляем элемент с параметрами **id** = *RUR*  и **rate** = *1*, так как рубль является основной валютой.
**categories** заполняются циклом `for`, у каждого элемента есть параметр **id**.
```python
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
```
В **offers** каждый элемент - запчасть, поэтому туда добавляется всё с помощью цикла `while True`, который прерывается, когда в ответе пусто.
```python
while True:
#el[0] - name, el[1] - artikl, el[2] - item_url, el[3] - price, el[4] - category, 
#el[5] - pic_link, el[6] - baza_store, el[7] - uid, el[8] - kod
details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
if len(details) == 0:
	break;
```
У каждой запчасти проверяется **код**, **артикул**, флаги **searchable** и **published**, **категорию**, **наличие** и **цену**.
```python
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
		if el["namestorage"] == "г.Челябинск, ул.Линейная, 98":
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
```
Для каждой запчасти создается тэг **offer** с параметром *id*, в который записываются 20 символов *external_id*, из которого убраны тире.
Далее идут тэги *name* и *vendorCode*, которые заполняются полями из запроса *detail["title"]* и *detail["article"]*.
Тэг *url* заполняется строкой, которая конкатенируется из **BASE_URL** и *detail["url"]*.
*price* заполняет ценой из ответа, предварительно конвертируя поле в string.
Тэги *currency_id* и *category_id* заполняются элементарно. Первый - константа *RUR*, а во второй значением *category_ids[detail_category]*.
Если **detail_category** = значениям *УРАЛ-63685, 63674,6563 (ДОРОЖНАЯ ГАММА) И УРАЛ-6370, Урал, КАМАЗ, ЯМЗ*, то у запчасти появляется тэг **country_of_origin** = *Россия*
```python
external_id = detail["external_id"]
offer = et.SubElement(offers, 'offer')
offer.set('id', external_id.replace("-","")[:20])
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
```
Далее с помощью списка ссылок на фото создаются тэги **picture** в достаточном количестве + картинки загружаются на комп, чтобы узнать их размер, ведь яндекс не хочет "переваривать" картинки толще 5Мб.
```python
pic_links = list(filter(None, self.pic_links(detail["images"]).split(',')))
i = 0
if len(pic_links) > 0:
	for pic in pic_links:
		pic = pic.strip()
		if i <= 9:
			try:
				pic_size = os.stat("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg").st_size/(1024*1024)
			except:
				wget.download(pic, "D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg")
				pic_size = os.stat("D:/parsing/pic/" + external_id + "_" + str(i) + ".jpeg").st_size/(1024*1024)
			if pic_size < 5:
				picture = et.SubElement(offer, 'picture')
				picture.text = pic
			elif pic_size >= 5 and len(pic_links) == 1:
				picture = et.SubElement(offer, 'picture') 
		i += 1 
else:
	picture = et.SubElement(offer, 'picture') 
```
Тэги *pickup*, *delivery* и *store* отвечают за разные способы получения запчасти, доставка, заказ, покупка в магазине.
Далее идут тэги *sales_notes*, в которых прописаны особенности продажи, например Оплата доставки отдельно.
Тэг *description* полностью оправдывает своё название.
Далее создаются нескольк тэгов *param*, в которых указывается категория == производитель, артикул и код запчасти.
Последним тэгом идет *count*, который отвечает за количество в наличии.
```python
pickup = et.SubElement(offer, 'pickup')
pickup.text = "true"
delivery = et.SubElement(offer, 'delivery')
delivery.text = "true"
store = et.SubElement(offer, 'store')
store.text = "true"
sposobi_oplati = et.SubElement(offer, 'sales_notes')
sposobi_oplati.text = "Наличные, онлайн-оплата на сайте или платеж по счету."
dostavka = et.SubElement(offer, 'sales_notes')
dostavka.text = "Доставка оплачивается отдельно."
sroki_dostavki = et.SubElement(offer, 'sales_notes')
sroki_dostavki.text = "Доставим за 4 часа или отправим по всей России."
sposobi_dostavki = et.SubElement(offer, 'sales_notes')
sposobi_dostavki.text = "Доставка по регионам любой ТК: СДЭК, Деловые Линии, ПЭК, КИТ и др."
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
count = et.SubElement(offer, 'count')
count.text = str(amount)
```
**`САМОЕ ГЛАВНОЕ`** - не забыть увеличить `start` на `limit`
```python
start += limit
```
Далее указан код, который позволяет всё красиво протабулировать, а также в начальном тэге **xml** явно указать параметр encoding и отобразить его в файле.
```python
f_str = minidom.parseString(et.tostring(yml_catalog)).toprettyxml(indent = "   ")
self.tree._setroot(et.fromstring(f_str))
self.tree.write(self.__filename, encoding = "UTF-8", xml_declaration = True)
```
Ну и в конце можно вызвать метод get_xml класса-родителя, чтобы в консоль вывелась строка **Yandex XML created**. 

Данные:
[[Yandex табличка]]

Ссылки на описание классов других площадок:
[[AutopiterArmtek]]
[[Avito]]
[[ЦФК]]
[[2Гис]]
[[Drom]]
[[ZZap]]
[[Rees46]]
[[SPL]]