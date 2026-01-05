# User Platform - Kubernetes Deployment

Проект представляет собой микросервисное веб-приложение для управления пользователями, развернутое в Kubernetes. Основная цель проекта - демонстрация навыков работы с Kubernetes, включая Deployments, Services, ConfigMaps, Secrets, StatefulSet, CronJobs и Helm Charts.

## Архитектура приложения

Приложение состоит из следующих компонентов:

### Микросервисы (Backend)

1. **auth-service** (порт 8001)
   - Регистрация пользователей
   - Авторизация (логин)
   - Валидация JWT токенов
   - Health endpoints: `/health/live`, `/health/ready`

2. **profile-service** (порт 8002)
   - Получение профиля пользователя
   - Обновление профиля
   - Health endpoints: `/health/live`, `/health/ready`

3. **notification-service** (порт 8003)
   - Получение уведомлений
   - Отправка уведомлений
   - Health endpoints: `/health/live`, `/health/ready`

4. **report-service** (порт 8004)
   - Генерация отчетов
   - Список отчетов
   - Health endpoints: `/health/live`, `/health/ready`

### Frontend

- **frontend** (порт 80)
  - Главная страница
  - Страница авторизации
  - Страница регистрации
  - Личный кабинет пользователя
  - Доступ через NodePort на порту 30080

### База данных

- **PostgreSQL** (порт 5432)
  - Хранение данных пользователей
  - Таблица `users` с полями: id, username, password_hash, email, status, created_at

## Структура проекта

```
UserPlatform/
├── auth-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── profile-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── notification-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── report-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
├── database/
│   └── init.sql
└── helm/
    └── user-platform/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── namespace.yaml
            ├── configmap.yaml
            ├── secret.yaml
            ├── postgres.yaml
            ├── auth-service.yaml
            ├── profile-service.yaml
            ├── notification-service.yaml
            ├── report-service.yaml
            ├── frontend.yaml
            └── cronjobs.yaml
```

## Требования

- Minikube
- kubectl
- Docker
- Helm

## Развертывание

1. **Запуск Minikube:**
   ```bash
   minikube start
   ```

2. **Сборка Docker образов:**
   ```bash
   eval $(minikube docker-env)
   docker build -t auth-service:latest ./auth-service
   docker build -t profile-service:latest ./profile-service
   docker build -t notification-service:latest ./notification-service
   docker build -t report-service:latest ./report-service
   docker build -t frontend:latest ./frontend
   ```

3. **Установка через Helm:**
   ```bash
   helm install user-platform ./helm/user-platform -n user-platform --create-namespace
   ```

4. **Проверка статуса:**
   ```bash
   kubectl get all -n user-platform
   ```

5. **Доступ к приложению:**
   ```bash
   minikube service frontend-service -n user-platform
   ```
   Или напрямую через NodePort:
   ```bash
   minikube ip
   # Откройте браузер: http://<minikube-ip>:30080
   ```

### Обновление и управление

**Обновление конфигурации:**
   ```bash
   helm upgrade user-platform ./helm/user-platform -n user-platform
   ```

**Просмотр значений:**
   ```bash
   helm show values ./helm/user-platform
   ```

**Удаление:**
   ```bash
   helm uninstall user-platform -n user-platform
   ```

## Конфигурация

### ConfigMap (ui-config)

Содержит конфигурацию интерфейса:
- `LOGIN_TITLE`: "Вход в систему"
- `REGISTER_TITLE`: "Регистрация"
- `WELCOME_MESSAGE`: "Добро пожаловать в платформу"

### Secret (app-secrets)

Хранит конфиденциальные данные:
- `db-password`: пароль базы данных
- `jwt-secret`: секретный ключ для JWT токенов

### Health Probes

Все сервисы имеют настроенные Liveness и Readiness probes:
- **LivenessProbe**: HTTP GET на `/health/live`
- **ReadinessProbe**: HTTP GET на `/health/ready`
- **Параметры**: `initialDelaySeconds: 30`, `periodSeconds: 10`

### Replicas

Все сервисы развернуты с минимум 2 репликами для обеспечения высокой доступности:
- auth-service: 2 реплики
- profile-service: 2 реплики
- notification-service: 2 реплики
- report-service: 2 реплики
- frontend: 2 реплики
- postgres: 1 реплика

## CronJobs

Приложение включает 3 автоматизированные фоновые задачи:

1. **daily-stats-collector**
   - Расписание: `0 2 * * *` (каждый день в 2:00)
   - Задача: сбор статистики по пользователям за последние 24 часа

2. **notification-sender**
   - Расписание: `0 9 * * *` (каждый день в 9:00)
   - Политика конкурентности: `Forbid`
   - Задача: отправка уведомлений пользователям

3. **data-cleanup**
   - Расписание: `0 0 * * 0` (каждое воскресенье в 00:00)
   - Задача: очистка устаревших данных

## Использование приложения

### Тестовый пользователь

