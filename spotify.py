# coding=utf-8
import time
import re
import HTMLParser
import random
import csv
import json
from spot_info import info
import requests
access_token = "BQC0VH36piQq_Xln6GHEAicI05j2ovPNReHLNxGWbh17iP74v9-nWgHYfMXDvSnaK2-9x6C7-J_eVJj3q8jZGe8RRiUhZmalOHL874Qa93etmwCLepY3hs5210bhmvPcI0kWSC3nNGgOriDhbv2gwmcMX4b8oOjXDoLXROOBhMbTTenhL70tUM14Eaf8PZo&refresh_token=AQDtA__4SZ0kzX5f9_PAiQSNhJflTN2Ccn8Z6b9HDZ-f33P0PLOjHF9ejTKNfaUsHkMFp4s5CPyjk0We3YbUMTgbk-L1qjVs0bhGX_H2EndAsEd6_8-V9Dr4t5pArYWIVng"
from datetime import date, timedelta, datetime

def get_song_analysis(song_id):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/audio-analysis/' + str(song_id),headers=headers)
	return r.text

def get_song_info(song_id, access_token, headers=False):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/tracks/' + str(song_id),headers=headers)
	return r.text

def get_multiple_tracks(song_ids, access_token, headers=False):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/tracks/' + "?ids="+ ",".join(song_ids),headers=headers)
	return r.text

def get_song_features(song_id):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/audio-features/' + str(song_id),headers=headers)
	return r.text

def get_multiple_features(song_ids, access_token):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/audio-features/' + "?ids="+ ",".join(song_ids),headers=headers)
	return r.text

def recently_played(access_token):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=50',headers=headers)
	return r.text

def recently_played_url(access_token, url):
	headers = {"Authorization": "Bearer " + access_token}
	r = requests.get(url,headers=headers)
	return r.text

def search(query_param, limit,access_token):
	headers = {"Authorization": "Bearer " + access_token}
	url = 'https://api.spotify.com/v1/search?q=' + query_param.encode('utf-8') + "&type=track&limit=" + str(limit)
	r = requests.get(url,headers=headers)
	return r.text

def personalization(type_):
	headers = {"Authorization": "Bearer " + access_token}
	url = 'https://api.spotify.com/v1/me/top/' + str(type_) + "?limit=50&offset=30"
	r = requests.get(url,headers=headers)
	
	return r.text

def pause():
	headers = {"Authorization": "Bearer " + access_token}
	url = 'https://api.spotify.com/v1/me/player/pause'
	r = requests.put(url,headers=headers)
	return r.text
def play():
	headers = {"Authorization": "Bearer " + access_token}
	url = 'https://api.spotify.com/v1/me/player/play'
	r = requests.put(url,headers=headers)
	return r.text

# for item in json.loads(recently_played())["items"]:
# 	print(item["track"]["id"])
def get_master_song_info(file_name):
	billboard_data = json.loads(open(file_name,'r').read())
	master_song_info = {}
	for date, song_list in billboard_data.items():
		for place, song_info in song_list.items():
			# print(song_info['name'])
			# print(song_info['artist'])
			tuple_key = str((song_info['name'].encode('utf-8'),song_info['artist'].encode('utf-8')))
			if tuple_key not in master_song_info:
				master_song_info.update({tuple_key:{
					'name': song_info['name'],
					'artist': song_info['artist'],
					'history': [],
					}})
			# print(song_info['artist'])
			master_song_info[tuple_key]['history'].append({
				'date': date,
				'place': place,
				'last_week': song_info['last_week'],
				'peak': song_info['peak'],
				'weeks_on_chart': song_info['weeks_on_chart']
				})
	write_file = open("master_song_info.json","w")
	write_file.write(json.dumps(master_song_info,indent=4,sort_keys=True))
