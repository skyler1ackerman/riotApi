# Riot API Dataclass

## Purpose
I wanted to know in depth statistics about my time playing one of my favorite games, League of Legends, so I started on this project. You can find out your own stats as well as long as you know your username.

## Usage
First, you'll need to get a Riot Api token. Then, you can use the api_getter file to download all the information you need. Origonally I had it stored as a json file for human readability, but it loads much quicker as a pickle file. Once the data is downloaded, you can load it in using the dataMan_class file. I recommend doing this in VSCODE cells, because the data takes quite some time to load at first. After, you will have access to a variety of functions such as averge of a stat, max of a stat, most champions played, most games player with other players, sorting by champ, mode, lane and role, and a variety of graphs. This is still a work in progress, so it's not perfect, and a lot was transferred over from my origonal code, which was purely functional. 

The class structure can be seen in the riotClass file. 