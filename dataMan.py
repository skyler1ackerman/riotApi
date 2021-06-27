import json, datetime, pprint, statistics, pickle
from config import TOKEN, ID
from riotwatcher import LolWatcher, ApiError
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
pp = pprint.PrettyPrinter(indent=4)

my_region = 'na1'

# username = 'thomasm16'
# username = 'Demente'
# username = 'Adrian Gomez'
# username = 'LunarFate'
# username = 'Jamessv98'
username = 'Jęnz'
# username = 'King Le'

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

def getChampNames():
	static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
	champ_dict = dict()
	for key in static_champ_list['data']:
	    row = static_champ_list['data'][key]
	    champ_dict[row['key']] = row['id']
	return champ_dict

def getChampName(id_):
	if 'champ_dict' not in globals():
		global champ_dict # TODO: Change this to be from file
		champ_dict = getChampNames()
	return champ_dict[str(id_)]

def getChampIDs():
	if 'champ_dict' not in globals():
		global champ_dict # TODO: Change this to be from file
		champ_dict = getChampNames()
	return {v:int(k) for k,v in champ_dict.items()}

def getChampID(name):
	if 'id_dict' not in globals():
		global id_dict # TODO: Change this to be from file
		id_dict = getChampIDs()
	return id_dict[name]

def loadData(file):
	with open(file, 'rb') as f:
		return pickle.load(f)

def getUserId(username=username):
	# First match has most recent id
	for part in data[0]['participantIdentities']:
		if username == part['player']['summonerName']:
			return part['player']['accountId']
	raise 

def getStatList(stat_list, mode=None, lane=None, role=None, username=username, champ=None, timenorm=False):
	if isinstance(stat_list, list):
		ret_list = [[] for x in stat_list]
	else:
		ret_list = list()
	if champ:
		champ_id=getChampID(champ)
	sum_id=getUserId(username=username)
	for match in data:
		if mode != None and match['gameMode']!=mode:
			continue
		# Figure out which player is the user
		for part in match['participantIdentities']:
			if sum_id == part['player']['accountId']:
				player = match['participants'][part['participantId']-1]
		if lane and player['timeline']['lane']!=lane:
			continue
		if role and player['timeline']['role']!=role:
			continue
		if champ and player['championId']!=champ_id:
			continue
		# Sum the total of that stat
		try:
			if not isinstance(stat_list, list):
				ret_list.append(player['stats'][stat_list])
			else:
				temp=[]
				for i, stat in enumerate(stat_list):
					if timenorm:
						temp.append(player['stats'][stat]/match['gameDuration'])
					else:
						temp.append(player['stats'][stat])
				for i, val in enumerate(temp):
					ret_list[i].append(val)
		except KeyError:
			pass
	return np.array(ret_list)

def maxStat(stat_list, mode=None, lane=None, role=None, username=username, champ=None, timenorm=None):
	if isinstance(stat_list, list):
		return [max(x) for x in getStatList(**locals())]
	return max(getStatList(**locals()))

def sumstat(stat_list, mode=None, lane=None, role=None, username=username, champ=None):
	if isinstance(stat_list, list):
		return [sum(x) for x in getStatList(**locals())]
	return sum(getStatList(**locals()))

def avgStat(stat_list, mode=None, lane=None, role=None, username=username, champ=None, timenorm=None):
	if isinstance(stat_list, list):
		return [np.average(x) for x in getStatList(**locals())]
	return np.average(getStatList(**locals()))

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

def plotHist(stat, mode=None, lane=None, champ=None, bins=None, save=False, show=True, timenorm=False, rotation=0):
	# Get the stats list
	stat_list = getStatList(stat, mode=mode, lane=lane, champ=champ, timenorm=timenorm)
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
	plt.xticks(tick_range, rotation=rotation)
	plt.title(f'Frequency of {stat}')
	plt.xlabel(f'Total {stat}')
	plt.ylabel('Frequency')
	plt.savefig(f'imgs/{stat}_hist_{bins}_bins_{username}') if save else 0
	plt.show() if show else 0

def graphScatter(stat_list, save=False, show=True, mode=None, lane=None, role=None, champ=None):
	if len(stat_list)!=2:
		raise Exception('Only supported for two stats vs eachother')
	ret_list = getStatList(stat_list, mode=mode, lane=lane, role=role, champ=champ)

	plt.scatter(ret_list[0], ret_list[1], c=np.multiply(ret_list[0], ret_list[1]), cmap='plasma')
	plt.xlabel(stat_list[0])
	plt.ylabel(stat_list[1])
	title = f'{stat_list[0]} vs {stat_list[1]}'
	plt.title(title)
	plt.savefig(f'imgs/scatter/{title}_scatter_{username}') if save else 0
	plt.show() if show else 0

def graphDict(graph_dict, num_vals=8, title=None, xlabel=None, ylabel=None, save=False, show=True, rotation=45):
	labels = list(reversed(list(graph_dict.keys())[-num_vals:]))
	vals = list(reversed(list(graph_dict.values())[-num_vals:]))

	rescale = lambda y: (y - np.min(y)) / (np.max(y) - np.min(y))
	cm = plt.cm.get_cmap('plasma')

	x = np.arange(len(labels))
	width = .8
	rect = plt.bar(x, vals, width, label='graph', color=cm(rescale(vals)))
	plt.xticks(x, labels, rotation=rotation)
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.savefig(f'imgs/{title}_bar_{num_vals}_bars_{username}') if save else 0
	plt.show() if show else 0

