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
Version = "1.0.6"


dataFolder = os.path.join(os.path.dirname(__file__), "data/")
settingsFile = os.path.join(dataFolder, "settings.json")
apiFile = os.path.join(dataFolder, "api.json")
textFile = os.path.join(dataFolder, "texts.json")
shipsDb= os.path.join(dataFolder,"ships_db.sqlite3")
regions = ["eu","ru","na","asia"]
langs = ["de","en"]

class Settings(object):
    def __init__(self, settingsfile=None):
        """ Load saved settings from file if available otherwise set default values. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8-sig")
        except:
                self.streamer = "Fuyu_Kitsune"
                self.defaultShip = "Roma"
                self.language = "de"
                self.region = "eu"
                self.appkey = ""
    
    def reload(self, jsondata):
        """ Reload settings from AnkhBot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")


class API(object):
    def __init__(self,apifile=None):
        try:
            with codecs.open(apifile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8-sig")
        except:
                self.PLAYER_SEARCH = "https://api.worldofwarships.{reg}/wows/account/list/?application_id={appkey}",
                self.PLAYER_STATS = "https://api.worldofwarships.{reg}/wows/account/info/?application_id={appkey}&fields=statistics.pvp.battles%2Cstatistics.pvp.damage_dealt%2C+statistics.pvp.frags%2Cstatistics.pvp.wins"
                self.PLAYER_SHIP = "https://api.worldofwarships.{reg}/wows/ships/stats/?application_id={appkey}&fields=pvp.battles%2C+pvp.damage_dealt%2C+pvp.frags%2C+pvp.wins"
                self.PLAYER_LINK = "https://worldofwarships.{reg}/community/accounts/"

class Texts(object):
    def __init__(self,textfile=None,language="en"):
        try:
            with codecs.open(textfile, encoding="utf-8-sig", mode="r") as f:
                tmp = json.load(f, encoding="utf-8-sig")
        except:
            tmp =   {
                "en":
                {
                    "help": "Show Statistics: !stats [Username] [Ship] - z.B.: !stats {player} {ship} - Hint: Shipname is optional",
                    "stats_player": "Statistics of {player} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
                    "stats_ships": "Statistics of {player} for {ship} --- Battles: {battles} || Average Damage: {avgDmg} || Winrate: {winrate}% --- Statuspage: {wgUrl}",
                    "hidden_player": "This player refuses to participate in Statshaming",
                    "unknown_player": "Player unknown",
                    "unknown_ship": "Ship unknown",
                    "unknown_stats": "No statistics available"
                }
            }
        self.__dict__ = tmp[language]


def Init():
    global settings
    settings = Settings(settingsFile)
    global api
    api = API(apiFile)
    global texts
    texts = Texts(textFile,settings.language)

def ReloadSettings(jsonContent):
    global settings
    settings.reload(jsonContent)
    global api
    api = API(apiFile)
    global texts
    texts = Texts(textFile,settings.language)
    Parent.Log(ScriptName,"Config Reloaded")

def Parse(parseString, userid, username, targetid, targetname, message):
    args = message.split(" ")
    if "$stats" in parseString:
        if settings.appkey == "":
            return parseString.replace("$stats","Please enter a Wargaming ApplicationID key to run this Script")
        elif message == "" or args[0].lower() == "help":
            retStr = str(texts.help)
            return parseString.replace("$stats",retStr.format(player=settings.streamer,ship=settings.defaultShip))
        elif len(args) == 1 and args[0].lower() != "help":
            player = getPlayer(args[0])
            if player.id == 0:
                retStr = str(texts.unknown_player)
                return parseString.replace("$stats",retStr)
            else:
                stats = getPlayerStats(player)
                if stats.hidden:
                    retStr = str(texts.hidden_player)
                    return parseString.replace("$stats",retStr)
                elif stats.damage == 0:
                    retStr = str(texts.unknown_stats)
                    return parseString.replace("$stats",retStr)
                else:
                    url = getPlayerLink(player)
                    retStr = str(texts.stats_player)
                    return parseString.replace("$stats",retStr.format(player=player.name, battles=stats.battles, avgDmg=stats.avgDamage,winrate=stats.avgWins, wgUrl=url))
        elif len(args) >= 2 and args[0].lower() != "help":
            player = getPlayer(args[0])
            if player.id == 0:
                retStr = str(texts.unknown_player)
                return parseString.replace("$stats",retStr)
            else:
                ship = getShip("_".join(args[1:]))
                stats = getShipStats(player,ship)
                if stats.hidden:
                    retStr = str(texts.hidden_player)
                    return parseString.replace("$stats",retStr)
                elif ship.id == 0:
                    retStr = str(texts.unknown_ship)
                    return parseString.replace("$stats",retStr)
                elif stats.damage == 0:
                    retStr = str(texts.unknown_stats)
                    return parseString.replace("$stats",retStr)
                else:
                    url = getPlayerLink(player)
                    if stats.battles == 0:
                        retStr = str(texts.unknown_stats)
                        return parseString.replace("$stats",retStr)
                    else:
                        retStr = str(texts.stats_ships)
                        return parseString.replace("$stats",retStr.format(player=player.name, ship=ship.name, battles=stats.battles, avgDmg=stats.avgDamage,winrate=stats.avgWins, wgUrl=url))
        else:
            return parseString.replace("$stats","An Error occured")
    elif "$aStats" in parseString:
        if args[0].lower() == "region":
            if args[1].lower() in regions:
                settings.region = args[1]
                return parseString.replace("$aStats","region changed to: " + args[1])
            else:
                return parseString.replace("$aStats","Invalid Region: " + args[1])
        elif args[0].lower() == "version":
            return parseString.replace("$aStats","Version: " + Version)
        elif args[0].lower() == "lang":
            if args[1].lower() in langs:
                settings.language = args[1]
                global texts
                texts = Texts(textFile,settings.language)
                return parseString.replace("$aStats","language changed to: " + args[1])
            else:
                return parseString.replace("$aStats","Invalid Language: " + args[1])
        else:
            return parseString.replace("$aStats","Invalid Parameters")
    return parseString

def OpenAPIPage():
    os.system("start https://developers.wargaming.net/applications/")
    return

def getPlayer(playerName):
    try:
        url = api.PLAYER_SEARCH
        url = str(url).format(reg=settings.region,appkey=settings.appkey,playerName=playerName)
        response = Parent.GetRequest(url,{})
        content = json.loads(response)
        if(content["status"] == 200):
            content = json.loads(content["response"])
            if content["meta"]["count"] == 0:
                return Player()
            if content ["data"][0]["nickname"].lower() != playerName.lower():
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
    link = str.format("{}{}-{}",str(api.PLAYER_LINK).format(reg=settings.region),player.id,player.name)
    return link

def db_connect(db_path=shipsDb):
    con = sqlite3.connect(db_path)
    con.text_factory = str
    return con

def getPlayerStats(player):
    try:
        url = api.PLAYER_STATS
        url = str(url).format(reg=settings.region,appkey=settings.appkey,accountID=player.id)
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
        url = api.PLAYER_SHIP
        url= str(url).format(reg=settings.region,appkey=settings.appkey,accountID=p.id,shipID=s.id)
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