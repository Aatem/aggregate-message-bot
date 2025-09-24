# aggregate-message-bot

Команда для обновления webhook в Telegram:
curl -F "url=https://aggregate-message-bot.onrender.com/" https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/setWebhook

Команда для проверки webhook:
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

P.s. Render по умолчанию читает webhook с домашней страницы '/', а значит и адрес должен заканчиваться на неё, а не на '/webhook'/
