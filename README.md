**Автор:** Приладышев Юрий Владимирович, БПИ238


## Описание проекта

Проект реализует интернет-магазин с разделением на микросервисы:

- **API Gateway** (порт 8005) — маршрутизация REST-запросов
- **Orders Service** (порт 8002) — управление заказами, асинхронная обработка через RabbitMQ с использованием Transactional Outbox
- **Payments Service** (порт 8001) — управление кошельками и платежами с использованием Transactional Inbox/Outbox
- **Frontend** — веб-интерфейс (порт 80) и десктоп-приложение (.exe)

### Соответствие критериям КР3

1. **Основные требования к функциональности (2 балла)** ✅
   - Payments Service: создание кошелька, пополнение, просмотр баланса
   - Orders Service: создание заказа, просмотр списка и статуса заказов
   - Асинхронная обработка платежей

2. **Архитектурное проектирование (4 балла)** ✅
   - Четкое разделение на микросервисы
   - Асинхронное взаимодействие через RabbitMQ
   - Transactional Outbox в Orders Service
   - Transactional Inbox/Outbox в Payments Service
   - At-most-once семантика при списании средств

3. **Swagger UI (0.5 балла)** ✅
   - Доступен по адресу http://localhost:8005/docs

4. **Тестовое покрытие > 65% (0.5 балла)** ✅
   - Unit-тесты для всех сервисов

5. **Docker и docker-compose (1 балл)** ✅
   - Все сервисы контейнеризированы
   - Система разворачивается через docker-compose

6. **Frontend (2 балла)** ✅
   - Веб-интерфейс (порт 80)
   - Десктоп-приложение (.exe)

## Запуск проекта

```bash
# Клонирование репозитория
git clone https://github.com/ggenjoyer95/msltrd.git
cd msltrd

# Запуск через Docker Compose
docker-compose up --build

# Или через скрипт
chmod +x start.sh
./start.sh
```

## REST API Endpoints

### Payments Service

| Метод | Путь | Описание | Тело запроса |
|-------|------|----------|--------------|
| POST | `/api/wallet/create` | Создать кошелек | `{"user_id": int}` |
| POST | `/api/wallet/{user_id}/deposit` | Пополнить кошелек | `{"amount": float}` |
| GET | `/api/wallet/{user_id}` | Получить баланс | - |

### Orders Service

| Метод | Путь | Описание | Тело запроса |
|-------|------|----------|--------------|
| POST | `/api/purchase` | Создать заказ | `{"user_id": int, "amount": float, "description": string}` |
| GET | `/api/purchase/{purchase_id}` | Получить статус заказа | - |
| GET | `/api/purchases` | Получить все заказы | - |

## Статусы заказов

- `NEW` - заказ создан
- `FINISHED` - заказ успешно оплачен
- `CANCELLED` - ошибка при оплате (недостаточно средств/нет кошелька)

## Архитектура системы

```plaintext
┌─────────────┐     ┌───────────────┐     ┌─────────────────┐
│             │     │               │     │                 │
│ API Gateway │◄────► Orders Service│◄────► Payments Service│
│ (port 8005) │     │ (port 8002)   │     │  (port 8001)    │
└─────────────┘     └───────────────┘     └─────────────────┘
       ▲                   ▲                      ▲
       │                   │                      │
       │            ┌──────┴──────┐              │
       │            │   RabbitMQ  │              │
       │            │             │              │
       │            └─────────────┘              │
       │                                         │
       │            ┌─────────────┐              │
       └────────────► PostgreSQL  ◄──────────────┘
                    └─────────────┘
```

## Используемые технологии

* **Backend:** Python 3.12, FastAPI, SQLAlchemy
* **Message Broker:** RabbitMQ
* **Database:** PostgreSQL
* **Frontend:** HTML/JS (веб), Desktop приложение (.exe)
* **Контейнеризация:** Docker, Docker Compose
* **Тестирование:** pytest

## Процесс создания заказа

1. Пользователь отправляет запрос на создание заказа
2. Orders Service создает заказ и задачу на оплату (Transactional Outbox)
3. Orders Service отправляет задачу в RabbitMQ
4. Payments Service получает задачу (Transactional Inbox)
5. Payments Service проверяет возможность оплаты:
   - Наличие кошелька
   - Достаточность средств
6. Payments Service отправляет результат обработки
7. Orders Service обновляет статус заказа

## Тестирование

Для запуска тестов:
```bash
pytest
```
