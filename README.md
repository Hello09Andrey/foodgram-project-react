[![Django-app workflow](https://github.com/Hello09Andrey/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Hello09Andrey/foodgram-project-react/actions/workflows/main.yml)

API развернут по адресу: [ссылка](http://158.160.31.59/)

# Foodgram
## Описание:
Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии:
- Python 3.10.8
- Django 4.1.7
- PostgreSQL
- Djangorestframework 3.14
- Dotenv 1.0.0
- Djoser 2.1.0

## Запуск проекта:
1. Клонировать репозиторий
```
git@github.com:Hello09Andrey/foodgram-project-react.git
```
2. Перейти в рабочий каталог:
```
cd foodgram-project-react
```
3. Заполнить базу ингредиентами (перейдите в каталог с расположением файла manage.py и выполните команду):

```
python manage.py load_ingredients
```