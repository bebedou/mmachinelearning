import requests
import re
from bs4 import BeautifulSoup
import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset
from tensorflow import keras
import glob
import math
import os
from datetime import datetime

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
	# If values are not available from the recap table on Wikipedia page, replace them by 0
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

	# Find all links containing Wiki in it
	for link in soup.findAll('a', attrs={'href': re.compile("^/wiki")}):
		res = link.get('href')
		fighters_url_list.append(res)
	# Filter URLs to keep only the useful ones i.e Ones containing Fighter record (excluding also Counrty link, organisation link etc)
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
	#filter Travis Fulton and wrong data
	f_d = f_d.drop(f_d[f_d["Ko wins"] > 80].index)
	return f_d
def select_training_data (fd):

	#Select a sample of 20 fighters with known styles
	training_data_names = ["Israel Adesanya","Conor McGregor",  "Royce Gracie", "Khabib Nurmagomedov", "Calvin Kattar", "Demian Maia", 
	"Melvin Manhoef", "Islam Makhachev", "Rory MacDonald (fighter)", "Anthony Johnson (fighter)", "Demetrious Johnson", "Mark Hunt", "Satoshi Ishii", "Max Holloway", "Dan Henderson",
	"Benson Henderson", "Uriah Hall", "Royce Gracie", "Tony Ferguson", "Paul Felder",  "Gunnar Nelson (fighter)", "Rousimar Palhares", "Diego Sanchez" ]
	
	training_data_striker = fd.loc[fd["Fighter name"].isin(["Israel Adesanya","Conor McGregor",  "Calvin Kattar",
	"Melvin Manhoef",  "Anthony Johnson (fighter)",  "Mark Hunt",  "Max Holloway", "Uriah Hall", "Paul Felder"])]
	training_data_mmartist = fd.loc[fd["Fighter name"].isin([ "Rory MacDonald (fighter)",  "Demetrious Johnson", "Tony Ferguson", "Diego Sanchez"])]
	training_data_grappler = fd.loc[fd["Fighter name"].isin([ "Royce Gracie",  "Demian Maia", "Gunnar Nelson (fighter)", "Rousimar Palhares", "Satoshi Ishii"])]
	training_data_wrestler = fd.loc[fd["Fighter name"].isin([ "Khabib Nurmagomedov", "Islam Makhachev","Dan Henderson","Benson Henderson"])]
	training_data_mmartist["fighter_type"] = 0
	training_data_striker["fighter_type"] = 1
	training_data_wrestler["fighter_type"] = 2
	training_data_grappler["fighter_type"] = 3
	training_data = pd.concat([pd.concat([training_data_mmartist, training_data_striker]), pd.concat([training_data_wrestler, training_data_grappler])])
	training_data = training_data.reindex(np.random.permutation(training_data.index))
	return training_data
def select_test_data (fd):

	test_data_names = [
	"Thiago Santos (fighter)", "Wanderlei Silva", "Khalil Rountree Jr.",
	"Anthony Smith (mixed martial artist)", "Ovince Saint Preux", "Marlon Vera (fighter)"
	, "Cláudio Silva", "Kazushi Sakuraba", "Paul Sass", "Chael Sonnen", "Cain Velasquez", "Phil Davis (fighter)"]
	
	test_data_striker = fd.loc[fd["Fighter name"].isin(["Thiago Santos (fighter)", "Wanderlei Silva", "Khalil Rountree Jr."
	])]
	test_data_mmartist = fd.loc[fd["Fighter name"].isin(["Anthony Smith (mixed martial artist)", "Ovince Saint Preux", "Marlon Vera (fighter)" ])]
	test_data_grappler = fd.loc[fd["Fighter name"].isin(["Cláudio Silva", "Kazushi Sakuraba", "Paul Sass" ])]
	test_data_wrestler = fd.loc[fd["Fighter name"].isin(["Chael Sonnen", "Cain Velasquez", "Phil Davis (fighter)"  ])]
	test_data_mmartist["fighter_type"] = 0
	test_data_striker["fighter_type"] = 1
	test_data_wrestler["fighter_type"] = 2
	test_data_grappler["fighter_type"] = 3
	test_data = pd.concat([pd.concat([test_data_mmartist, test_data_striker]), pd.concat([test_data_wrestler, test_data_grappler])])
	test_data = test_data.reindex(np.random.permutation(test_data.index))
	return test_data
def select_validation_data (fd):

	validation_data_names = [ "José Aldo", "Thomas Almeida", "Edson Barboza", "Bryan Barberena", "Vitor Belfort", "Michael Bisping", "Eddie Alvarez", "Joseph Benavidez", "Donald Cerrone", "David Branch (fighter)", 
	"Gilbert Burns (fighter)", "Antônio Carlos Júnior", "Josh Barnett", "Tony Bonello", "Phil De Fries", "Corey Anderson (fighter)", "Curtis Blaydes", "Derek Brunson" , "Ryan Bader", "Darrion Caldwell", "Henry Cejudo" , "Randy Couture", "Colby Covington" ]
	
	validation_data_striker = fd.loc[fd["Fighter name"].isin(["José Aldo", "Thomas Almeida", "Edson Barboza", "Bryan Barberena", "Vitor Belfort", "Michael Bisping", "T.J. Dillashaw" ])]
	validation_data_mmartist = fd.loc[fd["Fighter name"].isin(["Eddie Alvarez", "Joseph Benavidez", "Donald Cerrone" ])]
	validation_data_grappler = fd.loc[fd["Fighter name"].isin(["David Branch (fighter)", "Gilbert Burns (fighter)", "Antônio Carlos Júnior", "Josh Barnett", "Tony Bonello", "Phil De Fries", "Nate Diaz",  ])]
	validation_data_wrestler = fd.loc[fd["Fighter name"].isin(["Corey Anderson (fighter)", "Curtis Blaydes", "Derek Brunson" , "Ryan Bader", "Darrion Caldwell", "Henry Cejudo" , "Randy Couture", "Colby Covington"])]
	validation_data_mmartist["fighter_type"] = 0
	validation_data_striker["fighter_type"] = 1
	validation_data_wrestler["fighter_type"] = 2
	validation_data_grappler["fighter_type"] = 3
	validation_data = pd.concat([pd.concat([validation_data_mmartist, validation_data_striker]), pd.concat([validation_data_wrestler, validation_data_grappler])])
	validation_data = validation_data.reindex(np.random.permutation(validation_data.index))
	return validation_data
		


