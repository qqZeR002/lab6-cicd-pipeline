# Лекция 3. CI/CD

## CI

Continuous Integration: при каждом `push` сервер сам запускает тесты.

- ошибки видно сразу
- в `main` не попадает сломанный код

## CD

Continuous Delivery: после успешных тестов проект сам публикуется.

```yaml
on:
  push:
    branches: [main]
```