# get_master_song_info('new_new_bb_data.json')
def get_access_token():
	# import spotipy
	# from spotipy.oauth2 import SpotifyOAuth
	scope = "user-read-private user-read-email user-read-recently-played user-top-read user-modify-playback-state"
	print(scope)
	# url = "https://accounts.spotify.com/authorize?client_id=8adcf296e36042eca0ca6f5ea5ee897b&response_type=code&redirect_uri=http://localhost:8888/callback&scope=" + scope
	import base64
	# message = "8adcf296e36042eca0ca6f5ea5ee897b:2cb1973105ce490fbd9a86453c60cac1"
	# message_bytes = message.encode('ascii')
	# base64_bytes = base64.b64encode(message_bytes)
	# auth_str = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)
	auth_str = '{}:{}'.format("8adcf296e36042eca0ca6f5ea5ee897b", "2cb1973105ce490fbd9a86453c60cac1")
	b64_auth_str = base64.b64encode(auth_str).decode('utf-8')
	# print(b64_auth_str)
	url = "https://accounts.spotify.com/api/token"
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'Authorization': 'Basic {}'.format(b64_auth_str)
	}
	access_token = json.loads(requests.post(url, data={'grant_type': 'client_credentials'}, headers=headers).text)['access_token']
	return access_token

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
def search_song_exact_artist_song(file_name):
	access_token = get_access_token()
	master_song_info = json.loads(open(file_name,"r").read())
	new_master_song_info = {}
	duplicates = open("no_search2.json", "w")
	actual_duplicates = {}
	try_again = {}
	x = 0
	for tuple_key, song_info in master_song_info.items():
		x += 1
		query_param = 'track:' + song_info['name'] + ' artist:' + song_info['artist'] 
		query_param = query_param.replace(" ", '%20')
		print(query_param + '  '+str(x))
		response = json.loads(search(query_param, 1, access_token))
		if response.get('error'):
			print("ERRRO")
			print(response)
			if response['error']['status'] == 401:
				access_token = get_access_token()
			elif response['error']['status'] == 429:
				try_again.update({tuple_key: song_info})
		elif not response['tracks']['items']:
			try_again.update({tuple_key: song_info})
		else:
			response_info = response['tracks']['items'][0]
			# print(response_info)
			if new_master_song_info.get(response_info['id']):
				if not response_info['id'] in actual_duplicates:
					actual_duplicates.update({response_info['id']: []})
				actual_duplicates[response_info['id']].append([response_info, new_master_song_info[response_info['id']], tuple_key, song_info])
				duplicates.write(json.dumps(response_info,indent=4,sort_keys=True))
				duplicates.write(json.dumps(new_master_song_info[response_info['id']],indent=4,sort_keys=True))
				print(json.dumps(response_info,indent=4,sort_keys=True))
				print(json.dumps(new_master_song_info[response_info['id']],indent=4,sort_keys=True))
			else:
				new_master_song_info.update({response_info['id']: {
					'name': response_info['name'],
					'duration_ms': response_info['duration_ms'],
					'explicit': response_info['explicit'],
					'artists': [{'name': artist['name'], 'id': artist['id']} for artist in response_info['artists']],
					'release_date': response_info['album']['release_date'],
					'album_id': response_info['album']['id'],
					'original_song_info': (tuple_key, song_info),
					}})
	search_song_results_file = open("search_song_results_try20.json","w")
	search_song_results_file.write(json.dumps(new_master_song_info,indent=4,sort_keys=True))
	try_results_file = open("try_again_results_try20.json","w")
	try_results_file.write(json.dumps(try_again,indent=4,sort_keys=True))
	try_results_file = open("actual_duplicates_try20.json","w")
	try_results_file.write(json.dumps(actual_duplicates,indent=4,sort_keys=True))
	everything = {
	'try_again': try_again,
	'results': new_master_song_info,
	'duplicates': actual_duplicates,
	}
	print(json.dumps(everything,indent=4,sort_keys=True))
	return everything

def search_song_plain_text_y_year(everything):
	access_token = get_access_token()
	if not everything:
		songs_to_try = json.loads(open(file_name,"r").read())
		try_again = {}
		duplicates = {}
		master_song_info = {}
	else:
		songs_to_try = everything['try_again']
		everything['try_again'] = None
		master_song_info = everything['results']
		duplicates = everything['duplicates']
		try_again = {}
	csv_file = open("no_search2.csv", "w")
	csvwriter = csv.writer(csv_file)
	x = 0
	for tuple_key, song_info in songs_to_try.items():
		x += 1
		entrance_date = int(min([time_on['date'][-4:] for time_on in song_info['history']]))
		# print(entrance_date)
		query_param = song_info['name'] + ' year:' + str(entrance_date - 3) + "-" + str(entrance_date)
		query_param = query_param.replace(" ", '%20')
		print(query_param + '  '+str(x))
		response = json.loads(search(query_param, 50, access_token))
		print(json.dumps(response,indent=4,sort_keys=True))
		if response.get('error'):
			print("ERRRO")
			print(response)
			if response['error']['status'] == 401:
				access_token = get_access_token()
			elif response['error']['status'] == 429:
				try_again.update({tuple_key: song_info})
		elif not response['tracks']['items']:
			try_again.update({tuple_key: song_info})
			print('no')
		else:
			response_info = response['tracks']['items'][0]
			# print(response_info)
			if master_song_info.get(response_info['id']):
				if not response_info['id'] in duplicates:
					duplicates.update({response_info['id']: []})
				duplicates[response_info['id']].append([response_info, master_song_info[response_info['id']], tuple_key, song_info])
				csv_file.write(json.dumps(response_info,indent=4,sort_keys=True))
				csv_file.write(json.dumps(master_song_info[response_info['id']],indent=4,sort_keys=True))
				print(json.dumps(response_info,indent=4,sort_keys=True))
				print(json.dumps(master_song_info[response_info['id']],indent=4,sort_keys=True))
			else:
				master_song_info.update({response_info['id']: {
					'name': response_info['name'],
					'duration_ms': response_info['duration_ms'],
					'explicit': response_info['explicit'],
					'artists': [{'name': artist['name'], 'id': artist['id']} for artist in response_info['artists']],
					'release_date': response_info['album']['release_date'],
					'album_id': response_info['album']['id'],
					'original_song_info': (tuple_key, song_info),
					}})
	search_song_results_file = open("search_song_results21.json","w")
	search_song_results_file.write(json.dumps(master_song_info,indent=4,sort_keys=True))
	try_results_file = open("try_again_results21.json","w")
	try_results_file.write(json.dumps(try_again,indent=4,sort_keys=True))
	a_duplicates = open("actual_duplicates_try21.json","w")
	a_duplicates.write(json.dumps(duplicates,indent=4,sort_keys=True))
	everything = {
	'try_again': try_again,
	'results': master_song_info,
	'duplicates': duplicates,
	}
	if everything:
		return everything

