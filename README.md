# FOODGRAM

###### Данный проект позволяет добавлять свои рецепты, подписываться на интересных авторых рецептов, добавлять рецепты в избранные, а так же в корзину, откуда уже можно скачать список необходиых ингредиентов для покупки

### Адрес: [51.250.18.120](http://51.250.18.120/)

Мной был реализован бэкенд (DRF) и деплой (Nginx + Gunicorn) приложения на сервер. В качестве фронтенда использован React для сборки файлов.

### Установка и настройка. Для запуска вам потребуются установленные Docker и docker-compose:
1. Клонируйте репозиторий удобным вам способом
1. Перейдите в каталог ***infra***
`cd infra/`
1. создайте .env файл по образцу нижу:
> POSTGRES_PASSWORD=YOUR_PASSWORD

1. Для запуска проекта выполните следующее:
`sudo docker-compose up -d --build`
1. Выполните миграции внутри контейнера **backend**:
`sudo docker-compose exec backend python3 manage.py migrate`
1. Соберите статику:
`sudo docker-compose exec backend python3 manage.py collectstatic`
1. Загрузите в базу созданные ранее ингредиенты и теги:
`sudo docker-compose exec backend python3 manage.py read_data_from_json`
1. Создайте суперпользователя:
`sudo docker-compose exec backend python3 manage.py createsuperuser`

### Для проверки админки доступна комбинация:
> username: admin
> password: admin