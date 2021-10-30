# -*- encoding: utf-8 -*-
import json
from posixpath import pardir
import sys
import requests
import os
import sqlite3
import codecs
import time
from pathlib import Path

#   Classes
class Ship:
    def __init__(self,id=0, name=""):
        self.id = id
        self.name = name
    def __eq__(self, other):
        return self.name == other


#   Vars
UPDATEDB_PATH = Path(os.path.dirname(__file__))
TOOLS_PATH = UPDATEDB_PATH.parent.absolute()
BASE_PATH = TOOLS_PATH.parent.absolute()
DATA_PATH = os.path.join(str(BASE_PATH), 'Data')
DB_PATH = os.path.join(str(DATA_PATH), 'ships_db.sqlite3')
settingsFile = os.path.join(str(DATA_PATH), "settings.json")
ships = []
apikey = ""
with open(settingsFile) as f:
    data = f.read()
    data = json.loads(data)
    apikey = data["appkey"]

#   Functions
def GetShipsByType(n,s,lang):
    response = requests.get("https://api.worldofwarships.eu/wows/encyclopedia/ships/?application_id={id}&type={type}&fields=ship_id%2C+name&language={lang}&nation={nation}".format(type = s,nation = n,id = apikey,lang = lang))
    if(response.status_code == 200):
        jArray = json.loads(response.content)
        for x in jArray["data"].items():
            if x[1]['name'] not in ships:
                ships.append(Ship(name=x[1]['name'],id=x[1]['ship_id']))
                sys.stdout.write(".")
                sys.stdout.flush()        
    sys.stdout.write("\n")
    sys.stdout.flush()


def db_connect(db_path=DB_PATH):  
    con = sqlite3.connect(db_path)
    con.text_factory = str
    return con


def CreateDatabase():
    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)
    con=db_connect()
    c = con.cursor()
    c.execute('CREATE TABLE Ships (id INTEGER, name TEXT UNIQUE);')
    con.commit()
    con.close()


def AddShip(newShip):
    try:
        con = db_connect()
        cursor = con.cursor()
        try:
            cursor.execute('INSERT INTO Ships VALUES (?,?);',(newShip.id,newShip.name))
            con.commit()
        except Exception as e:
            print("Error: "+str(e))
            pass
        con.close()
    except Exception as e:
        print(e)


def cooldown(seconds):
    sys.stdout.write("cooldown")
    for x in range(seconds):
        time.sleep(1)
        sys.stdout.write(".")
    sys.stdout.write("\n")
    sys.stdout.flush()

def main():
    tmp = {}
    toolFolder = os.path.join(os.path.dirname(__file__))
    dataFile = os.path.join(toolFolder,"UpdateDbData.json")
    try:
        with open(dataFile,mode="r") as f:
            tmp = json.load(f)
    except:
        print("error")
        sys.exit(1)

    langs = tmp["langs"]
    nation = tmp["nations"]
    shipTpe = tmp["types"]

    CreateDatabase()

    for l in langs:   
        print("Getting Ships in Language: "+l)
        for n in nation:
            for s in shipTpe:
                print("Getting {} from {} ".format(s,n))
                GetShipsByType(n,s,l)
                time.sleep(0.5)
            cooldown(5)
        cooldown(10)
    for s in ships:
        print(u"Adding {} to Database".format(s.name))
        AddShip(s)

if __name__== "__main__":
    main()


