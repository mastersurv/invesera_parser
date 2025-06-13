# InvestEra Wikipedia Parser

Парсер статей Википедии с рекурсивным извлечением связанных статей и генерацией краткого содержания с помощью AI.

## Функциональность

- Рекурсивный парсинг статей Википедии (глубина 5 уровней)
- Сохранение статей в PostgreSQL базе данных
- Генерация краткого содержания с помощью OpenAI API
- Асинхронная обработка запросов
- RESTful API на базе FastAPI

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **OpenAI API** - генерация краткого содержания
- **Docker** - контейнеризация
- **Dependency Injector** - внедрение зависимостей

## Структура проекта

```
app/
├── ai/                     # AI сервисы
│   └── summary_generator.py
├── api/                    # API эндпоинты
│   └── endpoints.py
├── parsers/                # Парсеры
│   └── wikipedia_parser.py
├── repositories/           # Репозитории
│   └── article_repository.py
├── services/               # Бизнес-логика
│   └── article_service.py
├── config.py              # Конфигурация
├── containers.py          # DI контейнер
├── database.py            # Настройки БД
├── models.py              # Модели БД
├── schemas.py             # Pydantic схемы
└── main.py                # Главный файл приложения
```

## Запуск проекта

### Через Docker (рекомендуется)

1. Клонируйте репозиторий
2. Создайте файл `.env` на основе `.env.example`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/investera
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Запустите проект:
   ```bash
   docker-compose up --build
   ```

### Локальный запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите PostgreSQL
3. Настройте переменные окружения
4. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Эндпоинты

### POST /api/v1/parse
Запуск парсинга статьи Википедии

**Тело запроса:**
```json
{
  "url": "https://ru.wikipedia.org/wiki/Python"
}
```

**Ответ:**
```json
{
  "id": 1,
  "url": "https://ru.wikipedia.org/wiki/Python",
  "title": "Article Name",
  "content": "Article content...",
  "depth_level": 0,
  "summary": "AI generated summary...",
  "summary_generated": true,
  "created_at": "2024-01-01T00:00:00Z",
  "parent_id": null,
  "children": []
}
```

### GET /api/v1/summary?url={url}
Получение краткого содержания статьи

**Параметры:**
- `url` - URL статьи Википедии

**Ответ:**
```json
{
  "url": "https://ru.wikipedia.org/wiki/Python",
  "title": "Article Name",
  "summary": "AI generated summary...",
  "summary_generated": true
}
```

### POST /api/v1/generate-summaries
Генерация краткого содержания для всех статей без summary

## Особенности реализации

- **Рекурсивный парсинг**: автоматически извлекает и парсит связанные статьи до 5 уровней глубины
- **Асинхронность**: все операции выполняются асинхронно для максимальной производительности
- **Dependency Injection**: использование паттерна DI для слабой связанности компонентов
- **Repository/Service слои**: четкое разделение ответственности между слоями
- **Обработка ошибок**: централизованная обработка ошибок с понятными сообщениями

## Конфигурация

Основные настройки находятся в `app/config.py`:

- `DATABASE_URL` - строка подключения к PostgreSQL
- `OPENAI_API_KEY` - ключ API OpenAI
- `MAX_RECURSION_DEPTH` - максимальная глубина рекурсивного парсинга (по умолчанию 5)

## Мониторинг

Доступны эндпоинты для мониторинга:
- `GET /` - информация о приложении
- `GET /health` - проверка состояния приложения
- `GET /docs` - интерактивная документация API (Swagger UI) 