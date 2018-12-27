# Erste schritte
- Besorgt euch eine API Application ID von Wargaming und fügt diese dem script hinzu, dafür einfach die ID in das Textfeld kopieren.
- Region und Sprache wählen
- Default ship eintragen
- Ingamename des Streamers eintragen
- Speichern und Script neu laden
- Einen neuen command erstellen, im response muss `$stats`

optional:
- Erstelle neuen command für administrative funktionen
- berechtigungen einstellen
- im command muss `$aStats` stehen

Verfügbare Administrative befehle:

`!command lang [en || de]`

`!command region [eu || na || asia || ru]`
# WoWs-Stats
Script für den Streamlabs Chatbot zum anzeigen von World of Warships Statistiken. Die statistiken werden im Twitchchat vom Chatbot wiedergegeben.
 `Statistik von [spieler] für [schiff] --- Gefechte: || Durchschn. Schaden: || Winrate --- Statuspage: [link zum Offiziellen Profil]`
 # Commands
!stats [nutzername] [Schiffsname]
 `!stats Fuyu_Kitsune Roma` Zum anzeigen der Schiffsstatistiken für den Spieler Fuyu_Kitsune
 `!stats Fuyu_Kitsune` Zum anzeigen der allgemeinen Statistiken für den Spieler Fuyu_Kitsune
 # Config Datei
 Neue sprachen können hinzugefügt werden indem die JSON datei erweitert wird um z.B.:
 `"stats_player_nl" : "statistieken van {} --- gevechten: {} ... etc"`
 anschließend die sprache `language` auf `nl` setzen. Wichtig die datei muss als `UTF-8 with BOM` gespeichert werden, ich empfehle Notepad++ oder VS-Code zum bearbeiten der Datei.
 # Command
 Einfach die command datei über den Commandreiter importieren und anschließend wie gewohnt editieren.
 Alternativ über den Command tab einen neuen command erstellen. Wichtig ist das im response `$stats` steht damit das script die antwort einfügen kann


# Kontakt
Für fragen, anregungen oder kritik, schau einfach in meinem Discord channel vorbei https://discord.gg/RWDpTzK
