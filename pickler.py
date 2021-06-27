import pickle, json, time

username = 'thomasm16'

usernames=['thomasm16', 'LunarFate', 'Jamessv98', 'Demente', 'Adrian Gomez', 'Jęnz', 'King Le']


for username in usernames:
	with open(f'json/match_det_{username}.json', "r") as f: 
			data = json.load(f)

	with open(f'match_det_{username}', 'wb') as f:
		pickle.dump(data, f)

	with open(f'match_det_{username}', 'rb') as f:
		new_data = pickle.load(f)