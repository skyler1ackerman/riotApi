from config import TOKEN, ID
from riotwatcher import LolWatcher, ApiError
import pprint, json, time
pp = pprint.PrettyPrinter(indent=4)

watcher = LolWatcher(TOKEN)
my_region = 'na1'

username = 'LunarFate'

me = watcher.summoner.by_name(my_region, username)
# # my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
# # last_match = my_matches['matches'][0]
# # match_detail = watcher.match.by_id(my_region, last_match['gameId'])

i = 0
my_matches = {'matches':[1]}
while len(my_matches['matches'])!=0:
	my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'], begin_index=i*100, end_index=i*100+100)
	i+=1
	h=0
	while h < len(my_matches['matches']):
		match = my_matches['matches'][h]
		try:
			match_detail = watcher.match.by_id(my_region, match['gameId'])
			with open(f"match_det_{username}.json", "a") as f: 
				json.dump(match_detail, f, indent=4)
			h+=1
		except Exception:
			print(Exception)
			time.sleep(20)
		
	print(i)
	# if i==9:
	# 	break
	

