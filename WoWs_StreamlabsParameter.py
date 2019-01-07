# ---------------------------
#   Import Libraries
# ---------------------------
from __future__ import division
import os
import sys
import json
import clr
import codecs
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references
import sqlite3
from model import Ship, Player, Stats

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "WoWs Stats Para"
Website = "https://github.com/De-Wohli/WoWs-Stats-Params"
Description = "Shows Stats for player ships"
Creator = "Fuyu_Kitsune & Sehales"
Version = "1.0.4"

configFile = "config.json"
SHIPS_DB = os.path.join(os.path.dirname(__file__), './Databases/ships_db.sqlite3')
regions = ["eu","ru","na","asia"]
langs = ["de","en"]

def Parse(parseString, userid, username, targetid, targetname, message):
    args = message.split(" ")
    if "$stats" in parseString:
        if settings["appkey"] == "":
            return parseString.replace("$stats","Please enter a Wargaming ApplicationID key to run this Script")
        elif message == "" or args[0].lower() == "help":
            return parseString.replace("$stats",settings["help_" + LANGUAGE].format(player=settings["streamer"],ship=settings["defaultShip"]))
        elif len(args) == 1 and args[0].lower() != "help":
            player = getPlayer(args[0])
            if player.id == 0:
                return parseString.replace("$stats",settings["unknown_player_" + LANGUAGE])
            else:
                stats = getPlayerStats(player)
                if stats.hidden:
                    return parseString.replace("$stats",settings["hidden_player_" + LANGUAGE])
                else:
                    url = getPlayerLink(player)
                    return parseString.replace("$stats",settings["stats_player_" + LANGUAGE].format(player=player.name, battles=stats.battles, avgDmg=stats.avgDamage,winrate=stats.avgWins, wgUrl=url))
        elif len(args) >= 2 and args[0].lower() != "help":
            player = getPlayer(args[0])
            if player.id == 0:
                return parseString.replace("$stats",settings["unknown_player_" + LANGUAGE])
            else:
                ship = getShip("_".join(args[1:]))
                stats = getShipStats(player,ship)
                if stats.hidden:
                    return parseString.replace("$stats",settings["hidden_player_" + LANGUAGE])
                elif ship.id == 0:
                    return parseString.replace("$stats",settings["unknown_ship_" + LANGUAGE])
                else:
                    url = getPlayerLink(player)
                    if stats.battles == 0:
                        return parseString.replace("$stats",settings["unknown_stats_" + LANGUAGE])
                    else:
                        return parseString.replace("$stats",settings["stats_ships_" + LANGUAGE].format(player=player.name, ship=ship.name, battles=stats.battles, avgDmg=stats.avgDamage,winrate=stats.avgWins, wgUrl=url))
        else:
            return parseString.replace("$stats","An Error occured")
    elif "$aStats" in parseString:
        if args[0].lower() == "region":
            if args[1].lower() in regions:
                settings["region"] = args[1]
                refreshSettings()
                return parseString.replace("$aStats","region changed to: " + args[1])
            else:
                return parseString.replace("$aStats","Invalid Region: " + args[1])
        elif args[0].lower() == "version":
            return parseString.replace("$aStats","Version: " + Version)
        elif args[0].lower() == "lang":
            if args[1].lower() in langs:
                settings["language"] = args[1]
                refreshSettings()
                return parseString.replace("$aStats","language changed to: " + args[1])
            else:
                return parseString.replace("$aStats","Invalid Language: " + args[1])
        else:
            return parseString.replace("$aStats","Invalid Parameters")
    return parseString

