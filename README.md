## Устанока

https://github.com/mshinkareva/Auth_sprint_1

1. Прописать переменные окружения в файлах /auth-service/env
2. Сгеренировать пары ключей для /auth-service/nginx/ssl.key /auth-service/nginx/ssl.pem
3. Перейти в директорию с docker-compose.yaml
4. Запустить установку
```bash
docker-compose up -d --build --force-recreate
```
5. Сервис доступен по адресу https://127.0.0.1/api/openapi#/
