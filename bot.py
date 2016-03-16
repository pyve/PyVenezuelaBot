import telebot
from lxml.etree import fromstring
from lxml.cssselect import CSSSelector
import re

pypi_base_url = "https://pypi.python.org/pypi/"
bot = telebot.TeleBot("148844762:AAEYUrHETWR61EV7cysP6vssnZrhwETi4_8")
f = open("simple.html")
h = fromstring(f.read())
sel = CSSSelector("a")
packages = []
for e in sel(h):
    packages.append(e.get("href"))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hola! Estoy a tu servicio. Para una lista de comandos escribe /help, soy un bot en construccion")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, "Hola! Soy PyVeBot!\nSoy un bot para hacer mas simple la busqueda y enlace a paquetes del repositorio PyPi!\nFui creado por @DrBomb y tengo un repositorio con mi codigo fuente en https://github.com/DrBomb/PyVenezuelaBot")

@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message,"/help para esta ayuda\n/pypi para link directo\n/pysearch para busqueda de paquete\n/about sobre este bot")

@bot.message_handler(commands=['pypi'])
def pypi(message):
    if message.text is "/pypi":
      return    
    bot.reply_to(message,locate_or_list(message.text[6:]))

@bot.message_handler(commands=['pysearch'])
def pysearch(message):
    response = list_packages(message.text[10:])
    splitted_text = util.split_string(response, 3000)
    for text in splitted_text:
        bot.reply_to(message,text)

def list_packages(argument):
    count = 0
    results = []
    regexp = re.compile(argument,re.IGNORECASE)
    for x in packages:
        if regexp.search(x) is not None:
            results.append(x)
            count+=1
    if count==0:
        return package_not_found(argument)
    else:
        return package_list(argument,results,count)

def locate_or_list(argument):
    if argument.lower() in packages:
      return package_located(argument)
    regexp = re.compile(argument,re.IGNORECASE)
    count = 0
    results = []
    for x in packages:
        if regexp.search(x) is not None:
            results.append(x)
            count+=1
    if count==0:
        return package_not_found(argument)
    else:
        return package_list(argument,results,count)

def package_located(argument):
    return pypi_base_url + argument

def package_not_found(argument):
    return "Su busqueda regreso 0 resultados"

def package_list(argument,results,count):
    response = "{} Resultados:\n".format(count) if count>1 else "{} Resultado:\n".format(count)
    for x in results:
      response += x + "\n"
    return response

if __name__=="__main__":
    bot.polling()
