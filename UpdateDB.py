# -*- encoding: utf-8 -*-
import json
import sys
import requests
import os
import sqlite3
import codecs

#   Classes
class ship:
    def __init__(self,id=0l, name=""):
        self.id = id
        self.name = name

#   Lists
nation = ["ussr","japan","germany","france","usa","pan_asia","italy","uk","commonwealth","poland"]
shipTpe = ["AirCarrier","Battleship","Cruiser","Destroyer"]
#   Vars
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), './Data/ships_db.sqlite3')
path = os.path.dirname(__file__)
configFile = "config.json"

#   Functions
def GetShipsByType(n,s):
    response = requests.get("https://api.worldofwarships.eu/wows/encyclopedia/ships/?application_id={id}&type={type}&fields=ship_id%2C+name&language=de&nation={nation}".format(type=s,nation=n,id=settings["appkey"]))
    if(response.status_code == 200):
        jArray = json.loads(response.content)
        for x in jArray["data"].items():
            newShip = ship(name=x[1]['name'],id=x[1]['ship_id'])
            AddShip(newShip)
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
    c.execute('CREATE TABLE Ships (id INTEGER, name TEXT);')
    con.commit()
    con.close()

def AddShip(newShip):
    try:
        con = db_connect()
        cursor = con.cursor()
        cursor.execute('INSERT INTO Ships VALUES (?,?)',(newShip.id,newShip.name,))
        con.commit()
        con.close()
    except Exception, e:
        print(e)

#   Main
try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file)
except:
    print("Could not find config file")

CreateDatabase()
for n in nation:
    for s in shipTpe:
        print("Adding {} from {} to Database".format(s,n))
        GetShipsByType(n,s)    