def search_song_plain_text_n_year(everything, remove_parenthesis=False, remove_dashes=False, remove_slashs=False):
	access_token = get_access_token()
	if not everything:
		songs_to_try = json.loads(open(file_name,"r").read())
		try_again = {}
		duplicates = {}
		master_song_info = {}
	else:
		songs_to_try = everything['try_again']
		everything['try_again'] = None
		master_song_info = everything['results']
		duplicates = everything['duplicates']
		try_again = {}
	csv_file = open("no_search2.csv", "w")
	csvwriter = csv.writer(csv_file)
	x = 0
	for tuple_key, song_info in songs_to_try.items():
		x += 1
		entrance_date = int(min([time_on['date'][-4:] for time_on in song_info['history']]))
		# print(entrance_date)
		query_param = song_info['name']
		if remove_parenthesis:
			query_param = remove_parenthesis2(query_param)
		if remove_dashes:
			query_param = delete_dash(query_param)
		if remove_slashs:
			query_param = delete_slashs(query_param)
		query_param = query_param.replace(" ", '%20')
		print(query_param + '  '+str(x))
		response = json.loads(search(query_param, 1, access_token))
		if response.get('error'):
			print("ERRRO")
			print(response)
			if response['error']['status'] == 401:
				access_token = get_access_token()
			elif response['error']['status'] == 429:
				try_again.update({tuple_key: song_info})
		elif not response['tracks']['items']:
			try_again.update({tuple_key: song_info})
			print('no')
		else:
			response_info = response['tracks']['items'][0]
			# print(response_info)
			if master_song_info.get(response_info['id']):
				if not response_info['id'] in duplicates:
					duplicates.update({response_info['id']: []})
				duplicates[response_info['id']].append([response_info, master_song_info[response_info['id']], tuple_key, song_info])
				csv_file.write(json.dumps(response_info,indent=4,sort_keys=True))
				csv_file.write(json.dumps(master_song_info[response_info['id']],indent=4,sort_keys=True))
				print(json.dumps(response_info,indent=4,sort_keys=True))
				print(json.dumps(master_song_info[response_info['id']],indent=4,sort_keys=True))
			else:
				master_song_info.update({response_info['id']: {
					'name': response_info['name'],
					'duration_ms': response_info['duration_ms'],
					'explicit': response_info['explicit'],
					'artists': [{'name': artist['name'], 'id': artist['id']} for artist in response_info['artists']],
					'release_date': response_info['album']['release_date'],
					'album_id': response_info['album']['id'],
					'original_song_info': (tuple_key, song_info),
					}})
	search_song_results_file = open("search_song_results24.json","w")
	search_song_results_file.write(json.dumps(master_song_info,indent=4,sort_keys=True))
	try_results_file = open("try_again_results24.json","w")
	try_results_file.write(json.dumps(try_again,indent=4,sort_keys=True))
	a_duplicates = open("actual_duplicates_try24.json","w")
	a_duplicates.write(json.dumps(duplicates,indent=4,sort_keys=True))
	everything = {
	'try_again': try_again,
	'results': master_song_info,
	'duplicates': duplicates,
	}
	if everything:
		return everything

def remove_parenthesis2(word):
	new_word = ""
	in_parentehsis = False
	for x, letter in enumerate(word):
		if letter == "(":
			in_parentehsis = True
		# print(in_parentehsis)
		if not in_parentehsis:
			new_word += letter
		if letter == ")":
			in_parentehsis = False
	return new_word

def delete_dash(word):
	new_word = word
	location  = word.find("-")
	if location != -1:
		new_word = word[0:location]
	return new_word

def delete_slashs(word):
	new_word = word
	location  = word.find("/")
	if location != -1:
		new_word = word[location + 1: -1]
	return new_word
# print(json.dumps(search_song_exact_artist_song("only_ranson.json"),indent=4,sort_keys=True))
# print(remove_parenthesis("noah is cool (ft. sam)"))
# search_song_plain_text_n_year(search_song_plain_text_y_year(search_song_exact_artist_song("master_song_info.json")))
# everything2 = {
	# 'try_again': json.loads(open("try_again_results23.json", "r").read()),
	# 'results': json.loads(open("search_song_results23.json","r").read()),
	# 'duplicates': json.loads(open("actual_duplicates_try23.json","r").read())
# }
# search_song_plain_text_n_year(everything2, remove_dashes=True, remove_slashs=True)
# search_song_plain_text_n_year(everything2,remove_parenthesis=True)

def csv_try_again(file_name, csv_file_name):
	file = json.loads(open(file_name, "r").read())
	csv_file = open(csv_file_name, "w")
	csvwriter = csv.writer(csv_file)
	csvwriter.writerow(['Name', 'Artist', 'Date'])
	for stin, info in file.items():
		csvwriter.writerow([info['name'], info['artist'], info['history'][0]['date']])

# csv_try_again("try_again_results24.json", "songs_that_diddnt_return.csv")

def get_length(file_name):
	file = json.loads(open(file_name, "r").read())
	if file_name == "actual_duplicates_try22.json":
		print(len(file))
		print(sum([len(dupe) for name, dupe in file.items()]))
	else:
		print(len(file))

def print_stuff(file_name):
	file = json.loads(open(file_name, "r").read())
	for stin, info in file.items():
		print("name: " +info['name'] + "artist: " + info['artist'])