def graphNormDist(stat, save=False, show=True, mode=None, lane=None, role=None, champ=None, color='maroon'):
	if isinstance(stat, list):
		raise Exception('Only supported for one stat at a time')
	norm_list=getStatList(stat, mode=mode, lane=lane, role=role, champ=champ)
	norm_list.sort()
	mean = statistics.mean(norm_list)
	sd = statistics.stdev(norm_list)
	plt.plot(norm_list, norm.pdf(norm_list, mean, sd), color=color)
	plt.xlabel(stat)
	plt.ylabel('Frequency')
	plt.title(f'Normal Distribution of {stat}')
	plt.savefig(f'imgs/norm/{stat}_norm_{username}') if save else 0
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
		toAdd = 0
		if match['participants'][id_-1]['stats']['win']:
			toAdd = 1
		if player not in ret_dict.keys():
			ret_dict[player] = toAdd
		else:
			ret_dict[player] += toAdd
	return ret_dict

def champCounts():
	id_=500
	ret_dict = dict()
	for match in data:
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				id_=part['participantId']
		champ = match['participants'][id_-1]['championId']
		if champ in ret_dict.keys():
			ret_dict[champ]+=1
		else:
			ret_dict[champ]=1
	return {getChampName(k):v for k,v in sorted(ret_dict.items(), key=lambda item: item[1])}

def champKDAs(min_games=10):
	ret_dict = dict()
	for match in data:
		for part in match['participantIdentities']:
			if username == part['player']['summonerName']:
				player= match['participants'][part['participantId']-1]
		champ = player['championId']
		kills= player['stats']['kills']
		deaths = player['stats']['deaths']
		assists = player['stats']['assists']
		if champ in ret_dict.keys():
			ret_dict[champ]['kills']+=kills
			ret_dict[champ]['assists']+=assists
			ret_dict[champ]['deaths']+=deaths
			ret_dict[champ]['count']+=1
		else:
			ret_dict[champ]={'kills':kills, 'deaths':deaths,'assists':assists,'count':1}
	ret_dict = {k:(v['kills']+v['assists'])/max([1,v['deaths']]) for k,v in ret_dict.items() if v['count'] >=min_games}
	return {getChampName(k):v for k,v in sorted(ret_dict.items(), key=lambda item: item[1])}

def compareStats(stat, userList, fun=avgStat, mode=None, lane=None, role=None, title=None, xlabel=None, ylabel=None, save=False, show=True, rotation=0, timenorm=False):
	global data
	stat_dict = dict()
	for user in userList:
		data = loadData(f'pickle/match_det_{user}')
		stat_dict[user] = fun(stat, mode=mode, lane=lane, role=role, username=user, timenorm=timenorm)
	print(stat_dict)
	graphDict(stat_dict, num_vals=len(stat_dict), title=title, xlabel=xlabel, ylabel=ylabel, save=save, show=show, rotation=rotation)

def statPerChamp(stat, min_games=3, fun=avgStat):
	champ_counts = champCounts()
	stat_dict = dict()
	for k, v in champ_counts.items():
		if v >= min_games:
			stat_dict[k] = fun(stat, champ=k)
	return {k:v for k,v in sorted(stat_dict.items(), key=lambda item: item[1])}

# def statPerStat(stat_list, mode=None, lane=None, role=None)


# champCounts = champCounts()
# graphDict(champCounts, ylabel='Total plays', title='Total champ plays', save=True, num_vals=10)
# print(avgStat('visionScore', mode='CLASSIC'))
stats = ['wardsPlaced', 'wardsKilled', 'visionWardsBoughtInGame', 'visionScore']
userList=['thomasm16', 'Demente', 'Adrian Gomez', 'Jęnz']
stat = 'visionScore'
stat_list = ['totalTimeCrowdControlDealt', 'visionScore']
# compareStats(stat, userList, role='DUO_SUPPORT', title=f' Avg {stat} per person', ylabel=f'Avg {stat} per game', xlabel=f'Player', save=True, timenorm=True)




# data = loadData(f'pickle/match_det_{username}')

# graphDict(champKDAs(), title=f'{username} Best KDA\'s', xlabel='Champs', ylabel='KDA', save=True, show=True)


# avgStat(stat, champ='Syndra')
# graphNormDist(stat, mode='CLASSIC', show=False)
stat = 'goldEarned'
# graphNormDist(stat, mode='CLASSIC', color='blue')
# plotHist(stat, mode='CLASSIC', timenorm=True, bins=20, rotation=90)

# graphDict(statPerChamp(stat, min_games=20), title='Vision Score per champ', xlabel='Champion', ylabel='Vision Score', rotation=45,save=True, num_vals=20)
# print(avgStat(stat, champ='Thresh'))




# pprint.pprint(data[0]['participants'][0]['stats'])


# graphDict(champCounts(), save=True, title='King is a one trick', rotation=0)

# plotHist('visionScore', mode='CLASSIC', save=True, show=True)
# TODO: STAT per STAT
# TODO: Allow graphing of many stats
# TODO: Improve titles
# TODO: Items and runes
