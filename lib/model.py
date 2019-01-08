from __future__ import division
from threading import Timer,Thread,Event

#---------------------------
#   Datamodels
#---------------------------
class Ship:
    def __init__(self,id=0l, name=""):
        self.id = id
        self.name = name


class Player:
    def __init__(self,id=0l,name=""):
        self.id = id
        self.name = name


class Stats:
    def __init__(self,battles=0l,frags=0l,damage_dealt=0l,wins=0l,hidden=False):
        self.hidden = hidden
        self.battles = battles
        self.frags = float(frags)
        self.damage = float(damage_dealt)
        self.wins = wins
        if(self.battles != 0):
            self.avgFrags = round(self.frags / battles,2) 
            self.avgDamage = round(self.damage / battles ,2)
            self.avgWins = round(float(self.wins / battles),4)*100

