Полный сброс (контейнеры + тома)
docker-compose down -v

Пересборка и запуск
docker-compose up -d --build

Запуск тестов внутри контейнера приложения
docker-compose exec app pytest tests/