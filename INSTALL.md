# Инструкции по установке и запуску

## Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL (при локальном запуске)

## Быстрый запуск через Docker

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd InvestEra
   ```

2. Создайте файл `.env` с переменными окружения:
   ```bash
   cat > .env << EOF
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/investera
   OPENAI_API_KEY=your_openai_api_key_here
   MAX_RECURSION_DEPTH=5
   EOF
   ```

3. Запустите проект:
   ```bash
   docker-compose up --build
   ```

4. Приложение будет доступно по адресу: http://localhost:8000

## Локальный запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите PostgreSQL и создайте базу данных:
   ```sql
   CREATE DATABASE investera;
   ```

3. Настройте переменные окружения:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/investera"
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

4. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Тестирование

1. Проверьте работу парсера:
   ```bash
   python test_app.py
   ```

2. Проверьте API:
   ```bash
   curl -X GET "http://localhost:8000/health"
   ```

3. Протестируйте парсинг статьи:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/parse" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"}'
   ```

4. Получите summary статьи:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/summary?url=https://en.wikipedia.org/wiki/Python_(programming_language)"
   ```

## Документация API

После запуска приложения, документация будет доступна по адресу:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Структура базы данных

Приложение автоматически создаст необходимые таблицы при запуске. Основная таблица `articles` содержит:
- `id` - уникальный идентификатор
- `url` - URL статьи
- `title` - заголовок статьи
- `content` - содержание статьи
- `depth_level` - уровень вложенности при рекурсивном парсинге
- `summary` - краткое содержание (генерируется AI)
- `summary_generated` - флаг генерации summary
- `parent_id` - ссылка на родительскую статью
- `created_at`, `updated_at` - временные метки

## Настройка OpenAI API

1. Получите API ключ на https://platform.openai.com/
2. Добавьте ключ в файл `.env` или экспортируйте как переменную окружения
3. При отсутствии ключа summary не будет генерироваться

## Отладка

Для включения подробного логирования добавьте в `.env`:
```
LOG_LEVEL=DEBUG
```

## Производительность

- Рекурсивный парсинг может занять несколько минут для глубоких уровней
- Генерация summary выполняется в фоновом режиме
- При большой нагрузке рекомендуется масштабирование базы данных 