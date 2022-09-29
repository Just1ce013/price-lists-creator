# Rees46
[[Класс-родитель]]
## Поля и методы
`Поля`
Имя | Описание
------ | ------
category_ids | Словарь, который жестко фиксирует id для категорий
addresses | Адреса, на которых могут находиться запчасти
`Методы`
### Метод get_xml
Сначала присвоить `start` и `limit` переменным значения `0` и `1000` (`limit` вообще можно было бы сделать константой, так как она неизменна, а `start` можно было бы передавать в качестве параметра методов, но пока и так сойдет). Далее в ElementTree добавляем тэг **yml_catalog** с параметром *date*, дочерним элементом к которому добавляем **shop**. Для магазина нужно указать тэги *name*, *company*, *url*, *currencies*, *categories*, *locations*, *offers*. В **currencies** добавляем элемент *currency* с параметрами **id** и **rate**. **id** = "RUR", а **rate** = 1, так как рубль - основная валюта.
В **categories** добавляем элементы через цикл `for`. У каждой *category* есть параметр **id**, который мы берем из словаря *category_ids*.
В **locations** добавляем элементы также через цикл `for`. У элементов есть параметры **id**, **type**, **name**. *id* = индекс в списке addresses + 1, *type* = store, а *name* = address из того же списка.
В **offers** каждый элемент - запчасть, поэтому туда добавляется всё с помощью цикла `while True`, который прерывается, когда в ответе пусто.
```python
start = 0
limit = 1000
yml_catalog = et.Element('yml_catalog')
now = str(date.today()) + " " + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute)
yml_catalog.set('date', now)
shop = et.SubElement(yml_catalog, 'shop')
name = et.SubElement(shop, 'name')
name.text = 'Торговый Дом "БОВИД"'
company = et.SubElement(shop, 'company')
company.text = 'АО "Торговый Дом "БОВИД"'
url = et.SubElement(shop, 'url')
url.text = "https://tdbovid.ru"
currencies = et.SubElement(shop, 'currencies')
RUR = et.SubElement(currencies, 'currency')
RUR.set('id', "RUR")
RUR.set('rate', '1')
categories = et.SubElement(shop, 'categories')
for c in self.category_ids:
	category = et.SubElement(categories, 'category')
	category.set('id', str(self.category_ids[c]))
	category.text = c
locations = et.SubElement(shop, 'locations')
for address in self.addresses:
	location = et.SubElement(locations, 'location')
	location.set('id', str(self.addresses.index(address) + 1))
	location.set('type', "store")
	location.set('name', address)
offers = et.SubElement(shop, 'offers')
while True:
	details = self.session.get(f"http://tdbovid.ru:3500/api/position?start={start}&limit={limit}").json()
	if len(details) == 0:
		break
```
У каждой запчасти проверить код, артикул, наличие, категорию, цену
```python
for detail in details:
	if detail["code"] == None or detail["code"] == "":
		continue
	if len(detail["storage"]) == 0:
		continue
	if detail["article"] == None or detail["article"] == "" or detail["article"].find("...") > 0:
		continue
	store = {}
	nalichie = 0
	for storage in detail["storage"]:
		amount = str(storage["amount"])
		if amount[0] == "-":
			store[storage["namestorage"]] = 0
			continue
		if amount.find("\xa0") > 0:
			count = round(float(amount[:amount.find("\xa0")]))
			store[storage["namestorage"]] = count
		else:
			count = round(float(amount.replace(',','.')))
			store[storage["namestorage"]] = count
		nalichie += count    
	if nalichie == 0 or nalichie == 0.0 or str(nalichie) == "":
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
У тех, кто прошел все проверки нужно указать главный тэг **offer** с параметрами *id* и *available*. 
Далее идет большое количество дочерних элементов: *auto* - специально для запчастей, *detail_url*, *detail_name*, *price*, *category_id*, *detail_locations*, *picture*, *vendor*, *vendor_code*,*description*.
**detail_locations** заполняются циклом `for` из словаря *store*. У каждой *detail_location* есть параметр **id**, а также дочерний элемент *stock_quantity*, в котором указывается наличие в данной локации.
**picture** снова заполняются циклом `for`. В тэгах **vendor** и **vendorCode** нужная информация содержится в тексте, как и в **description**.
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
Ну и в конце можно вызвать метод get_xml класса-родителя, чтобы в консоль вывелась строка **Rees46 XML created**. 

Данные:
[[Rees46 табличка]]

Ссылки на описание классов других площадок:
[[AutopiterArmtek]]
[[Avito]]
[[ЦФК]]
[[2Гис]]
[[Drom]]
[[ZZap]]
[[Yandex]]
[[SPL]]