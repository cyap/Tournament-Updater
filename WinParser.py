import traceback
import re

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

####
urls = {
	'lc':[
		'http://www.smogon.com/forums/threads/the-lc-open-vi-round-1.3610246/'
	],
	'ubers':[
	'http://www.smogon.com/forums/threads/the-ubers-open-vi-round-1.3610289/'
	]
}

####

def posts_from_thread(url, start=1):
	posts = []
	
	# Calculate page of last post
	first_page = BeautifulSoup(urlopen(url).read().decode(), 'html.parser')
	try:
		end = int(str(first_page.find(class_='pageNavHeader'))
			.split('of ')[1].split('<')[0]) * 25
	except:
	# only one page
		end = 25

	# Iterate through all pages
	for i in range(start, int((end-1) / 25) + 2):
		page_num = 'page-' + str(i)
		try:
			page = urlopen(url.strip() + page_num).read().decode()
			posts += BeautifulSoup(page, 'html.parser').find_all(
				lambda x: x.name == 'li' and x.has_attr('data-author'))
		except:
			traceback.print_exc()
	return posts
	
def parse_post(post):
	
	# Post number
	number_tag = post.find('a', {'class':'postNumber'})
	post_number = number_tag.decode_contents(formatter='html')

	# Author
	author = post['data-author']
	
	# Body
	content = post.find('blockquote', 
		{'class':'messageText ugc baseHtml'}).decode_contents(formatter='html')
	
	# Timestamp
	timestampHTML = post.find('a', {'class':'datePermalink'}).findChildren()[0]
	timestamp = ['data-datestring']
		
	return {'post_number':post_number,
			'author':author, 
			'content':content, 
			'timestamp':timestamp}
	
def parse_pairings(raw_post):

	pairings = {}
	winners = []
	losers = []
	
	# Scrub post
	post = BeautifulSoup(raw_post, 'html.parser')
	post.a.unwrap()
	post.span.unwrap()

	for pairing in str(post).splitlines():
		if re.compile(r'.*\Wvs\W.*').match(pairing):
			players = list(map(str.strip, re.compile(r'vs\W').split(pairing)))
		
			# Format players
			player1 = BeautifulSoup(
				players[0], 'html.parser').get_text().strip() 
			player2 = BeautifulSoup(
				players[1], 'html.parser').get_text().strip()

			pairings[player1] = player2
			pairings[player2] = player1

			if players[0].startswith('<b>') or players[0].endswith('</b>'): 
				winners.append(player1)
				losers.append(player2)
			elif players[1].startswith('<b>') or players[1].endswith('</b>'):
				winners.append(player2)
				losers.append(player1)
		
	return {'pairings':pairings,
			'winners':winners,
			'losers':losers}

		# Extended matches
		
		# player -> tier -> round 1 -> win / loss / incomplete
		# round / wins
		# check which round
		# round 1


def upload_to_sheet(parsed_posts):
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
		'./creds.json', scopes=scope)

	file = gspread.authorize(credentials) # authenticate with Google
	sheet = file.open("Grand Slam VI")
	page = sheet.get_worksheet(6) # open sheet
	
	for i, post in enumerate(parsed_posts):
		page.update_cell(i + 1, 1, post['author'])
		page.update_cell(i + 1, 2, post['content'])
		page.update_cell(i+ 1, 3, post['timestamp'])
		# Change to single api call
	
def main():	
	# Main
	for tier in ('lc', 'ubers'):
		# Scrape open text
		posts = posts_from_thread(urls[tier][0])

		# Post author, post body, other
		parsed_posts = map(parse_post, posts)
		a = (list(parsed_posts))
	
		for winner in parse_pairings(a[0]['content'])['winners']:
			print(winner)
	#print(a)

	# Upload
	
	# Google sheets
	#upload_to_sheet(parsed_posts)




	
if __name__ == '__main__':
	main()





