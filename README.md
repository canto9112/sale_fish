# Магазин по продаже рыбы в Телеграм

Телеграм магазин подключен к CMS [elasticpath](https://www.elasticpath.com/). 
Выводится список товаров из CMS в ввиде inline кнопок.


* Пример бота в [Телеграм](https://t.me/sale_fish_devman_bot)


Скрипт ```telegram_bot.py``` запускает магазин в Телеграм.

### Как установить

У вас уже должен быть установлен Python 3. Если его нет, то установите.
Так же нужно установить необходимые пакеты:
```
pip3 install -r requirements.txt
```

### Как пользоваться скриптом

Для работы скрипта нужно создать файл ```.env``` в директории где лежит скрипт.

#### Настройки для Телеграм

1. Нужно создать бота в телеграм. Написать [Отцу ботов](https://telegram.me/BotFather):
    * /start
    * /newbot
    
2. Отец ботов попросит ввести два имени. 

    * Первое — как он будет отображаться в списке контактов, можно написать на русском. 

    * Второе — имя, по которому бота можно будет найти в поиске. 
      Должно быть английском и заканчиваться на bot (например, notification_bot)

3. Вставьте ваш токен бота в файл ```.env```:
    ```
    TELEGRAM_TOKEN=95132391:wP3db3301vnrob33BZdb33KwP3db3F1I
    ```

#### Настройки для CMS

1. Создать магазин в [elasticpath](https://www.elasticpath.com/).

2. Во вкладке Home найти ```Client ID``` и ```Client secret``` и вставить в файл ```.env```:
    ```
    MOLTIN_CLIENT_ID=cFfCsS4oEMrC8dtKyDMwgL8oVams5t9DkRmfT66u2p
    MOLTIN_CLIENT_SECRET=JvR0CFkcix46KtGz3bzwWoUJ5BzyWC9HTHU3XUIG81
    ```

#### Настройки для базы данных (Redis)

Вставить ваши данные в файл ```.env```:

``` 
REDIS_HOST='redis-16132.c263.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT=16143
REDIS_PASSWORD='tUN6QoJldZNMSXr9uV7DmSbWf1IwZwLX'
```
   
### Запуск скрипта
Для запуска магазина вам необходимо запустить командную строку и перейти в каталог со скриптом:
```
>>> python3 telegram_bot.py
```

### Цели проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
