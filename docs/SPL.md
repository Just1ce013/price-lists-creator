# Spl
[[Класс-родитель]]
## Поля и методы
`Поля`
Имя | Описание
--- | ---
data | Список запчастей, которые попали в выгрузку
stop_categories | Категории, которые не должны попадать в выгрузку
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
Дальше циклом `for` обойти весь список деталей, проверить **код**, **артикул**, **наличие на складах**, **категорию** и флаги **searchable** и **published**, чтобы собрать только нужные запчасти, карточки которых сейчас опубликованы на сайте.
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
	
	category = list(filter(None, detail["uri"].split('/')))[1]
	if category not in self.category_names.keys():
		continue
	if self.category_names[category] in self.stop_categories:
		continue
```
Дальше убрать многоточия из названий и убрать из выгрузки лишние запчасти, например из "левых" категорий или без норм цены. Собрать наличие запчастей на складе и в магазине на Линейной 98. Те, которых нет, выкинуть вместе с теми, у которых кривой артикул.
```python
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
```
Для оставшихся получить ссылки на фото в виде строки и добавить их в список для записи в excel
```python
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
```
**`САМОЕ ГЛАВНОЕ`** - не забыть увеличить `start` на `limit`
```python
start += limit
```
Ну и в конце можно вызвать метод get_xlsx класса-родителя, чтобы в консоль вывелась строка **SPL XLSX created**. 

Данные:
[[SPL табличка]]

Ссылки на описание классов других площадок:
[[AutopiterArmtek]]
[[Avito]]
[[ЦФК]]
[[2Гис]]
[[Drom]]
[[ZZap]]
[[Yandex]]
[[Rees46]]