# -*- encoding: utf-8 -*-
import json
import sys
import requests
import os
import sqlite3
import codecs
import time

#   Classes
class Ship:
    def __init__(self,id=0l, name=""):
        self.id = id
        self.name = name
    def __eq__(self, other):
        return self.name == other


#   Vars
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), '../Data/ships_db.sqlite3')
path = os.path.dirname(__file__)
ships = []
apikey=""


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


def db_connect(db_path=DEFAULT_PATH):  
    con = sqlite3.connect(db_path)
    con.text_factory = str
    return con


def CreateDatabase():
    if os.path.isfile(DEFAULT_PATH):
        os.remove(DEFAULT_PATH)
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
        except Exception, e:
            print("Error: "+str(e))
            pass
        con.close()
    except Exception, e:
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
        with codecs.open(dataFile, encoding="utf-8", mode="r") as f:
            tmp = json.load(f, encoding="utf-8")
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
            cooldown(2)
        cooldown(3)
    for s in ships:
        print(u"Adding {} to Database".format(s.name))
        AddShip(s)

if __name__== "__main__":
    main()


