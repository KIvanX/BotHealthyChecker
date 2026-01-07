# Bot Healthy Checker

Запущенный процесс Telegram-бота не гарантирует, что бот действительно работает.  
Возможны ситуации, когда процесс активен, но бот не отвечает на сообщения (зависание, потеря соединения с Telegram API, логическая ошибка и т.д.). 
Мониторинг процессов (systemd, docker, pm2 и т.д.) показывает только факт запуска процесса.  

**Bot Healthy Checker** — это Telegram-бот для проверки фактической работоспособности другого бота.

## How it works

Healthy Checker раз в минуту:

1. Отправляет тестовое сообщение `/start` проверяемому боту
2. Ожидает любой ответ
3. При отсутствии ответа отправляет уведомление в свой чат

## Why

Мониторинг процессов (systemd, docker, pm2 и т.д.) показывает только факт запуска процесса.  
Healthy Checker проверяет реальную доступность бота через Telegram API.

## How to run

#### 1. Clone repository

```bash
git clone https://github.com/KIvanX/BotHealthyChecker.git
cd BotHealthyChecker
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure environment
Создайте файл .env и укажите необходимые параметры:

```bash
TOKEN=
TELETHON_API_ID=
TELETHON_API_HASH=
```

#### 4. Start bot
```bash
python main.py
```
