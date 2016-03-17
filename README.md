[![Build Status](https://travis-ci.org/pyve/PyVenezuelaBot.svg?branch=master)](https://travis-ci.org/pyve/PyVenezuelaBot)

# PyVenezuelaBot
Bot para el canal de Telegram Python Venezuela

# Usar y depurar:

```bash
$ git clone git@github.com:pyve/PyVenezuelaBot.git
$ cd PyVenezuelaBot
$ sudo pip install -r requirements.txt
$ export TELEGRAM_TOKEN=YOUR_TOKEN#GENERATED-https://github.com/eternnoir/pyTelegramBotAPI#prerequisites
$ ./bot.py
```

# Debug:

```bash
$ ./bot.py --debug
```

Nota: en Ubuntu tendrás problemas con la lib lxml, borrala de los requirements e instalala con `sudo apt-get install python-lxml`

Eso es todo intenta establecer un chat en telegram con tu nombre bot de pruebas y listo.