def turn_master_info_to_original(master_song_info_file_info, duplicate_file, new_file_name):
	file = json.loads(open(master_song_info_file_info, "r").read())
	new_master = {}
	for song_id, info in file.items():
		if new_master.get(info['original_song_info'][0]):
			print("ayooooooooo")
			print(song_id, info)
		info.update({'song_id': song_id})
		new_master.update({info['original_song_info'][0]:info})
	duplicate_file = json.loads(open(duplicate_file, "r").read())
	for song_id, duplicates in duplicate_file.items():
		for duplicate in duplicates:
			response_info = duplicate[0]
			the_info = {
				'song_id': response_info['id'],
				'name': response_info['name'],
				'duration_ms': response_info['duration_ms'],
				'explicit': response_info['explicit'],
				'artists': [{'name': artist['name'], 'id': artist['id']} for artist in response_info['artists']],
				'release_date': response_info['album']['release_date'],
				'album_id': response_info['album']['id'],
				'original_song_info': (duplicate[2], duplicate[3]),
				}
			if new_master.get(the_info['original_song_info'][0]):
				print("ayooooooooo")
				# print(song_id, info)
			print(duplicate[2])
			new_master.update({duplicate[2]: the_info })
	new_file = open(new_file_name, "w")
	new_file.write(json.dumps(new_master,indent=4,sort_keys=True))

def get_all_tracks(results_file, return_file):
	song_infos = json.loads(open(results_file, "r").read())
	access_token = get_access_token()
	x = 0
	z = 0
	a=0
	tuple_keys = []
	song_ids = []
	print(len(song_infos))
	for tuple_key, song_info in song_infos.items():
		a += 1
		if x < 49:
			x += 1
			tuple_keys.append(tuple_key)
			song_ids.append(song_info['song_id'])
		if x == 49:
			print("50")
			z += 1
			print(z)
			response = json.loads(get_multiple_tracks(song_ids,access_token))
			if response.get('error'):
				print("ayoo errror")
				print(response)
				if response['error']['status'] == 401:
					access_token = get_access_token()
			for y, track in enumerate(response['tracks']):
				if not track:
					print("no track ayo")
				tuple_key = tuple_keys[y]
				the_song_info = song_infos[tuple_key]
				# print('ex', track['explicit'])
				the_song_info.update({'explicit': track['explicit']})
				# print(song_infos[tuple_key])
			x=0
			tuple_keys = []
			song_ids = []
		if a == len(song_infos):
			print("last one")
			print(len(song_ids))
			z += 1
			print(z)
			response = json.loads(get_multiple_tracks(song_ids,access_token))
			if response.get('error'):
				print("ayoo errror")
				print(response)
				if response['error']['status'] == 401:
					access_token = get_access_token()
			for y, track in enumerate(response['tracks']):
				if not track:
					print("no track ayo")
				tuple_key = tuple_keys[y]
				the_song_info = song_infos[tuple_key]
				# print('ex', track['explicit'])
				the_song_info.update({'explicit': track['explicit']})
				# print(song_infos[tuple_key])
			x=0
			tuple_keys = []
			song_ids = []

			# print(json.dumps(response,indent=4,sort_keys=True))
	new_file = open(return_file, "w")
	new_file.write(json.dumps(song_infos,indent=4,sort_keys=True))

def get_all_audio_features(results_file, return_file):
	song_infos = json.loads(open(results_file, "r").read())
	access_token = get_access_token()
	x = 0
	tuple_keys = []
	song_ids = []
	print(len(song_infos))
	z = 0
	a = 0
	for tuple_key, song_info in song_infos.items():
		a += 1
		if x < 49:
			x += 1
			tuple_keys.append(tuple_key)
			song_ids.append(song_info['song_id'])
		if x == 49:
			print("50")
			z += 1
			print(z)
			features = get_multiple_features(song_ids,access_token)
			if not features:
				print("ayoooooyyyy")
			response = json.loads(features)
			if response.get('error'):
				if response['error']['status'] == 401:
					access_token = get_access_token()
			for y, track in enumerate(response['audio_features']):
				tuple_key = tuple_keys[y]
				the_song_info = song_infos[tuple_key]
				the_song_info.update({
					'liveness': track['liveness'],
					'loudness': track['loudness'],
					'speechiness': track['speechiness'],
					'energy': track['energy'],
					'key': track['key'],
					'mode': track['mode'],
					'valence': track['valence'],
					'tempo': track['tempo'],
					})
			x=0
			tuple_keys = []
			song_ids = []
			# print(json.dumps(response,indent=4,sort_keys=True))
		if a == len(song_infos):
			print("50")
			z += 1
			print(z)
			features = get_multiple_features(song_ids,access_token)
			if not features:
				print("ayoooooyyyy")
			response = json.loads(features)
			if response.get('error'):
				if response['error']['status'] == 401:
					access_token = get_access_token()
			for y, track in enumerate(response['audio_features']):
				tuple_key = tuple_keys[y]
				the_song_info = song_infos[tuple_key]
				the_song_info.update({
					'liveness': track['liveness'],
					'loudness': track['loudness'],
					'speechiness': track['speechiness'],
					'energy': track['energy'],
					'key': track['key'],
					'mode': track['mode'],
					'valence': track['valence'],
					'tempo': track['tempo'],
					})
			x=0
			tuple_keys = []
			song_ids = []
	new_file = open(return_file, "w")
	new_file.write(json.dumps(song_infos,indent=4,sort_keys=True))

