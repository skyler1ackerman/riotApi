from config import TOKEN, ID
from riotwatcher import LolWatcher, ApiError
import pprint, json, time, pickle
pp = pprint.PrettyPrinter(indent=4)

watcher = LolWatcher(TOKEN)
my_region = 'na1'

username = 'Ryshandala'

me = watcher.summoner.by_name(my_region, username)
# # my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
# # last_match = my_matches['matches'][0]
# # match_detail = watcher.match.by_id(my_region, last_match['gameId'])

i = 0
my_matches = {'matches':[1]}
all_list=[]
while len(my_matches['matches'])!=0:
	my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'], begin_index=i*100, end_index=i*100+100)
	i+=1
	h=0
	while h < len(my_matches['matches']):
		match = my_matches['matches'][h]
		try:
			match_detail = watcher.match.by_id(my_region, match['gameId'])
			all_list.append(match_detail)
			h+=1
		except Exception:
			print(Exception)
			time.sleep(20)
	print(i)

with open(f'pickle/match_det_{username}', 'wb') as f:
		pickle.dump(data, f)

