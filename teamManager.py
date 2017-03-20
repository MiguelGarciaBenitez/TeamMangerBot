#!/usr/local/bin/python
# coding: utf-8
"""
This modules are needed for the system to work
http://influxdb-python.readthedocs.io/en/latest/include-readme.html
https://geekytheory.com/telegram-programando-un-bot-en-python/
"""
import telebot
from telebot import types
import time
import argparse

TOKEN = '344940006:AAFvqea_iXiClcFcZDE4cDc5eaHg0vnlucY'

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

users = [[0 for x in range(5)] for y in range(50)]
#0: uid
#1: name
#2: winings
#3: loses
#4: matches
players = []
#0: uid
place = ""

idArt = 1

commands = {  # command description used in the "help" command
              'start': 'Inicia el bot',
              'help': 'Muestra los comandos',
              'voy': 'Te añade a la lista',
              'novoy': 'Te borra de la lista',
              'reset': 'Resetea la lista de jugadores',
              'lista': 'Muestra la lista de jugadores',
              'donde': 'Modifica el lugar del encuentro',
              'usuarios': 'Muestra los usuarios',
              'add' : 'Añade a un jugador a lista'
}

imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard


hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print "New user detected, who hasn't used \"/start\" yet"
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Hola, usa /help para ver los comandos")
        command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, "Hola, usa /help para ver los comandos")
    command_read(m)

# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Los siguientes comandos estan disponibles: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page
# help page
@bot.message_handler(commands=['reset'])
def command_help(m):
    cid = m.chat.id
    global players
    players = []
    bot.send_message(cid, "La lista de jugadores se ha vaciado")  # send the generated help page

# chat_action example (not a good one...)
@bot.message_handler(commands=['voy'])
def command_add(m):
    global users
    global playes
    i = 0
    cid = m.chat.id
    if cid > 0:
        cname = m.chat.first_name # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
    else:
        cname = m.from_user.first_name # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    if len(players) > 9:
        bot.send_message(cid, "La /lista esta llena, lo siento")
        return 0
    #actualiza la id del jugador en users
    for user in users:
        if user[1] == (cname.lower()).capitalize():
            #actualza la id del jugador en players
            for pid in players:
                if pid == user[0]:
                    players[i] = cid
                    break
                i += 1
            user[0] = cid
    if cid in players:
        bot.send_message(cid, "Ya estas en la /lista")
        # return jugadores[uid]
    else:
        players.append(cid)
        users[len(players)-1][0] = cid
        users[len(players)-1][1] = cname
        bot.send_message(cid, "Hola " + cname +", has sido anadido a la /lista")
        print "New user add to list"
    command_write(m)


@bot.message_handler(commands=['novoy'])
def command_remove(m):
    cid = m.chat.id
    if cid > 0:
        cname = m.chat.first_name # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
    else:
        cname = m.from_user.first_name # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    i = 0
    #actualiza la id del jugador en users
    for user in users:
        if user[1] == (cname.lower()).capitalize():
            #actualza la id del jugador en players
            for pid in players:
                if pid == user[0]:
                    players.remove(pid)
                    break
                i += 1
            user[0] = cid

    if cid in players:
        players.remove(cid)
        bot.send_message(cid, "Has sido borrado de la /lista")
        print "New user remove to list"
        # return jugadores[uid]
    else:
        bot.send_message(cid, "No estas en la /lista")
        return 0

# user can chose an image (multi-stage command example)
@bot.message_handler(commands=['lista'])
def command_image(m):
    cid = m.chat.id
    if cid > 0:
        cname = m.chat.first_name # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
    else:
        cname = m.from_user.first_name # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    uid = 1
    i = 1
    string = ""
    if len(players) == 0:
        bot.send_message(cid, "Lista vacia")
    else:
        string = "Lista de jugadores: \n"
        for pid in players:
            for user in users:
                if user[0] == pid:
                    cname = user[1]
                    uid = user[0]
                    break
            string += " %d. %s\n" % (i, cname)
            i = i +1
        if len(place) >= 0:
            string += "\nDonde:\n" + place
        bot.send_message(cid, string)

@bot.message_handler(commands=['usuarios'])
def command_image(m):
    cid = m.chat.id
    if cid > 0:
        cname = m.chat.first_name # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
    else:
        cname = m.from_user.first_name # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    i = 1
    string = "Lista de usuarios: \n"
    for user in users:
        cname = user[1]
        uid = user[0]
        if uid == 0:
            break
        string += " %d. %s . %d\n" % (i, cname, uid)
        i = i +1
    bot.send_message(cid, string)


@bot.message_handler(commands=['add'])
def command_addS(m):
    global idArt
    global users
    global players
    cid = m.chat.id
    cname = m.text[5:15]
    i = 0
    if len(players) > 9:
        bot.send_message(cid, "La /lista esta llena, lo siento")
    else:
        if len(cname) > 0:
            for user in users:
                if user[1] == (cname.lower()).capitalize():
                    if user[0] in players:
                        bot.send_message(cid,(cname.lower()).capitalize()+" ya esta en la /lista")
                        return 0
                    else:
                        players.append(user[0])
                        bot.send_message(cid, "Has anadido a "+ (cname.lower()).capitalize()+" a la /lista")
                        print "New user add to list"
                        return 0
            users[len(players)][0] = idArt
            users[len(players)][1] = (cname.lower()).capitalize()
            players.append(idArt)
            idArt += 1
            bot.send_message(cid, "Has creado a "+ (cname.lower()).capitalize()+" y anadido a la /lista")
            print "New user add to list"
            return 0

@bot.message_handler(commands=['donde'])
def command_addS(m):
    global place
    cid = m.chat.id
    message = m.text[7:50]
    if len(message) > 0:
        place = message
        bot.send_message(cid, "Has establecido un lugar")

def command_write(m):
    global users
    # Open a file
    fo = open("users.txt", "wb")
    for user in users:
        #print str(user[0])+"|"+str(user[1])
        #Write
        fo.write(str(user[0])+"_"+str(user[1])+"|")
    # Close opend file
    fo.close()

def command_read(m):
    global users
    i=0
    auxUserR = ""
    # Open a file
    try:
        fo = open("users.txt", "r+")
        string =fo.read()
        usersR = string.split("|")
        for userR in usersR:
            if i<50:
                auxUserR = userR.split("_")
                users[i][0] = int(float(auxUserR[0]))
                users[i][1] = str(auxUserR[1])
                i += 1
        # Close opend file
        fo.close()
    except Exception:
        print "user.txt no encontrado"
bot.polling()