def print_all_results(results_file, new_file2, return_file, make_file=False):
	song_infos = json.loads(open(results_file, "r").read())
	new_file = open(return_file, "w")
	csvwriter = csv.writer(new_file)
	new_file3 = open(new_file2, "w")
	csvwriter2 = csv.writer(new_file3)
	csvwriter2.writerow(["Name","Artists","Release Date", "Duration","Explicit", "liveness", "loudness","speechiness","energy","key","mode","valence", "tempo", "Max Place", "Total Weeks on Billboard", "First Day on Billboard", "Total Artists"])
	csvwriter.writerow(["Date", "Name","Place", "Artists","Release Date", "Duration","Explicit", "liveness", "loudness","speechiness","energy","key","mode","valence", "tempo", "Last Week", "Peak (to this point)", "Weeks on Chart (to this point)", "Total Artists"])
	the_structure = {}
	the_second_structure = []
	for tuple_key, song_info in song_infos.items():
		# print(len(song_info['original_song_info'][1]['history']))
		for time_on_bill in song_info['original_song_info'][1]['history']:
			if make_file:
				the_structure.update({
					tuple_key : {
					'name': song_info['name'],
					'artists': "(comma)".join([artist['name'] for artist in song_info['artists']]),
					'release_date': song_info['release_date'],
					'duration_ms': song_info['duration_ms'],
					'explicit': song_info['explicit'],
					'liveness': song_info['liveness'],
					'loudness': song_info['loudness'],
					'speechiness': song_info['speechiness'],
					'energy': song_info['energy'],
					'key': song_info['key'],
					'mode': song_info['mode'],
					'valence': song_info['valence'],
					'tempo': song_info['tempo'],
					}
					})
				the_second_structure.append({
					'date': time_on_bill['date'],
					'name': song_info['name'],
					'place': time_on_bill['place'],
					'artists': "(comma)".join([artist['name'] for artist in song_info['artists']]),
					'release_date': song_info['release_date'],
					'duration_ms': song_info['duration_ms'],
					'explicit': song_info['explicit'],
					'liveness': song_info['liveness'],
					'loudness': song_info['loudness'],
					'speechiness': song_info['speechiness'],
					'energy': song_info['energy'],
					'key': song_info['key'],
					'mode': song_info['mode'],
					'valence': song_info['valence'],
					'tempo': song_info['tempo'],
					'tuple_key': tuple_key,
					})
			# print(song_info)
			csvwriter.writerow([
				time_on_bill['date'].encode('utf-8'),
				# time_on_bill['place'].encode('utf-8'),
				song_info['name'].encode('utf-8'),
				time_on_bill['place'].encode('utf-8'),
				"(comma)".join([artist['name'] for artist in song_info['artists']]).encode('utf-8'),
				str(song_info['release_date'][0:4]).encode('utf-8'),
				str(1.0 * song_info['duration_ms'] / 1000 / 60).encode('utf-8'),
				str(song_info['explicit']).encode('utf-8'),
				str(song_info['liveness']).encode('utf-8'),
				str(song_info['loudness']).encode('utf-8'),
				str(song_info['speechiness']).encode('utf-8'),
				str(song_info['energy']).encode('utf-8'),
				str(song_info['key']).encode('utf-8'),
				str(song_info['mode']).encode('utf-8'),
				str(song_info['valence']).encode('utf-8'),
				str(song_info['tempo']).encode('utf-8'),
				str(time_on_bill['place'].encode('utf-8') if time_on_bill['last_week'] == "-" else time_on_bill['last_week'].encode('utf-8')),
				str(time_on_bill['peak'].encode('utf-8')),
				str(time_on_bill['weeks_on_chart'].encode('utf-8')),
				str(len(song_info['artists'])),
				])
		csvwriter2.writerow([
			# time_on_bill['place'].encode('utf-8'),
			song_info['name'].encode('utf-8'),
			"(comma)".join([artist['name'] for artist in song_info['artists']]).encode('utf-8'),
			str(song_info['release_date'][0:4]).encode('utf-8'),
			str(1.0 * song_info['duration_ms']  / 1000 / 60).encode('utf-8'),
			str(song_info['explicit']).encode('utf-8'),
			str(song_info['liveness']).encode('utf-8'),
			str(song_info['loudness']).encode('utf-8'),
			str(song_info['speechiness']).encode('utf-8'),
			str(song_info['energy']).encode('utf-8'),
			str(song_info['key']).encode('utf-8'),
			str(song_info['mode']).encode('utf-8'),
			str(song_info['valence']).encode('utf-8'),
			str(song_info['tempo']).encode('utf-8'),
			str(min([int(time_on_bill['place']) for time_on_bill in song_info['original_song_info'][1]['history']])),
			str(len(song_info['original_song_info'][1]['history'])),
			str(min(datetime.strptime(time_on_bill['date'], "%m/%d/%Y") for time_on_bill in song_info['original_song_info'][1]['history']).strftime("%m/%d/%Y")),
			str(len(song_info['artists'])),
			])
		# print([time_on_bill['place'] for time_on_bill in song_info['original_song_info'][1]['history']])
		# print(min([int(time_on_bill['place']) for time_on_bill in song_info['original_song_info'][1]['history']]))
	if make_file:
		json_file = open("all_songs_file.json", "w")
		json_file.write(json.dumps(the_structure,indent=4,sort_keys=True))
		json_file = open("all_songs_file2.json", "w")
		json_file.write(json.dumps(the_second_structure,indent=4,sort_keys=True))

