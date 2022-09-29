# Описание для Яндекса
## Турбо-страницы
### Главные тэги
Имя | Описание | Пример
--- | --- | ---
yml_catalog | Самый главный тэг с датой создания прайса | `<yml_catalog date ="2022-09-28 9:20">`
shop | Внутри содержится описание магазина и каталог | `<shop> ... </shop>`
name | Название магазина | `<name>Торговый дом "БОВИД"</name>`
company | Полное название компании |  `<company> АО "Торговый дом "БОВИД"</company>`
url | Ссылка на главную страницу сайта | `<url>https://tdbovid.ru</url>`
platform | Название CMS | `<platform>MODX Revo</platform>`
version | Версия CMS | `<version>2.8.1</version>`
agency | | `<agency>Торговый дом "БОВИД"</agency>`
email | Почта для заказов | `<email>zakaz@bovid.ru</email>`
currencies | Контейнер для валют | `<currencies> ... </currencies>`
currency | Конкретная валюта | `<currency id="RUR" rate="1" />`
categories | Контейнер для категорий | `<categories> ... </categories>`
category | Категория | `<category id="1">Автобусы</category>`
offers | Каталог | `<offers> ... </offers>`

### Тэги запчасти
Имя | Описание | Пример
--- | --- | ---
offer | Главный тэг запчасти | `<offer id="*Тут страшный набор из 20 символов*" available="True"> ... </offer>`
url | Ссылка на карточку | `<url>*Ссылка*</url>`
name | Наименование | `<name>Жгут проводов ...</name>`
price | Цена | `<price>199910</price>`
currencyId | Id валюты | `<currencyId>RUR</currencyId>`
categoryId | Id категории | `<categoryId>41</categoryId>`
picture | Ссылка на фото | `<picture> ... </picture>`
pickup | | `<pickup>true</pickup>`
delivery | | `<delivery>true</delivery>`
store | | `<store>true</store>`
vendorCode | Артикул запчасти | `<vendorCode>0005499</vendorCode>`
description | Описание (повторяет наименование) | `<description> ... </description>`
param | Различные параметры карточки | `<param name="Артикул">0420110</param>`
count | Количество запчастей в наличии | `<count>14</count>`
sales_notes | Уточнения по поводу, оплаты, доставки и тп | `<sales_notes> ... </sales_notes>`

## Яндекс.Директ
`Отличие лишь в том, что в этой выгрузке не участвуют запчасти, в карточках которых нет фото`