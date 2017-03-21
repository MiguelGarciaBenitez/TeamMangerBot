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

#users = [[0 for x in range(5)] for y in range(50)]
users = []
#0: uid
#1: name
#2: winings
#3: loses
#4: matches
players = []
#0: uid
#1: name
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
    uid = m.from_user.id
    print m
    try:
        if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
            knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
            userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
            bot.send_message(cid, "Hola, usa /help para ver los comandos")
            command_help(m)  # show the new user the help page
        else:
            bot.send_message(cid, "Hola, usa /help para ver los comandos")
        users = command_Read_Users(m)
        players = command_Read_Players(m)
    except Exception:
        print "ERROR: start"
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
    players = []
    command_Write_Players(m,players)
    bot.send_message(cid, "La lista de jugadores se ha vaciado")  # send the generated help page

# chat_action example (not a good one...)
@bot.message_handler(commands=['voy'])
def command_add(m):
    users = command_Read_Users(m)
    players = command_Read_Players(m)
    flag = 0
    cid = m.chat.id
    if cid > 0:
        uname = m.chat.first_name.lower().capitalize() # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
        uid = m.chat.id
    else:
        uid = m.from_user.id
        uname = m.from_user.first_name.lower().capitalize() # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    playerR = []
    playerR.append(uid)
    playerR.append(uname)
    #actualiza la id del jugador en users
    for user in users:
        if user[1] == uname:
            #actualza la id del jugador en players y users
            user[0] = uid
            flag = 1 #en users
            for j in range(len(players)):
                if players[j][1] == uname:
                    players[j][0] = uid
                    break
    #introducimos en users si no esta
    if flag == 0:
        users.append(playerR)
        bot.send_message(cid,uname +", te has unido a la /lista")
    #comprobamos si cabe  n players
    if len(players) > 9:
        bot.send_message(cid, "La /lista esta llena, lo siento")
    #comprobamos si esta en players
    flag = 0
    for player in players:
        if player[0] == uid:
            if player[1] == uname:
                bot.send_message(cid, uname + ", ya estas en la /lista")
                flag = 1
    #si no esta en players lo introducimos
    if flag == 0:
        players.append(playerR)
    command_Write_Users(m,users)
    command_Write_Players(m,players)
    try:
        print ""
    except Exception:
        print "ERROR: voy"

@bot.message_handler(commands=['novoy'])
def command_remove(m):
    flag = 0
    users = command_Read_Users(m)
    players = command_Read_Players(m)
    cid = m.chat.id
    i = 0
    if cid > 0:
        uname = str(m.chat.first_name.lower().capitalize()) # Si 'cid' es positivo, usaremos 'm.chat.first_name' para el nombre
        uid = m.chat.id
    else:
        uid = m.from_user.id
        uname = str(m.from_user.first_name.lower().capitalize()) # Si 'cid' es negativo, usaremos 'm.from_user.first_name' para el nombre
    playerR = []
    playerR.append(uid)
    playerR.append(uname)
    #actualiza la id del jugador en users
    for user in users:
        if user[1] == uname:
            #actualza la id del jugador en players y users
            user[0] = uid
            flag = 1 #en users
            for j in range(len(players)):
                if players[j][1] == uname:
                    players[j][0] = uid
                    break
    #introducimos en users si no esta
    if flag == 0:
        users.append(playerR)
        bot.send_message(cid,uname +", te has unido a la /lista")
    #comprobamos si esta en players
    flag = 0
    for player in players:
        if player[1] == uname:
            if player[0] == uid:
                players.remove(playerR)
                flag = 1
                bot.send_message(cid, uname + ", has sido borrado de la /lista")
    #no esta en players
    if flag == 0:
        bot.send_message(cid, uname + ", no estas en la /lista")
    command_Write_Users(m,users)
    command_Write_Players(m,players)
    try:
        print ""
    except Exception:
        print "ERROR: novoy"
# user can chose an image (multi-stage command example)
@bot.message_handler(commands=['lista'])
def command_image(m):
    cid = m.chat.id
    users = command_Read_Users(m)
    players = command_Read_Players(m)
    uname = ""
    uid = 1
    i = 1
    string = ""
    if len(players) == 0:
        bot.send_message(cid, "Lista vacia")
    else:
        string = "Lista de jugadores: \n"
        for player in players:
            uid = player[0]
            uname = player[1]
            string += " %d. %s\n" % (i, uname)
            i = i +1
        if len(place) > 0:
            string += "\nDonde:\n" + place
        bot.send_message(cid, string)
    try:
        print ""
    except Exception:
        print "ERROR: lista"
