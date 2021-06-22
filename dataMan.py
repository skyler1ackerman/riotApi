import json, datetime, pprint
from config import TOKEN, ID
from riotwatcher import LolWatcher, ApiError
import matplotlib.pyplot as plt
import numpy as np
pp = pprint.PrettyPrinter(indent=4)

my_region = 'na1'

watcher = LolWatcher(TOKEN)
latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']

def getItemsNames():
	static_item_list = watcher.data_dragon.items(latest, False)
	item_dict = dict()
	for key in static_item_list['data']:
		item_dict[key] = static_item_list['data'][key]['name']
	return item_dict

def getItemName(id_):
	if 'item_dict' not in globals():
		global item_dict # TODO: Change this to be from file
		item_dict = getItemsNames()
	return item_dict[str(id_)]

def removeDup():
	temp = []
	res = dict()
	newData = []
	for match in data:
	    if match['gameId'] not in temp:
	        temp.append(match['gameId'])
	        newData.append(match)
	     
	return newData

def getChampNames(static_list):
	static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
	champ_dict = dict()
	for key in static_champ_list['data']:
	    row = static_champ_list['data'][key]
	    champ_dict[row['key']] = row['id']
	return champ_dict

def getChampName(id_):
	if 'champ_dict' not in globals():
		global champ_dict # TODO: Change this to be from file
		champ_dict = getNames()
	return champ_dict[str(id_)]

def loadData(file):
	with open(file, "r") as f: 
		return json.load(f)

def maxStat(stat, mode=None):
	cur_max = -1000000000
	id_=500
	for match in data:
		# Figure out which player is the user
		if mode and match['gameMode']!=mode:
			continue
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		# Get the current match
		cur = match['participants'][id_-1]['stats'][stat]
		# Check if it's the max
		if cur > cur_max:
			cur_max = cur
	return cur_max

def sumstat(stat, mode=None):
	total = 0
	id_=500
	for match in data:
		# Figure out which player is the user
		if mode and match['gameMode']!=mode:
			continue
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		# Sum the total of that stat
		try:
			total+=match['participants'][id_-1]['stats'][stat]
		except KeyError:
			pass

	return total

def avgStat(stat, mode=None):
	return sumstat(stat, mode=None)/len(data)

def sumTeamStat(stat, mode=None):
	total = 0
	id_=500
	for match in data:
		if mode and match['gameMode']!=mode:
			continue
		# Figure out which player is the user
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		# Figure out which team the player is on
		team = match['participants'][id_-1]['teamId']
		# Team is either 100 or 200, so we can do this
		total+=match['teams'][(team//100)-1][stat]
	return total

def sumOtherTeamStat(stat, mode=None):
	total = 0
	id_=500
	for match in data:
		if mode and match['gameMode']!=mode:
			continue
		# Figure out which player is the user
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		# Figure out which team the player is on
		team = match['participants'][id_-1]['teamId']
		# Team is either 100 or 200, so we can do this
		total+=match['teams'][1-((team//100)-1)][stat]
	return total

def sumTime(mode=None):
	total = 0
	id_=500
	for match in data:
		if mode and match['gameMode']!=mode:
			continue
		total+=match['gameDuration']
	return total

def maxTime(mode=None):
	total = 0
	cur_max = -1
	for match in data:
		if mode and match['gameMode']!=mode:
			continue
		cur = match['gameDuration']
		if cur > cur_max:
			cur_max = cur
	return cur_max

def getStatList(stat, mode=None):
	ret_list = []
	id_=500
	for match in data:
		# Figure out which player is the user
		if mode and match['gameMode']!=mode:
			continue
		# Get the participant
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		# Get the current match
		try:
			ret_list.append(match['participants'][id_-1]['stats'][stat])
		except KeyError:
			pass

	return ret_list

def plotHist(stat, mode=None, bins=None, save=False, show=True):
	# Get the stats list
	stat_list = getStatList(stat, mode=None)
	# Get color map
	cm = plt.cm.get_cmap('plasma')
	# Make the histogram
	range_ = max(stat_list)-min(stat_list)
	if bins == None:
		bins = range_
	try:
		bin_range = np.arange(min(stat_list), max(stat_list), (range_)//bins)-.5
	except ZeroDivisionError:
		print('Too many bins!')
	n, bins_, patches = plt.hist(stat_list, bins=bin_range)
	# Change the color
	bin_centers = 0.5 * (bins_[:-1] + bins_[1:])
	col = bin_centers - min(bin_centers)
	col /= max(col)
	for c, p in zip(col, patches):
	    plt.setp(p, 'facecolor', cm(c))
	if range_ > 15:
		numticks = 15
	else:
		numticks = range_
	tick_range = np.arange(min(stat_list), max(stat_list)-1, (range_)//numticks)
	plt.xticks(tick_range)
	plt.title(f'Frequency of {stat}')
	plt.xlabel(f'Total {stat}')
	plt.ylabel('Frequency')
	plt.savefig(f'imgs/{stat}_hist_{bins}_bins_{username}') if save else 0
	plt.show() if show else 0

def userPlays():
	ret_dict = dict()
	for match in data:
		# Get the participant
		for part in match['participantIdentities']:
			player = part['player']['summonerName']
			if player not in ret_dict.keys():
				ret_dict[player] = 1
			else:
				ret_dict[player] += 1
	return ret_dict

def userWins():
	ret_dict = dict()
	id_=500
	for match in data:
		# Get the participant
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		player = part['player']['summonerName']
		if match['participants'][id_-1]['stats']['win']:
			if player not in ret_dict.keys():
				ret_dict[player] = 1
			else:
				ret_dict[player] += 1
	return ret_dict

username = 'thomasm16'
# username = 'Demente'
# username = 'Adrian Gomez'
# username = 'LunarFate'
# username = 'Jamessv98'

data = loadData(f'match_det_{username}.json')

uplay = userPlays()
uwins = userWins()
win_list = []
# for plays, wins in zip(uplay, uwins):
# 	print(plays)
# 	win_list.append((plays, uwins[wins]/uplay[plays]))
uplay = sorted(uplay.items(), key=lambda item: item[1])
uwins = sorted(uwins.items(), key=lambda item: item[1])
# win_list = sorted(win_list, key=lambda item: item[1])
for plays, wins in zip(uplay, uwins):
	win_list.append((plays[0], wins[1]/plays[1]))

# uplay = {k: v for k, v in }
# print(uplay['thomasm16']<uplay['Adrian Gomez'])


# plotHist('visionScore', mode='CLASSIC', save=True, show=True)



# print(datetime.timedelta(seconds=sumTime()))
# print(len(data))
# print(sumstat('wardsPlaced',mode='CLASSIC'))
# for key in data[0]['participants'][0]['stats']:
# 	try:
# 		print(f'{key}: {avgStat(key)}')
# 	except:
# 		pass