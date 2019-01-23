from pynput.keyboard import Key, Controller
import time
import sys

keyboard = Controller()

testcases = [
                "!stats",
                "!stats Fuyu_Kitsune",
                "!stats Fuyu_Kitsune Roma",
                "!stats Fuyuuuuuu",
                "!stats Fuyu_Kitsune Romaaaaaaa",
                "!stats Fuyu_Kitsune Großer Kurfürst",
                "!stats Fuyu_Kitsune Grosser Kurfurst",
                "!stats Fuyu_Kitsune jurien de la graviere",
                "!stats SaS_leader"
            ]
stress= [
    "ARP Ashigara",
    "ARP Haguro",
    "ARP Haruna",
    "ARP Hiei",
    "ARP Kirishima",
    "ARP Kongō",
    "ARP Myoko",
    "ARP Nachi",
    "ARP Takao",
	"Acasta",
	"Admiral Graf Spee",
	"Admiral Hipper",
	"Admiral Makarov",
	"Aigle",
	"Akatsuki",
	"Akizuki",
	"Alabama",
	"Alabama ST",
	"Alaska",
	"Albany",
	"Algérie",
	"Alsace",
	"Amagi",
	"Anshan",
	"Aoba",
	"Arizona",
	"Arkansas Beta",
	"Asashio",
	"Asashio B",
	"Ashitaka",
	"Atago",
	"Atago B",
	"Atlanta",
	"Aurora",
	"Azuma",
	"Baltimore",
	"Bayern",
	"Belfast",
	"Bellerophon",
	"Benson",
	"Bismarck",
	"Black",
	"Black Swan",
	"Bogatyr",
	"Bogue",
	"Boise",
	"Bougainville",
	"Bourgogne",
	"Brennus",
	"Bretagne",
    "Budionny",
	"Budjonny",
	"Budyonny",
	"Buffalo",
	"Błyskawica",
	"Caledon",
	"Campbeltown",
	"Chabarowsk",
	"Chapayev",
	"Charles Martel",
	"Charleston",
	"Chengan",
	"Chester",
	"Chikuma",
	"Chung Mu",
	"Clemson",
	"Cleveland",
	"Colorado",
	"Conqueror",
	"Cossack",
	"Courbet"
    ]

def normaltest():
    for x in testcases:
        keyboard.type(x)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(3)

def stresstest():
    for x in stress:
        keyboard.type("!stats Fuyu_Kitsune " + x)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

for x in range(5):
    time.sleep(1)
    sys.stdout.write(".")
sys.stdout.write("\n")
sys.stdout.flush()

# stresstest()
normaltest()