def make_chart(function_html, div_html):
	file = open("spotify_chart.html", "r")
	contents = file.readlines()
	# print(file.read())
	for x, line in enumerate(contents):
		# print(line)
		if line == """      //////////
""":
			the_line = x + 1
		if line == """    <!--  -->
""":
			div_line = x + 2
	file.close()
	contents.insert(the_line,function_html)
	contents.insert(div_line,div_html)
	file = open("spotify_chart.html", "w")
	contents = "".join(contents)
	file.write(contents)
	file.close()
# make_chart("""      function drawChart() {
#         var data = google.visualization.arrayToDataTable([['ID', 'Place', 'Run Order', 'f', 'Population'], ['', 0.25, 0.25, 'f', 2887], ['', 0.75, 0.25, 'f', 3370], ['', 0.25, 0.75, 'f', 3231], ['', 0.75, 0.75, 'f', 3267]]);

#         var options = {
#           title: 'Place vs. Run Order',
#           hAxis: {title: 'Place', minValue: 0, maxValue: 1},
#           vAxis: {title: 'Run Order', minValue: 0, maxValue: 1},
#           legend: 'none'
#         };

#         var chart = new google.visualization.BubbleChart(document.getElementById('chart_div'));

#         chart.draw(data, options);
#       }
# """, """    <div id="chart_div" style="width: 900px; height: 500px;"></div>
# """)

def add_chart(results_file, second_results_file, variable, chart_type):
	song_infos = json.loads(open(results_file, "r").read())
	song_infos = json.loads(open(second_results_file, "r").read())
	data = []
	options = []
	if variable == "explicit":
		
		data = [
		['Explicit or Not', 'Number of Songs'],
		['Explicit', sum([1 if song_info['explicit'] else 0 for tuple_key, song_info in song_infos.items()])],
		['Clean', sum([0 if song_info['explicit'] else 1 for tuple_key, song_info in song_infos.items()])]
		]
		options = """{title: 'Explicit Songs'}"""
	if variable == "tempo":
		options = """{title: 'Tempo'}"""
		data = [[song_info['name'].encode('utf-8'), song_info['tempo']] for tuple_key, song_info in song_infos.items()]
		data.insert(0, ['Song Name', 'Tempo'])
	if variable == "yearhist":
		options = """{title: 'Songs by Year'}"""
		data = [[song_info['name'].encode('utf-8'), int(song_info['release_date'][0:4])] for tuple_key, song_info in song_infos.items()]
		data.insert(0, ['Song Name', 'Year'])
	id_ending = str(random.randint(1, 1000000))
	x = """
      google.charts.setOnLoadCallback(drawChart""" + id_ending + """);
      function drawChart""" + id_ending + """() {
        var data = google.visualization.arrayToDataTable(""" + str(data) + """);

        var options = """ + str(options) + """;

        var chart = new google.visualization.""" + chart_type + """(document.getElementById('chart_div""" + str(id_ending) +"""'));

        chart.draw(data, options);}
"""
	
	div_stuff = """<div id="chart_div""" + str(id_ending) + """" style="width: 900px; height: 500px;"></div>
"""
	make_chart(x, div_stuff)

def restrict_to_top_x(file, new_file, restrict):
	the_file = json.loads(open(file, "r").read())
	for song_info in the_file:
		if not song_info['place'] >= restrict:
			the_file.remove(song_info)
	open(new_file, "w").write(json.dumps(the_file,indent=4,sort_keys=True))

def most_common_word(all_songs_file, return_file, second_return_file):
	file = json.loads(open(all_songs_file, "r").read())
	all_words = {}
	for song_info in file:
		words = song_info['name'].split()
		for word in words:
			if word not in all_words:
				all_words.update({word: 0})
			all_words[word] += 1
	all_words = sorted(all_words.items(), key=lambda k: k[1], reverse=True)
	csvwriter = csv.writer(open(second_return_file, "w"))
	csvwriter.writerow(['Word', "Number of Instances"])
	for word_info in all_words:
		csvwriter.writerow([word_info[0].encode("utf-8"), word_info[1]])
	open(return_file, "w").write(json.dumps(all_words,indent=4,sort_keys=True))
# most_common_word("all_songs_file2.json", "most_common_word.json", "most_common_word.csv")


# restrict_to_top_x("all_songs_file2.json", "all")

# add_chart("all_songs_file.json", "all_songs_file2.json", "explicit", "PieChart")
# add_chart("all_songs_file.json","all_songs_file2.json", "yearhist", "Histogram")




# print_all_results("get_all_audio_features.json", "28000.csv", "all_results_final_try5.csv",  make_file=True)




# get_all_tracks("new_search_results.json","get_all_tracks.json")
# get_all_audio_features("get_all_tracks.json", "get_all_audio_features.json")

# turn_master_info_to_original("search_song_results24.json","actual_duplicates_try24.json","new_search_results.json")
# print_stuff("try_again_results24.json")