def Init(): 
    global settings, API_PLAYER_SHIP, API_PLAYER_SEARCH, API_PLAYER_STATS, PLAYER_BASE, LANGUAGE, path

    API_PLAYER_SEARCH="https://api.worldofwarships.$reg/wows/account/list/?application_id=$appkey"
    API_PLAYER_STATS="https://api.worldofwarships.$reg/wows/account/info/?application_id=$appkey&fields=statistics.pvp.battles%2Cstatistics.pvp.damage_dealt%2C+statistics.pvp.frags%2Cstatistics.pvp.wins"
    API_PLAYER_SHIP="https://api.worldofwarships.$reg/wows/ships/stats/?application_id=$appkey&fields=pvp.battles%2C+pvp.damage_dealt%2C+pvp.frags%2C+pvp.wins"
    PLAYER_BASE="https://worldofwarships.$reg/community/accounts/"
    path = os.path.dirname(__file__)

    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file)
    except Exception, e:
        settings = {
            "help_en": "Show Statistics: !stats Username Ship - z.B.: !stats {player} {ship} - Hint: Shipname is optional",
            "stats_player_en": "Statistics of {player} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
            "stats_ships_en": "Statistics of {player} for {ship} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
            "hidden_player_en": "This player refuses to participate in Statshaming",
            "unknown_player_en": "Player unknown",
            "unknown_ship_en": "Ship unknown",
            "unknown_stats_en": "No statistics available",
            "missing_permission_en": "No Permission",
            "cooldown_message_en": "Command is still on cooldown",
            "command": "!stats",
            "streamer": "Fuyu_Kitsune",
            "defaultShip": "Roma",
            "language": "en",
            "region": "eu",
            "showCurrentShipStats" : False
            }
        Parent.Log(ScriptName,"Error LoadConfig:" + str(e))

    settings["region"] = settings["region"].replace("na","com")
    API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$reg",settings["region"])
    API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$appkey",settings["appkey"])
    API_PLAYER_STATS = API_PLAYER_STATS.replace("$reg",settings["region"])
    API_PLAYER_STATS = API_PLAYER_STATS.replace("$appkey",settings["appkey"])
    API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$reg",settings["region"])
    API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$appkey",settings["appkey"])
    PLAYER_BASE = PLAYER_BASE.replace("$reg",settings["region"])
    LANGUAGE = settings["language"]

def ReloadSettings(jsonContent):
    Parent.Log(ScriptName, str(jsonContent))
    global settings, API_PLAYER_SHIP, API_PLAYER_SEARCH,API_PLAYER_STATS, PLAYER_BASE, LANGUAGE, path

    API_PLAYER_SEARCH="https://api.worldofwarships.$reg/wows/account/list/?application_id=$appkey"
    API_PLAYER_STATS="https://api.worldofwarships.$reg/wows/account/info/?application_id=$appkey&fields=statistics.pvp.battles%2Cstatistics.pvp.damage_dealt%2C+statistics.pvp.frags%2Cstatistics.pvp.wins"
    API_PLAYER_SHIP="https://api.worldofwarships.$reg/wows/ships/stats/?application_id=$appkey&fields=pvp.battles%2C+pvp.damage_dealt%2C+pvp.frags%2C+pvp.wins"
    PLAYER_BASE="https://worldofwarships.$reg/community/accounts/"
    path = os.path.dirname(__file__)

    try:
        settings = json.loads(jsonContent)
    except Exception, e:
        settings = {
            "help_en": "Show Statistics: !stats Username Ship - z.B.: !stats {player} {ship} - Hint: Shipname is optional",
            "stats_player_en": "Statistics of {player} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
            "stats_ships_en": "Statistics of {player} for {ship} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
            "hidden_player_en": "This player refuses to participate in Statshaming",
            "unknown_player_en": "Player unknown",
            "unknown_ship_en": "Ship unknown",
            "unknown_stats_en": "No statistics available",
            "missing_permission_en": "No Permission",
            "cooldown_message_en": "Command is still on cooldown",
            "command": "!stats",
            "streamer": "Fuyu_Kitsune",
            "defaultShip": "Roma",
            "language": "en",
            "region": "eu",
            "showCurrentShipStats" : False
            }
        Parent.Log(ScriptName,"Error LoadConfig:" + str(e))

    settings["region"] = settings["region"].replace("na","com")
    API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$reg",settings["region"])
    API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$appkey",settings["appkey"])
    API_PLAYER_STATS = API_PLAYER_STATS.replace("$reg",settings["region"])
    API_PLAYER_STATS = API_PLAYER_STATS.replace("$appkey",settings["appkey"])
    API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$reg",settings["region"])
    API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$appkey",settings["appkey"])
    PLAYER_BASE = PLAYER_BASE.replace("$reg",settings["region"])
    LANGUAGE = settings["language"]