@bot.message_handler(commands=['usuarios'])
def command_image(m):
    users = command_Read_Users(m)
    cid = m.chat.id
    i = 1
    string = "Lista de usuarios: \n"
    for user in users:
        uid = user[0]
        uname = user[1]
        string += " %d. %s\n" % (i, uname)
        i = i +1
    bot.send_message(cid, string)
    try:
        print ""
    except Exception:
        print "ERROR: usuarios"

@bot.message_handler(commands=['add'])
def command_addS(m):
    global idArt
    users = command_Read_Users(m)
    players = command_Read_Players(m)
    cid = m.chat.id
    uid = idArt
    uname = m.text[5:15].lower().capitalize()
    flag = 0
    playerR = []
    playerR.append(str(uid))
    playerR.append(str(uname))
    #comprobamos si esta en players
    if len(players) > 9:
        bot.send_message(cid, "La /lista esta llena, lo siento")
    else:
        for player in players:
            if player[1] == uname:
                flag = 1
                bot.send_message(cid,uname+" ya esta en la /lista")
    #no esta en players, introducir
    if flag == 0:
        if len(uname) > 0:
            #buscamos en users
            for i in range(len(users)):
                if users[i][1] == uname:
                    flag = 1
                    #el usuario existe en users
                    playerR[0] = users[i][0]
            if flag == 0:
                idArt += 1
            #introducir en players
            players.append(playerR)
            bot.send_message(cid, uname + " se ha unido a la /lista")
            command_Write_Users(m,users)
            command_Write_Players(m,players)
            print "New user add to list"
        else:
            bot.send_message(cid, "Uso: /add nombre")
    try:
        print ""
    except Exception:
        print "ERROR: add"
@bot.message_handler(commands=['donde'])
def command_addS(m):
    global place
    cid = m.chat.id
    try:
        message = m.text[7:50]
        if len(message) > 0:
            place = message
            bot.send_message(cid, "Has establecido un lugar")
        else:
            bot.send_message(cid, "Uso: /donde descripcion")
    except Exception:
        print "ERROR: donde"
def command_Write_Users(m, users):
    cid = m.chat.id
    try:
        # Open a file
        fo = open("users_"+str(cid)+".txt", "wb")
        for user in users:
            #print str(user[0])+"|"+str(user[1])
            #Write
            fo.write(str(user[0])+"_"+str(user[1])+"|")
        # Close opend file
        fo.close()
    except Exception:
        print "ERROR: write"
def command_Read_Users(m):
    users = []
    cid = m.chat.id
    i=0
    auxUserR = []
    try:
        # Open a file
        fo = open("users_"+str(cid)+".txt", "r+")
        string =fo.read()
        usersR = string.split("|")
        for userR in usersR:
            if i<50:
                auxUserR = userR.split("_")
                if auxUserR[0] != "":
                    users.append(auxUserR)
                i += 1
        # Close opend file
        fo.close()
        print "Users:\n"+str(users)
        return users
    except Exception:
        print "ERROR: read users"
        command_Write_Users(m, users)
        return users
def command_Write_Players(m, players):
    cid = m.chat.id
    # Open a file
    try:
        fo = open("players_"+str(cid)+".txt", "wb")
        for player in players:
            fo.write(str(player[0])+"_"+str(player[1])+"|")
        fo.close()
    except Exception:
        print "ERROR: write players"
def command_Read_Players(m):
    players = []
    cid = m.chat.id
    i = 0
    try:
        # Open a file
        fo = open("players_"+str(cid)+".txt", "r+")
        string =fo.read()
        playersR = string.split("|")
        for playerR in playersR:
            if i<50:
                auxPlayerR = playerR.split("_")
                if auxPlayerR[0] != "":
                    players.append(auxPlayerR)
                i += 1
        fo.close()
        print "Players:\n" + str(players)
        return players
    except Exception:
        print "ERROR: read players"
        command_Write_Players(m, players)
        return players
bot.polling()