По умолчанию создается тестовый пользователь:
- **Логин**: `admin`
- **Пароль**: `admin123`

### API Endpoints

#### Auth Service
- `POST /api/register` - Регистрация нового пользователя
- `POST /api/login` - Вход в систему
- `POST /api/validate` - Валидация JWT токена

#### Profile Service
- `GET /api/profile` - Получение профиля (требует Authorization header)
- `PUT /api/profile` - Обновление профиля (требует Authorization header)

#### Notification Service
- `GET /api/notifications` - Получение уведомлений (требует Authorization header)
- `POST /api/notifications/send` - Отправка уведомления

#### Report Service
- `POST /api/reports/generate` - Генерация отчета (требует Authorization header)
- `GET /api/reports/list` - Список отчетов (требует Authorization header)

## Проверка работы сервисов

### kubectl port-forward

Для проверки каждого сервиса можно использовать port-forward:

```bash
kubectl port-forward service/auth-service 8001:8001 -n user-platform
kubectl port-forward service/profile-service 8002:8002 -n user-platform
kubectl port-forward service/notification-service 8003:8003 -n user-platform
kubectl port-forward service/report-service 8004:8004 -n user-platform
```

После запуска port-forward сервис будет доступен на `http://localhost:<порт>`

### Способ 2: Проверка через curl (с использованием токена)

1. **Получите JWT токен** (войдите через фронтенд и скопируйте токен из localStorage браузера, или используйте curl):

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:\<port\>/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

echo "Token: $TOKEN"
```

2. **Проверка Profile Service:**
```bash
curl -X GET http://127.0.0.1:\<port\>/api/profile \
  -H "Authorization: Bearer $TOKEN" | jq

curl -X PUT http://127.0.0.1:\<port\>/api/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"newemail@example.com"}' | jq
```

3. **Проверка Notification Service:**
```bash
curl -X GET http://127.0.0.1:\<port\>/api/notifications \
  -H "Authorization: Bearer $TOKEN" | jq

curl -X POST http://127.0.0.1:\<port\>/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"message":"Test notification"}' | jq
```

4. **Проверка Report Service:**
```bash
curl -X POST http://127.0.0.1:\<port\>/api/reports/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"user_stats"}' | jq

curl -X GET http://127.0.0.1:\<port\>/api/reports/list \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Проверка Health Endpoints

Все сервисы имеют health endpoints, которые можно проверить без авторизации:

```bash
kubectl exec -it deployment/auth-service -n user-platform -- curl http://localhost:8001/health/live
```

## Мониторинг и отладка

### Просмотр логов

```bash
# Логи конкретного сервиса
kubectl logs -f deployment/auth-service -n user-platform
kubectl logs -f deployment/profile-service -n user-platform
kubectl logs -f deployment/notification-service -n user-platform
kubectl logs -f deployment/report-service -n user-platform
kubectl logs -f deployment/frontend -n user-platform
kubectl logs -f deployment/postgres -n user-platform
```

### Просмотр CronJobs

```bash
# Список CronJobs
kubectl get cronjobs -n user-platform

# Просмотр Jobs, созданных CronJob
kubectl get jobs -n user-platform

# Логи конкретного Job
kubectl logs job/<job-name> -n user-platform
```

### Проверка статуса подов

```bash
kubectl get pods -n user-platform
kubectl describe pod <pod-name> -n user-platform
```

### Проверка сервисов

```bash
kubectl get services -n user-platform
kubectl describe service <service-name> -n user-platform
```

### Проверка ConfigMap и Secret

```bash
kubectl get configmap -n user-platform
kubectl get secret -n user-platform
kubectl describe configmap ui-config -n user-platform
```

## Масштабирование

### Увеличение количества реплик

```bash
kubectl scale deployment auth-service --replicas=3 -n user-platform
```

Или через Helm:
```bash
helm upgrade user-platform ./helm/user-platform -n user-platform --set replicas.authService=3
```

## Удаление

### Удаление через kubectl

```bash
kubectl delete namespace user-platform
```

### Удаление через Helm

```bash
helm uninstall user-platform -n user-platform
kubectl delete namespace user-platform
```

## Особенности реализации

1. **Микросервисная архитектура**: Приложение разделено на 4 независимых сервиса
2. **Высокая доступность**: Все сервисы развернуты с минимум 2 репликами
3. **Health checks**: Все сервисы имеют настроенные Liveness и Readiness probes
4. **Безопасность**: Конфиденциальные данные хранятся в Secrets
5. **Конфигурация**: UI конфигурация вынесена в ConfigMap
6. **Автоматизация**: Использование CronJobs для фоновых задач
7. **Управление**: Helm Chart для удобного управления развертыванием

## Технологии

- **Backend**: Python 3.11, Flask
- **Frontend**: HTML, CSS, JavaScript, Nginx
- **Database**: PostgreSQL 15
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Package Management**: Helm

## Примечания

- Все сервисы являются демонстрационными и могут содержать упрощенную логику