def refreshSettings():
    global settings, API_PLAYER_SHIP, API_PLAYER_SEARCH,API_PLAYER_STATS, PLAYER_BASE, LANGUAGE, path

    try:
        API_PLAYER_SEARCH="https://api.worldofwarships.$reg/wows/account/list/?application_id=$appkey"
        API_PLAYER_STATS="https://api.worldofwarships.$reg/wows/account/info/?application_id=$appkey&fields=statistics.pvp.battles%2Cstatistics.pvp.damage_dealt%2C+statistics.pvp.frags%2Cstatistics.pvp.wins"
        API_PLAYER_SHIP="https://api.worldofwarships.$reg/wows/ships/stats/?application_id=$appkey&fields=pvp.battles%2C+pvp.damage_dealt%2C+pvp.frags%2C+pvp.wins"
        PLAYER_BASE="https://worldofwarships.$reg/community/accounts/"

        settings["region"] = settings["region"].replace("na","com")
        API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$reg",settings["region"])
        API_PLAYER_SEARCH = API_PLAYER_SEARCH.replace("$appkey",settings["appkey"])
        API_PLAYER_STATS = API_PLAYER_STATS.replace("$reg",settings["region"])
        API_PLAYER_STATS = API_PLAYER_STATS.replace("$appkey",settings["appkey"])
        API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$reg",settings["region"])
        API_PLAYER_SHIP = API_PLAYER_SHIP.replace("$appkey",settings["appkey"])
        PLAYER_BASE = PLAYER_BASE.replace("$reg",settings["region"])
        LANGUAGE = settings["language"]
        

        return
    except Exception, e :
        Parent.Log(ScriptName,"Error refreshSettings(): "+str(e))
        return

def OpenAPIPage():
    os.system("start https://developers.wargaming.net/applications/")
    return

def getPlayer(playerName):
    try:
        url = API_PLAYER_SEARCH + "&search=" + playerName
        response = Parent.GetRequest(url,{})
        content = json.loads(response)
        if(content["status"] == 200):
            content = json.loads(content["response"])
            if content["meta"]["count"] == 0:
                return Player()
            else:
                nick = content["data"][0]["nickname"]
                pid = content["data"][0]["account_id"]
                newPlayer = Player(name = nick, id = pid)
                return newPlayer
    
    except Exception, e:
        Parent.Log(ScriptName,"EXCEPTION GetPlayer(): "+str(e))
        return Player()

def getPlayerLink(player):
    link = str.format("{}{}-{}",PLAYER_BASE,player.id,player.name)
    return link

def db_connect(db_path=SHIPS_DB):  
    con = sqlite3.connect(db_path)
    con.text_factory = str
    return con

def getPlayerStats(player):
    try:
        url = API_PLAYER_STATS + "&account_id=" + str(player.id)
        response = Parent.GetRequest(url,{})
        content = json.loads(response)
        if(content["status"] == 200):
            content = json.loads(content["response"])
            if bool(content["data"]):
                if bool(content["meta"]["hidden"]):
                    st = Stats(1,1,1,1,True)
                else:
                    battles = content["data"][str(player.id)]["statistics"]['pvp']['battles']
                    wins = content["data"][str(player.id)]["statistics"]['pvp']['wins']
                    frags = content["data"][str(player.id)]["statistics"]['pvp']['frags']
                    damage_dealt= content["data"][str(player.id)]["statistics"]['pvp']['damage_dealt']
                    st = Stats(battles,frags,damage_dealt,wins)
            else:
                return Stats()
            return st
    except Exception, e:
        Parent.Log(ScriptName,"Error getPlayerStats(player): " + str(e))
        return Stats()

def getShip(name):
    try:
        con = db_connect()
        cursor = con.cursor()
        cursor.execute('SELECT id,Name FROM ships WHERE name LIKE ?',(name,))
        rows = cursor.fetchone()
        if rows is None:
            return Ship()
        else:
            return Ship(id=rows[0],name=rows[1])
    except Exception, e:
        Parent.Log(ScriptName,"Error getShip: " + str(e))
        return Ship()

def getShipStats(p,s):
    try:
        url= API_PLAYER_SHIP + "&account_id=" + str(p.id) + "&ship_id=" + str(s.id)
        response = Parent.GetRequest(url,{})
        content = json.loads(response)
        if(content["status"] == 200):
            content = json.loads(content["response"])
            if bool(content["meta"]["hidden"]):
                st = Stats(1,1,1,1,True)
            elif bool(content["data"]) and not content["data"][str(p.id)] == None :
                battles = content["data"][str(p.id)][0]['pvp']['battles']
                wins = content["data"][str(p.id)][0]['pvp']['wins']
                frags = content["data"][str(p.id)][0]['pvp']['frags']
                damage_dealt= content["data"][str(p.id)][0]['pvp']['damage_dealt']
                st = Stats(battles,frags,damage_dealt,wins)
            else:
                return Stats()
            return st
    except Exception, e:
        Parent.Log(ScriptName,"Error getShipStats: " + str(e))
        return Stats()