def get_compiled_model():
	model = tf.keras.Sequential([
	tf.keras.layers.Dense(6, activation='sigmoid'),
	tf.keras.layers.Dense(8, activation='sigmoid'),
	tf.keras.layers.Dense(8, activation='sigmoid'),
	tf.keras.layers.Dense(4, activation='softmax')
	])
	opt = keras.optimizers.Adam(lr=0.007)
	model.compile(optimizer=opt,
				loss='sparse_categorical_crossentropy',
				metrics=['accuracy'])
	return model
def classifier_keras (train_dataset, train_labels, test_dataset, test_labels, fighters_data):
	res = []
	class_names = ["MMArtist","Striker", "Wrestler", " Grappler"]
	model = get_compiled_model()
	model.fit(train_dataset, train_labels, epochs=150, batch_size = 5, shuffle = True)
	#test_loss, test_acc = model.evaluate(test_dataset,  test_labels, verbose=2)
	#print('\nTest accuracy:', test_acc)
	
	predictions = model.predict(fighters_data)
	
	# Chose most likely class predicted using argmax
	for i in predictions :
		res.append(np.argmax(i))
	
	# Plot predicted values in a histogram
	plt.hist(res)
	plt.xticks(range(4), class_names, rotation = 45)
	plt.show()
	
	# Return predicted classes
	return res
	
def get_win_pct(f_d):
	res = []
	for index, row in f_d.iterrows():
		try:
			res.append((row["Ko wins"]+ row["Submission wins"] + row ["Decision wins"])/
			(row["Ko losses"]+ row["Submission losses"] + row ["Decision losses"]+row["Ko wins"]+ row["Submission wins"] + row ["Decision wins"]))
		except ValueError:
			res.append(100)
		except ZeroDivisionError :
			res.append(100)
		
	return res
def write_results_to_files(df):
	now = datetime.now()
	dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
	filename_csv = "Test_NN_MMA_Class_" + dt_string + ".csv"
	filename_xlsx = "Test_NN_MMA_Class_" + dt_string + ".xlsx"
	df.to_csv(filename_csv)
	df.to_excel(filename_xlsx)
	return True
def format_classes(list, class_names):	
	ret = []
	for i in list:
		ret.append(class_names[i])
	return ret
	
def main() :

	"""
		Main function calling different functions to perform the data extraction/exploration
		Once data has been extracted or read from CSV File, classifier_keras function performs the learning on training_features
		After the learning has been performed, the function predict the class of each fighter computing the proper columns of the dataframe
		
	"""
	filename = "fighters_db_2.csv"
	
	#0 = MMArtist, 1 = Striker, 2 = Wrestler, 3 = Grappler
	class_names = ["MMArtist","Striker", "Wrestler", " Grappler"]
	
	"""
		The next two lines can scrape URLs from recap page on Wkipedia to create a file listing all of them
		Then it reads the URLs from the file and extract Fighter names + records and store them as an array in a .csv file
	"""
	# construct_url_file(filename)
	#content = read_urls_from_file(filename)
	#write_db_to_csv(content)
	
	# Read Fighters data from csv and construct dataframe f_d
	f_d = read_db_from_csv(filename)
	# Set all classes to 0 just for default value purpose
	f_d["fighter_type"] = 0

	# Hand pick training dataset with no particular policy, just well known fighters and their classes
	# Training dataset is merged with test and validation because it was not big enough to provide proper training, 
	# They were separated
	training_data = select_training_data(f_d)	
	training_targets = training_data["fighter_type"]
	training_features = training_data[["Ko wins", "Ko losses", "Submission wins", "Submission losses", "Decision wins", "Decision losses"]]
	
	validation_data = select_validation_data(f_d)
	validation_targets = validation_data["fighter_type"]
	validation_features = validation_data[["Ko wins", "Ko losses", "Submission wins", "Submission losses", "Decision wins", "Decision losses"]]
	
	training_targets = pd.concat([training_targets, validation_targets])	
	training_features = pd.concat([training_features, validation_features])
	test_data = select_test_data(f_d)

	test_features = test_data[["Ko wins", "Ko losses", "Submission wins", "Submission losses", "Decision wins", "Decision losses"]]
	test_targets = test_data["fighter_type"]
	f_d = f_d.reindex(np.random.permutation(f_d.index))
	fighters_data = f_d[["Ko wins", "Ko losses", "Submission wins", "Submission losses", "Decision wins", "Decision losses"]]
	
	# Expand training dataset 
	training_targets = pd.concat([training_targets, test_targets])	
	training_features = pd.concat([training_features, test_features])
	
	# Predict
	f_classes = classifier_keras(training_features.to_numpy(), training_targets.to_numpy(), test_features.to_numpy(), test_targets.to_numpy(), fighters_data.to_numpy() )
	# Replace predicted class value by proper name
	f_classes = format_classes (f_classes, class_names)
	f_d["fighter_type"] = f_classes
	write_results_to_files(f_d)

main()