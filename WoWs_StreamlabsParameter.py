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
import re
from model import Ship, Player, Stats


# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "WoWs Stats"
Website = "https://github.com/De-Wohli/WoWs-Stats-Params"
Description = "Shows Stats for player ships"
Creator = "Fuyu_Kitsune & Sehales"
Version = "2.1.5"

# ---------------------------
#  Global Vars
# ---------------------------

dataFolder = os.path.join(os.path.dirname(__file__), "data/")
settingsFile = os.path.join(dataFolder, "settings.json")
apiFile = os.path.join(dataFolder, "api.json")
textFile = os.path.join(dataFolder, "texts.json")
asnFile = os.path.join(dataFolder,"asn.json")
shipsDb= os.path.join(dataFolder,"ships_db.sqlite3")
regions = ["eu","ru","na","asia"]
langs = ["de","en","pl","fr","tr"]

# ---------------------------
#  Class Definitions
# ---------------------------

class Settings(object):
    def __init__(self, settingsfile=None):
        """ Load saved settings from file if available otherwise set default values. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8-sig")
        except Exception,e:
                self.streamer = "Fuyu_Kitsune"
                self.defaultShip = "Roma"
                self.language = "de"
                self.region = "eu"
                self.appkey = ""
                Parent.Log(ScriptName,"Settings: "+str(e))
    
    def reload(self, jsondata):
        """ Reload settings from AnkhBot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")


