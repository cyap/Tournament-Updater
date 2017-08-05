from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

####
urls = {
	'lc':[
		'http://www.smogon.com/forums/threads/the-lc-open-vi-round-1.3610246/'
	]
}



####

def posts_from_thread(url):
	posts = []
	# Calculate page of last post
	first_page = BeautifulSoup(urlopen(url).read().decode()
				, "html.parser")
	try:
		end = int(str(first_page.find(class_="pageNavHeader"))
			.split("of ")[1].split("<")[0]) * 25
	except:
	# only one page
		end = 25

	# Iterate through all pages
	for i in range(1, int((end-1) / 25) + 2):
		page_num = "page-" + str(i)
		try:
			#page = (urlopen(url.strip() + page_num)
			#		.read().decode().split("</article>")[:-1])
			#posts += page
			page = urlopen(url.strip() + page_num).read().decode()
			posts += BeautifulSoup(page, 'html.parser').find_all(
				lambda x: x.name == 'li' and x.has_attr('data-author'))
			
		except:
			pass
			#traceback.print_exc()
	return posts
	
def parse_post(post):
	# Author
	author = post['data-author']
	#author = HTML.find(lambda x: x.has_attr('data-author'))['data-author']
	#author = post.find('li')['data-author']
	
	# Body
	HTMLcontent = post.find('blockquote', 
		{'class':'messageText ugc baseHtml'}).decode_contents(formatter='html')
	raw_content = BeautifulSoup(HTMLcontent).get_text()
	
	# Timestamp
	try:
		timestamp = (post.find('abbr', {'class':'DateTime'})
			.decode_contents(formatter='html'))
	except:
		timestamp = None
	return {'author':author, 'content':raw_content, 'timestamp':timestamp}
	
def upload_to_sheet(parsed_posts):
	scope = ['https://spreadsheets.google.com/feeds']
	credentials =ServiceAccountCredentials.from_json_keyfile_name(
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
	
	# Scrape open text
	posts = posts_from_thread(urls['lc'][0])

	# Post author, post body, other
	parsed_posts = map(parse_post, posts)

	# Upload
	
	# Google sheets
	upload_to_sheet(parsed_posts)




	
if __name__ == '__main__':
	main()





