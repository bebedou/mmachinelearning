import requests
import re
from bs4 import BeautifulSoup
import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def num(s) :
	s = s[:-1]
	try:
		return int(s)
	except ValueError:
		return 0
def get_page_record (url) :
	content = []
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	tb = soup.find('table', class_='wikitable')
	if tb == None :
		return False
	#print (tb)
	for link in tb.find_all('td') :
			content.append(link.get_text('b'))
	if "Professional record breakdownb\n" in content :
			return True
	else :
			return False

def is_born(url):
	searched_word = "born"
	soup = BeautifulSoup(page.content, 'html.parser')
	results = soup.body.find_all(string=re.compile('.*{0}.*'.format(searched_word)), recursive=True)
	if results == None :
		return False
	if len(results) > 0 :
		return True
	else :
		return False
def filter_urls(urls_list) :
	filtered_list = []
	base_url= "https://en.wikipedia.org"
	for fighter_url in urls_list :
			url = base_url + fighter_url
			if get_page_record(url) == True :
				filtered_list.append(fighter_url)
				print (url)
	return filtered_list
                    
        
def get_fighter_record(fighter_url):
	url= "https://en.wikipedia.org"
	url = url + fighter_url
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	#print(page.status_code)
	content = []
	wins = []
	losses = []
	ret = []
	fighter_name = soup.find('title')
	fighter_name = fighter_name.get_text()
	fighter_name = fighter_name[:-12]
	ret.append(fighter_name)
	tb = soup.find('table', class_='wikitable')
	for link in tb.find_all('td') :
			content.append(link.get_text('b'))
			#print (link.get_text('b'))
	try:
		ret.append(num(content[content.index('By knockoutb\n')+1]))
	except ValueError:
		ret.append(0)
	try :
		ret.append(num(content[content.index('By knockoutb\n')+2]))
	except ValueError:
		ret.append(0)
	try :
		ret.append(num(content[content.index('By submissionb\n')+1]))
	except ValueError:
		ret.append(0)
	try :
		ret.append(num(content[content.index('By submissionb\n')+2]))
	except ValueError:
		ret.append(0)
	try :
		ret.append(num(content[content.index('By decisionb\n')+1]))
	except ValueError:
		ret.append(0)
	try :
		ret.append(num(content[content.index('By decisionb\n')+2]))
	except ValueError:
		ret.append(0)

	return ret
	
def read_urls_from_file(fname) :
	with open(fname) as f:
		content = f.read().splitlines()
	return content
	
def construct_url_file (filename) :
	f= open(filename,"w+")
	fighters_url_list = []
	url = "https://en.wikipedia.org/wiki/List_of_male_mixed_martial_artists"
	page = requests.get(url)
	print(page.status_code)
	soup = BeautifulSoup(page.content, 'html.parser')

	for link in soup.findAll('a', attrs={'href': re.compile("^/wiki")}):
		res = link.get('href')
		fighters_url_list.append(res)
	filtered = filter_urls(fighters_url_list)
	print (len(filtered))
	for i in filtered :
		f.write(i+'\n')

def write_db_to_csv (list) :
	with open("fighters_db_2.csv", mode='w') as db:
		db_writer = csv.writer(db, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		db_writer.writerow(['Fighter name', 'Ko wins', 'Ko losses', 'Submission wins', 'Submission losses', 'Decision wins', 'Decision losses'])
		for fighter in list:
			tmp = get_fighter_record(fighter)
			try :				
				db_writer.writerow(tmp)
			except UnicodeEncodeError:
				tmp[0] = "Unamed"
				db_writer.writerow(tmp)
def read_db_from_csv(filename):
	f_d = pd.read_csv(filename, sep=",", encoding = "ISO-8859-1")
	#filter Travis Fulton and data aberrantes
	f_d = f_d.drop(f_d[f_d["Ko wins"] > 80].index)
	return f_d
def select_training_data (fd):
	#Select a sample of 20 fighters with known styles
	#Select Adesanya, Mcgregor, Khabib, Kattar, Maia, Manhoef, Makhachev, Mcdonald, Anthony Johnson, Demetrious Johnson, 
	# Mark Hunt, Ishii, Holloway, Dan Henderson, Benson Henderson, Uriah Hall, Royce Gracie, Tony Ferguson, Paul Felder
	training_data = fd.loc[fd["Fighter name"].isin(["Israel Adesanya","Conor McGregor",  "Royce Gracie", "Khabib Nurmagomedov", "Calvin Kattar", "Demian Maia", 
	"Melvin Manhoef", "Islam Makhachev", "Rory MacDonald (fighter)", "Anthony Johnson (fighter)", "Demetrious Johnson", "Mark Hunt", "Satoshi Ishii", "Max Holloway", "Dan Henderson",
	"Benson Henderson", "Uriah Hall", "Royce Gracie", "Tony Ferguson", "Paul Felder"])]
	return training_data
def select_test_data (fd):
	pass
def select_validation_data (fd):
	pass
	
def main() :
	filename = "fighters_db_2.csv"
	#content = read_urls_from_file(filename)
	#write_db_to_csv(content)
	f_d = read_db_from_csv(filename)
	#0 = MMArtist, 1 = Striker, 2 = Wrestler, 3 = Grappler
	f_d["fighter_type"] = 0
	print (f_d.dtypes)
	training_data = select_training_data(f_d)
	print (training_data)
	validation_data = select_validation_data(f_d)
	test_data = select_test_data(f_d)
main()