class API(object):
    def __init__(self,apifile=None):
        try:
            with codecs.open(apifile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8-sig")
        except Exception,e:
                self.PLAYER_SEARCH = "https://api.worldofwarships.{reg}/wows/account/list/?application_id={appkey}",
                self.PLAYER_STATS = "https://api.worldofwarships.{reg}/wows/account/info/?application_id={appkey}&fields=statistics.pvp.battles%2Cstatistics.pvp.damage_dealt%2C+statistics.pvp.frags%2Cstatistics.pvp.wins"
                self.PLAYER_SHIP = "https://api.worldofwarships.{reg}/wows/ships/stats/?application_id={appkey}&fields=pvp.battles%2C+pvp.damage_dealt%2C+pvp.frags%2C+pvp.wins"
                self.PLAYER_LINK = "https://worldofwarships.{reg}/community/accounts/"
                Parent.Log(ScriptName,"APIs: "+str(e))


class Texts(object):
    def __init__(self,textfile=None,language="en"):
        try:
            with codecs.open(textfile, encoding="utf-8-sig", mode="r") as f:
                tmp = json.load(f, encoding="utf-8-sig")
        except Exception,e:
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
            Parent.Log(ScriptName,"Texts: "+str(e))
        self.__dict__ = tmp[language]

# ---------------------------
#  StreamLabs functions
# ---------------------------

def Init():
    try:
        global asn, settings, api, texts
        settings = Settings(settingsFile)
        api = API(apiFile)
        texts = Texts(textFile,settings.language)
        asn = loadAsn()
    except Exception,e:
        Parent.Log(ScriptName,"Fatal, init failed: "+str(e))


def loadAsn():
    try:
        with codecs.open(asnFile, encoding="utf-8-sig", mode="r") as f:
            return json.load(f, encoding="utf-8-sig")
    except Exception,e:
        Parent.Log(ScriptName,"Failed to load Asn: "+str(e))
        pass


def ReloadSettings(jsonContent):
    try:
        settings.reload(jsonContent)
        api = API(apiFile)
        texts = Texts(textFile,settings.language)
        Parent.Log(ScriptName,"Config Reloaded")
    except Exception,e:
        Parent.Log(ScriptName,"Fatal, reload failed: "+str(e))


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
                ship = getShip(" ".join(args[1:]))
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
    elif "$rstats" in parseString:
        regex = re.compile(r'(^[1][0-1]$){1}|(^[1-9]$){1}|(^s[1-4]$){1}',re.IGNORECASE) # regex to check for valid season
        Parent.Log("regex",str(len(regex.findall(args[0]))))
        if settings.appkey == "":
            return parseString.replace("$rstats","Please enter a Wargaming ApplicationID key to run this Script")
        elif len(regex.findall(args[0])) == 0:
            retStr = "Please enter a Valid season identifier: i.e [!rstats 11 {player}] for season 11 or [!rstats s4 {player}] for sprint 4".format(player=settings.streamer)
            return parseString.replace("$rstats",retStr)
        elif len(args) < 2:
            retStr = "Please enter a request: i.e [!rstats 11 {player}] for season 11 or [!rstats s4 {player}] for sprint 4".format(player=settings.streamer)
            return parseString.replace("$rstats",retStr)
        elif len(args) == 2 and args[0] != "help":
            season = convertSeason(args[0])
            playerObject = getPlayer(args[1])
            if playerObject.id == 0:
                retStr = str(texts.unknown_player)
                return parseString.replace("$rstats",retStr)
            else:
                playerStats = getRankedStats(playerObject,season)
                if playerStats is None or playerStats.damage == 0:
                    retStr = str(texts.unknown_stats)
                    return parseString.replace("$rstats",retStr)
                elif playerStats.hidden:
                    retStr = str(texts.hidden_player)
                    return parseString.replace("$rstats",retStr)
                else:
                    url = getPlayerLink(playerObject)
                    retStr = str(texts.stats_player)
                    return parseString.replace("$rstats",retStr.format(player=playerObject.name, battles=playerStats.battles, avgDmg=playerStats.avgDamage,winrate=playerStats.avgWins, wgUrl=url))
        elif len(args) > 2:
            season = convertSeason(args[0])
            playerObject = getPlayer(args[1])
            if playerObject.id == 0:
                retStr = str(texts.unknown_player)
                return parseString.replace("$rstats",retStr)
            else:
                ship = getShip(" ".join(args[2:]))
                if ship.id == 0:
                    retStr = str(texts.unknown_ship)
                    return parseString.replace("$rstats",retStr)
                else:
                    shipStats = getRankedStats(playerObject,season,ship)
                    if shipStats.hidden:
                        retStr = str(texts.hidden_player)
                        return parseString.replace("$rstats",retStr)
                    elif shipStats.damage == 0:
                        retStr = str(texts.unknown_stats)
                        return parseString.replace("$rstats",retStr)
                    else:
                        url = getPlayerLink(playerObject)
                        retStr = str(texts.stats_ships)
                        return parseString.replace("$rstats",retStr.format(player=playerObject.name, ship=ship.name, battles=shipStats.battles, avgDmg=shipStats.avgDamage,winrate=shipStats.avgWins, wgUrl=url))
    return parseString

# ---------------------------
#  Helper Functions
# ---------------------------

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
        else:
            Parent.Log(ScriptName,content["message"])
    except Exception, e:
        Parent.Log(ScriptName,"EXCEPTION GetPlayer(): "+str(e))
        return Player()


def getPlayerLink(player):
    link = str.format("{}{}-{}",str(api.PLAYER_LINK).format(reg=settings.region),player.id,player.name)
    return link


def db_connect(db_path=shipsDb):
    try:
        con = sqlite3.connect(db_path)
        con.text_factory = str
        return con
    except Exception,e:
        Parent.Log(ScriptName,"db_connect failed: "+str(e))


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
        else:
            Parent.Log(ScriptName,content["message"])
    except Exception, e:
        Parent.Log(ScriptName,"Error getPlayerStats(player): " + str(e))
        return Stats()


def getShip(name):
    try:
        con = db_connect()
        cursor = con.cursor()
        if asn.get(name.lower(),None) != None:
            cursor.execute('SELECT id,Name FROM ships WHERE id LIKE ?',(asn[name.lower()],))
        else:
            cursor.execute('SELECT id,Name FROM ships WHERE name = ? COLLATE NOCASE',(name,))
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
        else:
            Parent.Log(ScriptName,content["message"])
    except Exception, e:
        Parent.Log(ScriptName,"Error getShipStats: " + str(e))
        return Stats()


def getRankedStats(player,season,ship = None):
    try:
        if ship is not None:
            url = api.R_SHIP_STATS.format(reg=settings.region,wgapi=settings.appkey,accountID=player.id,shipID = ship.id)
        else:
            url = api.R_PLAYER_STATS.format(reg=settings.region,wgapi=settings.appkey,accountID=player.id)
        response = Parent.GetRequest(url,{})
        content = json.loads(response)
        stats = Stats()
        if(content["status"] == 200):
            content = json.loads(content["response"])
            if bool(content["meta"]["hidden"]):
                stats = Stats(1,1,1,1,True,200)
            elif bool(content["data"]) and not content["data"][str(player.id)] == None :
                if ship is not None:
                    seasons = content["data"][str(player.id)][0]["seasons"]
                    if season in seasons:
                        currentSeason = content["data"][str(player.id)][0]["seasons"][season]
                    else:
                        return None
                else:
                    seasons = content["data"][str(player.id)]["seasons"]
                    if season in seasons:
                        currentSeason = content["data"][str(player.id)]["seasons"][season]
                    else:
                        return None
                r = []
                r.append(currentSeason["rank_solo"])
                r.append(currentSeason["rank_div2"])
                r.append(currentSeason["rank_div3"])
                for x in r:
                    if x is not None:
                        stats.wins += x["wins"]
                        stats.damage += x["damage_dealt"]
                        stats.battles += x["battles"]
                        stats.frags += x["frags"]
            else:
                return None
            return stats
        else:
            return None
        pass
    except Exception, e:
        Parent.Log(ScriptName,"Error getRankedStats: "+str(e))
        pass


def convertSeason(value):
    season = value
    if season == "s1":
        season = "101"
    elif season == "s2":
        season = "102"
    elif season == "s3":
        season = "103"
    elif season == "s4":
        season = "104"
    return season