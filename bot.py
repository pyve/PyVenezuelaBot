#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Este es un bot para buscar en pypi por ti cualquier paquete python.
usado en el grupo python Venezuela en telegram.
"""

import telebot
import random
from telebot import util
from lxml.etree import fromstring
from lxml.cssselect import CSSSelector
import re
import os
import click
import logging
import xmlrpclib

logger = telebot.logger

MAX_PACKAGE_RETURN = 50
pypi_base_url = "https://pypi.python.org/pypi/"


def get_token():
    if os.path.isfile("token.txt"):
        with open("token.txt") as t:
            token = t.readline().replace('\n', '')
    else:
        token = os.environ.get('TELEGRAM_TOKEN')
    return token


def get_bot(token):
    return telebot.TeleBot(token)

with open("simple.html") as f:
    h = fromstring(f.read())
    sel = CSSSelector("a")
    packages = []
    for e in sel(h):
        packages.append(e.get("href"))

token = get_token()
bot = get_bot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, "Hola! Estoy a tu servicio. "
        "Para una lista de comandos escribe /help, soy un bot en construccion")


@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, "Hola! Soy PyVeBot!\nSoy un bot para hacer mas "
                 "simple la busqueda y enlace a paquetes del repositorio "
                 "PyPi!\nFui creado por @DrBomb y mantenido por Python "
                 "Venezuela tengo un repositorio con mi codigo fuente en "
                 "https://github.com/pyve/PyVenezuelaBot")


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message, "/help para esta ayuda\n/pypi para link directo\n/pysearch "
        "para busqueda de paquete\n/about sobre este bot")


def get_message(message, info):
    '''
    Just formating the output.
    '''
    if isinstance(info, str):
        return info
    name = info.get('name') or ''
    return '''*{name} {version}*
_{user}_

{summary}

\xE2\xAC\x85 [Visit the Homepage]({home_page}) or...
\xE2\x98\x9D [Go to PyPi Site]({package_url})
'''.format(name=name,
           user=message.from_user and 'via: @' + str(message.from_user.username) or '',
           summary=info.get('summary') or '',
           version=info.get('version') or '',
           package_url=info.get('package_url') or '',
           home_page=info.get('home_page') or '')

def get_search_msg(info):
    return '''*No encontre nada con ese nombre* _pero esto se parece_
{search}'''.format(search=info)

@bot.message_handler(commands=['pypi'])
def pypi(message):
    argument = get_arg(message.text)
    if argument == '' or argument is None:
        return
    info = locate_or_list(argument)
    if not isinstance(info, dict):
        bot.reply_to(message, get_search_msg(info),
                     parse_mode='Markdown')
        return
    if not info.get('name'):
        bot.reply_to(message, 'Sorry not found: %s' % info)
        return
    bot.send_message(message.chat.id, get_message(message, info),
                     parse_mode='Markdown',
                     disable_web_page_preview=True)


@bot.message_handler(commands=['pysearch'])
def pysearch(message):
    argument = get_arg(message.text)
    if argument == '' or argument is None:
        return
    response = list_packages(argument)
    splitted_text = util.split_string(response, 3000)
    for text in splitted_text:
        bot.reply_to(message, text)


def get_arg(argument):
    regexp = re.compile("\/\w*(@\w*)*\s*([\s\S]*)", re.IGNORECASE)
    textmatch = regexp.match(argument)
    return textmatch.group(2)


def list_packages(argument):
    count = 0
    results = []
    regexp = re.compile(argument, re.IGNORECASE)
    for x in packages:
        if regexp.search(x) is not None:
            results.append(x)
            count += 1
    if count == 0:
        return package_not_found(argument)
    elif count > MAX_PACKAGE_RETURN:
        return too_many_packages(argument, results, count)
    else:
        return package_list(argument, results, count)


def locate_or_list(argument):
    if argument.lower() in packages:
        return package_located(argument)
    regexp = re.compile(argument, re.IGNORECASE)
    count = 0
    results = []
    for x in packages:
        if regexp.search(x) is not None:
            results.append(x)
            count += 1
    if count == 0:
        return package_not_found(argument)
    elif count > MAX_PACKAGE_RETURN:
        return too_many_packages(argument, results, count)
    else:
        return package_list(argument, results, count)


def package_located(argument):
    info = {}
    info['url'] = str(pypi_base_url + argument)
    # Using https://wiki.python.org/moin/PyPIXmlRpc
    pkg_info = xmlrpclib.ServerProxy(pypi_base_url, allow_none=True)
    rel = pkg_info.package_releases(argument)
    info['lastest_rel'] = rel and rel[0] or None
    pkg_data = pkg_info.release_data(argument, info['lastest_rel'])
    return pkg_data


def package_not_found(argument):
    return "Su busqueda regreso 0 resultados"


def package_list(argument, results, count):
    response = "{} Resultados:\n".format(
        count) if count > 1 else "{} Resultado:\n".format(count)
    for x in results:
        response += x + "\n"
    return response


def too_many_packages(argument, results, count):
    response = "{} Resultados:\nAlgunos de estos son:\n".format(count)
    for x in range(MAX_PACKAGE_RETURN):
        response += random.choice(results) + "\n"
    return response


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--stop-after-init', is_flag=True)
def serve(debug, stop_after_init):
    if debug:
        telebot.logger.setLevel(logging.DEBUG)
    if stop_after_init:
        # Solo para efectos de prueba:
        # TODO: reemplazar por un mejor entorno
        # unittest y setup.py
        exit()
    bot.polling(none_stop=True)

if __name__ == "__main__":
    serve()
