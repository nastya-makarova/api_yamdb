# Проект Yamdb (v1)

## Описание проекта
### Проект YaMDb собирает отзывы пользователей на произведения.  
Произведения делятся на категории. Произведению может быть присвоен жанр из списка предустановленных.
Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку.
На одно произведение пользователь может оставить только один отзыв. Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

## Установка

### Клонировать репозиторий и перейти в него в командной строке:

```git@github.com:Kukus89/api_yamdb.git```

```cd api_yamdb```

### Cоздать и активировать виртуальное окружение:

```python3 -m venv env```

```source env/bin/activate```

### Установить зависимости из файла requirements.txt:

```python3 -m pip install --upgrade pip```

```pip install -r requirements.txt```

### Выполнить миграции:

```python3 manage.py migrate```

### Запустить проект:

```python3 manage.py runserver```

## Примеры запросов к API.

+ Получить список всех произведений.

  ```GET http://127.0.0.1:8000/api/v1/titles/```
  
  Пример ответа с пагинацией:

```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "^-$"
        }
      ],
      "category": {
        "name": "string",
        "slug": "^-$"
      }
    }
  ]
}

```

+ Добавление нового произведения. Права доступа: Администратор.
  
  ```POST http://127.0.0.1:8000/api/v1/titles/```

```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}

```

  Пример ответа:
```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {}
  ],
  "category": {
    "name": "string",
    "slug": "^-$"
  }
}
```

+ Получение публикации по id.
  
  ```GET http://127.0.0.1:8000/api/v1/posts/{id}/```

  Пример ответа:
  ```
  {
    "id": 0,
    "author": "string",
    "text": "string",
    "pub_date": "2019-08-24T14:15:22Z",
    "image": "string",
    "group": 0
  }
  ```

+ Получение списка всех отзывов.

  ```GET http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/```

  Пример ответа:
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {}
  ]
}
```

### Документация для API Yatube доступна:

```http://127.0.0.1:8000/redoc/```


В директории /api_yamdb/static/data, подготовлены несколько файлов в формате csv с контентом для ресурсов 
Users, Titles, Categories, Genres, Reviews и Comments.  Для загрузки данных используйте management-команду, 
добавляющую данные в БД через Django ORM:

```python manage.py load_csv_data```