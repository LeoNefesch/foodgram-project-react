### О чём проект?
##### Проект написан с применением архитектуры REST и контейнеризации.
##### Представляет из себя сайт со следующим функционалом:
 - авторизация и аутентификация пользователя;
 - добавление, редактирование и удаление пользователем своих рецептов;
 - добавление чужих рецептов в избранное;
 - возможность подписываться на публикации других авторов;
 - создание списка продуктов для приготовления выбранных блюд.


 **Стэк технологий:**
 - IDE VSCode;
 - терминал Linux;
 - Python 3.9.5;
 - Django 3.2.3;
 - djangorestframework 3.12.4;
 - djoser;
 - Pillow;
 - gunicorn;
 - nginx;
 - Docker;
 - GitHub Actions;
 - PostgreSQL
 - React

**Польза проекта**
- наглядный пример контейнеризации;
- иллюстрация возможностей авторизованных и неавторизованных пользователей;
- возможности сайта применимы в повседневной жизни.

### Как запустить проект:

##### Клонировать репозиторий:

```
git clone git@github.com:LeoNefesch/foodgram-project-react.git
```

##### В головной директории проекта создать файл с переменными окружения

```
cd foodgram-project-react/
touch .env
nano .env
```
Файл .env должен содержать следующие переменные:

```
POSTGRES_USER=<пользователь_БД>
POSTGRES_PASSWORD=<пароль_пользователя_БД>
POSTGRES_DB=<имя_БД>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<django-insecure-сгенерированный_на_https://djecrety.ir/_ключ_для_джанго>
ALLOWED_HOSTS=<список_используемых_доменных_имён_и_IP_адресов>
PORT_NGINX=<порт_на_который_пойдут_все_запросы_в_Docker>

```
##### Установка Docker

```
sudo apt update
```
```
sudo apt install curl
```
```
curl -fSL https://get.docker.com -o get-docker.sh
```
```
sudo sh ./get-docker.sh
```
##### Установка утилиты Docker Compose

```
sudo apt-get install docker-compose-plugin
```
##### Убедитесь, что докер запущен

```
sudo service docker status
```
##### В директории foodgram-project-react/backend создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```
    или
    ```
    . venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Обновить pip:

```
python3 -m pip install --upgrade pip
```

Установить flake:

```
pip install flake8==6.0.0 flake8-isort==6.0.0
```

Создать в головной директории файл setup.cfg (для исключений flake'а) с содержимым:

```
[flake8]
ignore =
    I001,
    I003,
    I005,
    W503,
    F811
exclude = 
    tests/,
    */migrations/,
    venv/,
    */venv/,
    env/
    */env/,
per-file-ignores =
    */settings.py:E501
```

Запустить проверку flake'ом из головной директории и убедиться, что локально все тесты пройдены.
   
##### Стянуть образы для проекта с DockerHub

```
sudo docker compose -f docker-compose.production.yml pull
```

##### Остановить работающие контейнеры

```
sudo docker compose -f docker-compose.production.yml down
```

##### Запустить контейнеры в фоне

```
sudo docker compose -f docker-compose.production.yml up -d
```

##### Выполнить миграции

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

##### Собрать статику бэкенда

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

##### Скопировать статику в директорию, связанную с volume static

```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collect_static/. /static_backend/static/
```


### Проект выполнил студент Яндекс Практикума
### [Леонид Негашев](https://github.com/LeoNefesch/)

