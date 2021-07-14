# %%
from dataMan import getChampNames
import json, datetime, pprint, statistics, pickle
from copy import deepcopy
from config import TOKEN, ID
from riotwatcher import LolWatcher, ApiError
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from riotClass import *
from functools import partial
pp = pprint.PrettyPrinter(indent=4)

# %%
my_region = 'na1'

username = '<USERNAME>'

watcher = LolWatcher(TOKEN)
latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']

class User:
	# TODO: Troubleshoot why this is so slow
	def __init__(self, username):
		self.username = username
		self.data = self.loadData(f'pickle/match_det_{self.username}')
		self.id = self.getUserId()
		for match in self.data.matchlist:
			match.get_id(self.id)
		self.champ_names = self.getChampNames()
		self.champ_ids = self.getChampIDs()
		self.fdata = deepcopy(self.data)
	
	def resetData(self):
		self.fdata = deepcopy(self.data)
	
	def getUserId(self):
		# First match has most recent id
		for part in self.data.matchlist[0].participantIdentities:
			if username == part.player.summonerName:
				return part.player.accountId
		raise Exception('Player not found in first game!')

	def filterMode(self, mode):
		for match in self.fdata.matchlist:
			if match.gameMode != mode:
				self.fdata.matchlist.remove(match)

	def filterRole(self, lane):
		for match in self.fdata.matchlist:
			player = match.participants[match.userIndex]
			if player.timeline.lane!=lane:
				self.fdata.matchlist.remove(match)
	
	def filterLane(self, role):
		for match in self.fdata.matchlist:
			player = match.participants[match.userIndex]
			if player.timeline.role!=role:
				self.fdata.matchlist.remove(match)

	def filterChamp(self, champ):
		champ_id=self.getChampID(champ)
		for match in self.fdata.matchlist:
			player = match.participants[match.userIndex]
			if player.championId != champ_id:
				self.fdata.matchlist.remove(match)

	def loadData(self, file):
		with open(file, 'rb') as f:
			return jsons.load({'matchlist': pickle.load(f)}, MatchList)

	def getChampNames(self):
		static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
		champ_dict = dict()
		for key in static_champ_list['data']:
			row = static_champ_list['data'][key]
			champ_dict[row['key']] = row['id']
		return champ_dict

	def getChampName(self, id_):
		return self.champ_names[str(id_)]

	def getChampIDs(self):
		return {v:int(k) for k,v in self.champ_names.items()}

	def getChampID(self, name):
		return self.champ_ids[name]

	def getStatList(self, *stat_list):
		ret_list = [[] for _ in stat_list]
		for match in self.fdata.matchlist:
			# Figure out which player is the user
			player = match.participants[match.userIndex]
			try:
				for i, stat in enumerate(stat_list):
					ret_list[i].append(getattr(player.stats, stat))
			except KeyError: # TODO: Better way to do this?
				pass # TODO: Check if this evenly spreads stats
		return np.array(ret_list)

	def maxStat(self, *stat_list):
			return [max(x) for x in self.getStatList(*stat_list)]

	def sumstat(self, *stat_list):
			return [sum(x) for x in self.getStatList(*stat_list)]

	def avgStat(self, *stat_list):
		return [np.average(x) for x in self.getStatList(*stat_list)]

	def sumTeamStat(self, stat): #TODO: Convert this to list 
		total = 0
		for match in self.fdata.matchlist:
			team_id = match.participants[match.userIndex].teamId
			# Team is either 100 or 200, so we can do this
			total+=getattr(match.teams[(team_id//100)-1], stat)
		return total

	def sumOtherTeamStat(self, stat): #TODO: Make one function?
		total = 0
		for match in self.fdata.matchlist:
			team_id = match.participants[match.userIndex].teamId
			# Team is either 100 or 200, so we can do this
			total+=getattr(match.teams[1-((team_id//100)-1)], stat)
		return total

	def sumTime(self):
		return sum(match.gameDuration for match in self.fdata.matchlist)

	def maxTime(self):
		return max(match.gameDuration for match in self.fdata.matchlist)

	def plotHist(self, stat, bins=None, save=False, show=True, rotation=0): # TODO: Fix zeros
		# Get the stats list
		stat_list = self.getStatList(stat)[0]
		print(stat_list)
		# Get color map
		cm = plt.cm.get_cmap('plasma')
		# Make the histogram
		range_ = max(stat_list)-min(stat_list)
		if not bins:
			bins = range_
		try:
			bin_range = np.arange(min(stat_list), max(stat_list), (range_)//bins)-.5
		except ZeroDivisionError:
			raise Exception('Too many bins!')
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

	def graphScatter(self, *stat_list, save=False, show=True):
		print(stat_list)
		if len(stat_list)!=2:
			raise Exception('Only supported for two stats vs eachother')
		ret_list = self.getStatList(*stat_list)

		plt.scatter(ret_list[0], ret_list[1], c=np.multiply(ret_list[0], ret_list[1]), cmap='plasma')
		plt.xlabel(stat_list[0])
		plt.ylabel(stat_list[1])
		title = f'{stat_list[0]} vs {stat_list[1]}'
		plt.title(title)
		plt.savefig(f'imgs/scatter/{title}_scatter_{username}') if save else 0
		plt.show() if show else 0

	def graphDict(self, graph_dict, num_vals=8, title=None, xlabel=None, ylabel=None, save=False, show=True, rotation=45):
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

	def graphNormDist(self, stat, save=False, show=True, mode=None, lane=None, role=None, champ=None, color='maroon'):
		if isinstance(stat, list):
			raise Exception('Only supported for one stat at a time')
		norm_list=self.getStatList(stat, mode=mode, lane=lane, role=role, champ=champ)[0]
		norm_list.sort()
		mean = statistics.mean(norm_list)
		sd = statistics.stdev(norm_list)
		plt.plot(norm_list, norm.pdf(norm_list, mean, sd), color=color)
		plt.xlabel(stat)
		plt.ylabel('Frequency')
		plt.title(f'Normal Distribution of {stat}')
		plt.savefig(f'imgs/norm/{stat}_norm_{username}') if save else 0
		plt.show() if show else 0

	def userPlays(self): # TODO: Work with ID's?
		ret_dict = dict()
		for match in self.fdata.matchlist:
			for part in match.participantIdentities:
				player = part.player.summonerName
				if player not in ret_dict.keys():
					ret_dict[player] = 1
				else:
					ret_dict[player] += 1
		return {k:v for k,v in sorted(ret_dict.items(), key=lambda item: item[1])}

	def champCounts(self):
		ret_dict = dict()
		for match in self.fdata.matchlist:
			player = match.participants[match.userIndex]
			champ = player.championId
			if champ in ret_dict.keys():
				ret_dict[champ]+=1
			else:
				ret_dict[champ]=1
		return {self.getChampName(k):v for k,v in sorted(ret_dict.items(), key=lambda item: item[1])}

	def champKDAs(self, min_games=10):
		ret_dict = dict()
		for match in self.fdata.matchlist:
			player = match.participants[match.userIndex]
			champ = player.championId
			kills= player.stats.kills
			deaths = player.stats.deaths
			assists = player.stats.assists
			if champ in ret_dict.keys():
				ret_dict[champ]['kills']+=kills
				ret_dict[champ]['assists']+=assists
				ret_dict[champ]['deaths']+=deaths
				ret_dict[champ]['count']+=1
			else:
				ret_dict[champ]={'kills':kills, 'deaths':deaths,'assists':assists,'count':1}
		ret_dict = {k:(v['kills']+v['assists'])/max([1,v['deaths']]) for k,v in ret_dict.items() if v['count'] >=min_games}
		return {self.getChampName(k):v for k,v in sorted(ret_dict.items(), key=lambda item: item[1])}

	# TODO: Fix and move to graph class
	# TODO: Make this work with maxstat and sumstat	
	# TODO: How to iterate through classes
	def compareStats(self, stat, userList, title=None, xlabel=None, ylabel=None, save=False, show=True, rotation=0):
		stat_dict = dict()
		for user in userList:
			stat_dict[user] = user.avgStat(stat)
		print(stat_dict)
		self.graphDict(stat_dict, num_vals=len(stat_dict), title=title, xlabel=xlabel, ylabel=ylabel, save=save, show=show, rotation=rotation)

	# TODO: Make generic for
	# TODO: Make filter for champ
	def statPerChamp(self, stat, min_games=5):
		champ_counts = self.champCounts()
		stat_dict = dict()
		for k, v in champ_counts.items():
			if v >= min_games:
				stat_dict[k] = self.avgStat(stat)
		return {k:v for k,v in sorted(stat_dict.items(), key=lambda item: item[1])}


stats = ['wardsPlaced', 'wardsKilled', 'visionWardsBoughtInGame', 'visionScore']
userList=['thomasm16', 'Demente', 'Adrian Gomez', 'Jamessv98']
stat = 'visionScore'
stat_list = ['totalTimeCrowdControlDealt', 'pentaKills']



# %%

tom = User(username)


# plotHist('visionScore', mode='CLASSIC', save=True, show=True)
# TODO: STAT per STAT
# TODO: Allow graphing of many stats
# TODO: Improve titles
# TODO: Items and runes
# TODO: Fix default values

# %%
tom.filterMode('CLASSIC')
tom.avgStat(stat)

# %%
# print(data.matchlist[0].userIndex)
# %%
