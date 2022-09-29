# Описание для Rees46
## Главные тэги
Имя | Описание | Пример
--- | --- | ---
yml_catalog | Самый главный тэг с датой создания прайса | `<yml_catalog date ="2022-09-28 9:20">`
shop | Внутри содержится описание магазина и каталог | `<shop> ... </shop>`
name | Название магазина | `<name>Торговый дом "БОВИД"</name>`
company | Полное название компании |  `<company> АО "Торговый дом "БОВИД"</company>`
url | Ссылка на главную страницу сайта | `<url>https://tdbovid.ru</url>`
currencies | Контейнер для валют | `<currencies> ... </currencies>`
currency | Конкретная валюта | `<currency id="RUR" rate="1" />`
categories | Контейнер для категорий | `<categories> ... </categories>`
category | Категория | `<category id="1">Автобусы</category>`
locations | Контейнер для локаций | `<locations> ... </locations>`
location | Локация | `<location id="1" type="store" name="г.Челябинск, ул.Линейная, 98" />`
offers | Каталог | `<offers> ... </offers>`

## Тэги запчасти
Имя | Описание | Пример
--- | --- | ---
offer | Главный тэг запчасти | `<offer id="*Тут страшный набор из 20 символов*" available="True"> ... </offer>`
auto | Пустой тэг, обязательный для авто тематики | `<auto />`
url | Ссылка на карточку | `<url>*Ссылка*</url>`
name | Наименование | `<name>Жгут проводов ...</name>`
price | Цена | `<price>199910</price>`
categoryId | Id категории | `<categoryId>41</categoryId>`
locations | | 
location | Тэг для каждого склада, в котором запчасть в наличии | `<location id="5"> ... </location>`
stock_quantity | Дочерний тэг *location*, в котором указывается количество запчастей | `<stock_quantity>5</stock_quantity>`
vendor | Название каталога на сайте | `<vendor>Hitachi</vendor>`
vendorCode | Артикул запчасти | `<vendorCode>0005499</vendorCode>`
description | Описание (повторяет наименование) | `<description> ... </description>`