# get_length("actual_duplicates_try24.json")
# get_length("search_song_results24.json")
# get_length("try_again_results24.json")
# search_song_plain_text("try_again_results2.json")
# replace_missing_songs("missing songs - Sheet1.csv")
# response = json.loads(search("a", 1, "BQC-0T2sDHUn635eFbELNwpBRdxv-ZdVP7206Vrstzdx2yWFrxjZXCwnL9Y7RvbMaSf0oj5go4wW8Kff41Vz_IdI8nSt_L4g-QVngvpyWANM78YQMltA-6-0xtBtWyN28hclbs0t0Eh_Z1amDm51STvEXX_r7usEAS7DAItdlquDPgVEsBZlYA&refresh_token=AQB-Xs1FaGXFvXss6YpnJEBkh-s_42CPTNxsOxBLKfrALhfKEo_U6reY3063KsKOUQ32Opq6i7itlwk2yQb9uyGbSykYloIIC15FYt0PpjWToaLZxWj0OzUeFKIIDoNIX8w"))
# try_again_results = json.loads(open("try_again_results_try10.json", "r").read())
# everything2 = {
# 	'try_again': try_again_results,
# 	'results': json.loads(open("search_song_results_try10.json","r").read()),
# 	'duplicates': json.loads(open("actual_duplicates_try10.json","r").read())
# }
# search_song_plain_text_y_year(everything2)
# print(len(json.loads(open("master_song_info.json", "r").read())))
# try_again = json.loads(open("try_again_results3.json", "r").read())
# for f, g in try_again.items():
	# print(g['name'] + ' - ' + g['artist'] + " - " +g['history'][0]['date'])
# print(len(json.loads(open("search_song_results3.json", "r").read())))
# print(jsn.looads(get_song_info("5Z0AM9HW78XIyZqF2BPasa")))
def replace_missing_songs(csv_file):
	the_csv_file = open(csv_file, "r").read()
	import ast
	# print(the_csv_file)
	missing_songs = the_csv_file.splitlines()
	billboard_data = json.loads(open("new_data_with_new.json", "r").read())
	# print(missing_songs)
	for row in missing_songs[1:]:
		row = row.split(",")
		song_infos = billboard_data[str(row[0])]
		first_orginal_song_at_place = str(song_infos[row[1]])
		song_infos[row[1]].update({
            "artist": row[3], 
            "last_week": row[4], 
            "name": row[2], 
            "peak": row[5],
            "weeks_on_chart": row[6]
			})
		current_replace_place = int(row[1]) + 1
		orginal_song_at_place = ast.literal_eval(first_orginal_song_at_place)
		while current_replace_place < 100:
			print(orginal_song_at_place)
			next_orginal_song_at_place = str(song_infos[str(current_replace_place)])
			print(next_orginal_song_at_place)
			song_infos[str(current_replace_place)].update(orginal_song_at_place)
			orginal_song_at_place = ast.literal_eval(next_orginal_song_at_place)
			print(orginal_song_at_place)
			current_replace_place += 1
		song_infos.update({str(current_replace_place): orginal_song_at_place})
	new_file = open("new_new_bb_data.json","w")
	new_file.write(json.dumps(billboard_data,indent=4,sort_keys=True))
import string

list_o_stuff = []
for l in string.ascii_lowercase:
	list_o_stuff.append(l)
for l in string.ascii_uppercase:
	list_o_stuff.append(l)
for l in [0,1,2,3,4,5,6,7,8,9]:
	list_o_stuff.append(l)

def get_random_id():
	random_id = "0"
	for x in xrange(1,22):
		random_id += str((list_o_stuff[random.randint(0,len(list_o_stuff)-1)]))
	return random_id


# csv_file = open("spotify.csv",'w')
# csvwriter = csv.writer(csv_file)
# csvwriter.writerow(["Date","Place", "Song","Artist","Last Week", "Peak","Weeks On Chart"])

def get_song_on_billboard(date):
	url = "https://www.billboard.com/charts/hot-100/" + str(date)
	r = requests.get(url)
	body = r.text
	# print("got body")
	positions = []
	end_positions = []
	second_positions = []
	second_end_positions = []
	# print(body)
	def get_values(search_string, end_search_string):
			# print("here values")
			positions = []
			end_positions = []
			final_values = []
			# print("before re")
			positions = [m.start() + len(search_string) for m in re.finditer(search_string, body)]
			# print("after re")
			# print(positions)
			# for start_char in xrange(len(body)):
			# 	if body[start_char:start_char + len(search_string)] == search_string:
			# 		positions.append(start_char + len(search_string))
			for position in positions:
				end_positions.append(body.find(end_search_string,position))
			x = 0
			for position in positions:
				final_values.append(body[position:end_positions[x]])
				x+= 1
			return final_values
	names = get_values("""<span class="chart-element__information__song text--truncate color--primary">""","""</span>""")
	artists = get_values("""<span class="chart-element__information__artist text--truncate color--secondary">""","""</span>""")
	weeks_on_charts = get_values("""<span class="chart-element__meta text--center color--secondary text--week">""","""</span>""")
	peaks = get_values("""<span class="chart-element__meta text--center color--secondary text--peak">""","""</span>""")
	last_weeks = get_values("""<span class="chart-element__meta text--center color--secondary text--last">""","""</span>""")
	song_infos = {}
	x = 0
	if len(names) == len(artists) == len(last_weeks) == len(peaks) == len(weeks_on_charts):
		for x in range(0, len(names)):
			song_infos.update({(x+1):{
				"name": HTMLParser.HTMLParser().unescape(names[x]),
				"artist": HTMLParser.HTMLParser().unescape(artists[x]),
				"peak": HTMLParser.HTMLParser().unescape(peaks[x]),
				"last_week": HTMLParser.HTMLParser().unescape(last_weeks[x]),
				"weeks_on_chart": HTMLParser.HTMLParser().unescape(weeks_on_charts[x]),
				}})
			x += 1
		# print(song_infos)
		for y, name in song_infos.items():
			# print(name["name"])
			csvwriter.writerow([
				str(date.strftime("%m/%d/%Y")),
				str(y),
				name["name"].encode('utf-8'),
				name["artist"].encode('utf-8'),
				name["last_week"].encode('utf-8'),
				name["peak"].encode('utf-8'),
				name["weeks_on_chart"].encode('utf-8'),
				])
		return song_infos
	else:
		print("sadghlsdhglshdglhsdlhg")
		return {}
