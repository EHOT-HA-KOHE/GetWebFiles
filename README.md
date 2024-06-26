# Инструкция по настройке проекта

Данные инструкции помогут вам создать виртуальное окружение, установить необходимые зависимости и запустить основной скрипт проекта.

---

## Заполнить своими данными файл tg_connection_data.json

---

# Первый вариант:

```bash
chmod +x start_copy_bot.sh
```

```bash
./start_copy_bot.sh
```

---

# Второй вариант:

## Шаг 1: Создание виртуального окружения

Перед установкой зависимостей рекомендуется создать виртуальное окружение для изоляции пакетов проекта. Откройте терминал и выполните следующие команды.

```bash
python3.11 -m venv venv
```

## Шаг 2: Активация виртуального окружения

После создания виртуального окружения его необходимо активировать.

```bash
source venv/bin/activate
```

## Шаг 3: Установка зависимостей

Все необходимые зависимости перечислены в файле `requirements.txt`. Устанавливаем их следующей командой:

```bash
pip install -r requirements.txt
```

## Шаг 4: Запуск приложения

Теперь, когда все зависимости установлены, вы можете запустить главный скрипт проекта.

```bash
python3.11 main.py
```
