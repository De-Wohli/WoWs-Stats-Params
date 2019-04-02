from __future__ import division

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
        
    @property
    def avgFrags(self):
       if self.battles > 0:
           return round(self.frags / self.battles,2)
    @property
    def avgDamage(self):
        if self.battles > 0:
            return round(self.damage / self.battles,2)
    @property
    def avgWins(self):
        if self.battles > 0:
            return round(float(self.wins / self.battles),4) * 100