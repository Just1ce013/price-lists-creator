# AutopiterArmtek
[[Класс-родитель]]
## Поля и методы
`Поля`
Имя | Описание
--- | ---
fail_articles | Список артикулов, на которые ругается Autopiter
data | Список запчастей, которые попали в выгрузку
`Методы`
### Метод **get_xlsx**
Сначала присвоить `start` и `limit` переменным значения `0` и `1000` (`limit` вообще можно было бы сделать константой, так как она неизменна, а `start` можно было бы передавать в качестве параметра методов, но пока и так сойдет)
Вызвать **write_column_names**, чтобы в эксельку названия столбцов записать.
Дальше можно и `while True` бахнуть, который прервется, когда на запрос ничего не вернется в ответ.
```python
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
```
Дальше циклом `for` обойти весь список деталей, проверить **код**, **артикул**, **наличие на складах**, **категорию** и флаги **searchable** и **published**, чтобы собрать только нужные запчасти, карточки которых сейчас опубликованы на сайте. Название категории здесь нужно, его по ключу можно вытащить из словаря **category_names**.
```python
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
```
Дальше убрать многоточия из названий и убрать из выгрузки лишние запчасти, например из "левых" категорий или без норм цены. Собрать наличие запчастей на складе и в магазине на Линейной 98. Те, которых нет, выкинуть вместе с теми, у которых кривой артикул.
```python
nalichie = 0
title = detail["title"]
if title.find("...") > 0:
	title = title.replace("...", "")
if vendor == "Распродажа" or vendor == "Автошины" or vendor == "Т-150" or vendor == "ЮМЗ" or vendor == "Прицепы" or vendor == "Экскаватор" or vendor == "Радиаторы ЛРЗ" or vendor == "Т-40" or vendor == "Автокраны и КМУ" or vendor == "ДТ-75" or vendor == "РВД" or vendor == "Фильтры и комплекы прокладок МОТОРДЕТАЛЬ" or vendor == "ДЗ-98;ДЗ-180" or vendor == "Автобусы" or vendor == "Подшипники" or vendor == "Легковые иномарки" or vendor == "Прочие" or vendor == "Электрооборудование":
	continue
if detail["price"] == 0 or detail["price"] == 0.0 or round(detail["price"]) == 0 or str(detail["price"]) == "":
	continue 
for storage in detail["storage"]:
	if storage["codestorage"] == "00006" or storage["codestorage"] == "00008":
		nalichie += storage["amount"]
if nalichie == 0:
	continue
if detail["article"] in self.fail_articles:
	continue
```
Прошедшие отбор добавить в список для записи в эксельку
```python
self.data.append([
	vendor,
	detail["article"],
	title,
	detail["price"],
	nalichie
	])
```
**`САМОЕ ГЛАВНОЕ`** - не забыть увеличить `start` на `limit`
```python
start += limit
```
Ну и в конце можно вызвать метод get_xlsx класса-родителя, чтобы в консоль вывелась строка **Autopiter/Armtek XLSX created**. 

Данные:
[[AutopiterArmtek табличка]]

Ссылки на описание классов других площадок:
[[Drom]]
[[Avito]]
[[ЦФК]]
[[2Гис]]
[[SPL]]
[[ZZap]]
[[Yandex]]
[[Rees46]]