def allsaturdays(year):
   d = date(year, 1, 1)                    # January 1st
   d += timedelta(days = 5 - d.weekday() if d.weekday() <= 5 else 7 + 5 - d.weekday())  # First Sunday
   while d.year == year:
      yield d
      d += timedelta(days = 7)
def run_all(start_year, end_year):
	current_year = start_year
	data = {}
	t1 = time.time()
	while current_year <= end_year:
		for saturday in allsaturdays(current_year):
			t2 = time.time()
			print(round(t2 - t1, 2))
			# if t2 - t1 < 2:
			# 	time.sleep(2 - (t2 - t1))
			t1 = time.time()
			time.sleep(2)
			print(saturday)
			data.update({saturday.strftime("%m/%d/%Y"): get_song_on_billboard(saturday)})
		current_year += 1
	return data
# data_structure = open("data_structure.json", "w")
# data_structure.write(json.dumps(run_all(1959,2020),indent=4,sort_keys=True))
def get_needed_days(data):
	current_year = 1959
	end_year = 2020
	needed_days = []
	while current_year <= end_year:
		for saturday in allsaturdays(current_year):
			if not data[saturday.strftime("%m/%d/%Y")]:
				# pass
				needed_days.append(saturday)
		current_year += 1
	return needed_days
def create_csv(data):
	csv_file = open("all_spotify.csv", "w")
	csvwriter = csv.writer(csv_file)
	csvwriter.writerow(["Date","Place", "Song","Artist","Last Week", "Peak","Weeks On Chart"])
	for date, song_list in data.items():
		for place, song_info in song_list.items():
			csvwriter.writerow([
				str(date),
				str(place),
				song_info["name"].encode('utf-8'),
				song_info["artist"].encode('utf-8'),
				song_info["last_week"].encode('utf-8'),
				song_info["peak"].encode('utf-8'),
				song_info["weeks_on_chart"].encode('utf-8'),
				])
def find_missing_songs_22():
	a = []
	for x in xrange(1,101):
		a.append(x)
	new_data = json.loads(open("new_data_with_new.json","r").read())
	for date, song_list in new_data.items():
		if len(song_list) != 100:
			b = []
			print(date[-4:] + "-" + date[0:2] + '-'+ date[3:5])
			for place, song_info in song_list.items():
				b.append(int(place))
			# print(list(set(a).difference(b)))
			# print(len(song_list))
def add_needed_days():
	needed_days = get_needed_days(actual_data)
	data = actual_data
	t1 = time.time()
	for needed_day in needed_days:
		t2 = time.time()
		print(round(t2 - t1, 2))
		# if t2 - t1 < 2:
		# 	time.sleep(2 - (t2 - t1))
		t1 = time.time()
		time.sleep(2)
		print(needed_day)
		data.update({needed_day.strftime("%m/%d/%Y"): get_song_on_billboard(needed_day)})
	new_file = open("new_data_with_new.json", "w")
	new_file.write(json.dumps(data,indent=4,sort_keys=True))
def remove_commas():
	# from spotify_structure import spotify_
	spotify_ = json.loads(open("text_version_test.txt","r").read())
	no_commas = open("no_commas.csv", "w")
	for date, info in spotify_:
		for place, song_info in info:
			no_commas.write(",".join(
				date,
				str(place),
				song_info['name'].replace(",","(comma)"),
				song_info['artist'].replace(",","(comma)"),
				song_info['last_week'].replace(",","(comma)"),
				song_info['peak'].replace(",","(comma)"),
				song_info['weeks_on_chart'].replace(",","(comma)"),
				))


def get_past_songs():
	access_token = "BQD11Spmf-b1UEnZHX8S-gLx7iN41AsINlewY6gsMVGlW22XMezORTkJYLHBHpdGIUvzYk05pQp5My7WLMMUzlsNIEPFDomfuY2CPIfWHDu-2xo18kfoLa6ilqByVh5DJ2oRGRxCaRt7YZnLgGuUSuuVJNW0Zo_E1zScUgFr"
	all_info = []
	def get_songs(url):
		if url:
			return recently_played_url(access_token,url + "")
		else:
			return None
	def append_infos(songs):
		# print(json.dumps(songs,indent=4,sort_keys=True))
		for thing in songs['items']:
			all_info.append({
				'played_at': thing['played_at'],
				'name': thing['track']['name'],
				'artists': [{'name': artist['name'], 'id': artist['id']} for artist in thing['track']['artists']],
				'id': thing['track']['id'],
				})
		# print(json.dumps(songs,indent=4,sort_keys=True))
		return songs['next']
	x = 0
	the_next = append_infos(json.loads(get_songs("https://api.spotify.com/v1/me/player/recently-played")))
	while x < 100:
		songs = get_songs(the_next)
		if songs:
			the_next = append_infos(json.loads(songs))
		else:
			print(x)
			break
		x += 1
	return all_info
print(json.dumps(get_past_songs(),indent=4,sort_keys=True))











