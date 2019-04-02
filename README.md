# Setup
- Download the Zip and import it into Streamlabs Chatbot from the scripts tab.

### Update
- Extract the Update.zip into the WoWs-Stats folder inside your Streamlabs Chatbot scripts folder.

### API IDs
- Visit the wargaming website https://developers.wargaming.net/applications/ and register an application to recieve Application ID.
- Copy the Application ID from the website and paste it into the config in Streamlabs Chatbot.

### Region and Language
- Go to the configuration of the script inside Streamlabs Chatbot.
- Choose a Language and the Region you want to recieve the stats from.
- Enter a Default ship that is shown in the helptext.
- Enter a Playername that is shown in the helptext.

### Commands
- Go to the Commands tab inside Streamlabs Chatbot.
- Create a new command (`!stats` recommended).
- Enter `$stats` inside the response textfield. If you want the answers to be whispered use `/w $user $stats`
- Create another command for administrative commands (`!aStats` recommended).
- Enter `$aStats` inside the response textfield.
- Create another command for Ranked stats (`!rstats` recommended).
- Enter `$rstats` inside the response textfield. If you want the answers to be whispered use `/w $user $stats`

# General

### Supported Commands
- Administrative: `!command lang [en || de]` to set the language via command.
- Administrative: `!command region [eu || na || asia || ru]` to set the region via command.
- Administrative: `!command version` to show the currently running version.
- General: `!command` to show helptext.
- General: `!command help` to show helptext.
- General `!command [player]` to show player stats.
- General: `!command [player] [ship]` to show players stats for specified ship.
- Ranked: `!command [season] [player]` to show player stats for specified season (integers for normal seasons, `s`+ sprint for sprints (i.e. `s4`))
- Ranked: `!command [season] [player] [ship]` to show player stats for specified ship and season (integers for normal seasons, `s`+ sprint for sprints (i.e. `s4`))


### Supported Languages
- German
- English
- Polish
- French
- Turkish

If you'd like to add a translation, please contact me on the discord server https://discord.gg/feMnm5B to recieve instructions for translation works.

# Contact
For requests, support and ideas please visit https://discord.gg/feMnm5B

If you'd like to support this project, feel free to leave donation via https://paypal.me/Fuyune
