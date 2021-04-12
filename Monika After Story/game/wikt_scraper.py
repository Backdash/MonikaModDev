import urllib.request as request
from bs4 import BeautifulSoup
import json

'''
Note: this is just a utility for sifting, will be deleted when it's done

What it do:
loads word dictionary
gets letter input
cycles through all words in the letter's list
	gets wiktionary content for word
	checks for english subsection
	checks for flags
	if page 404s, has no english section, or has flags in it, write into the manual check file

also reconstructs the list without 404s in a separate file'''

def mancheck(check_file,word,reason):
	"""
	IN:
		check_file - file in write mode
		word - string, word to append
		reason - string, reason for appending word

	Appends word and reason to check_file
	"""
	line = word + ' ' + reason
	print(line)
	check_file.write(line+'\n')

def getpage(word):
	"""
	IN:
		word - string, the word to get the page for

	Returns a html thing if corresponding page exists on wiktionary, 0 otherwise
	"""
	try:
		page = request.urlopen('https://en.wiktionary.org/wiki/'+ word)
		return page
	except:
		#if 404 try capitalized
		try:
			page = request.urlopen('https://en.wiktionary.org/wiki/'+ word.title())
			return page
		except:
			# if 404 again, return 0
			return 0


with open("shiritori_dictionary_full.json") as orig:
	dict_orig = json.load(orig)

prompt = "gib letter\n"
letter = input(prompt)

try:
	word_list = dict_orig[letter]
except NameError:
	print("no such letter")
except:
	print("this is not supposed to happen")
else:
	flags = [
		'<span class="mw-headline" id="Proper_noun">',
		'Template:abbreviation_of',
		'Template:alternative_spelling_of',
		'Template:comparative_of',
		'Template:contraction_of',
		'Template:misspelling_of',
		'Template:plural_of',
		'Template:superlative_of'
		]
	check_file = open('man_check_file_'+letter+'.txt','w')
	de404_file = open('de404_'+letter+'.txt','w')

	for word in word_list:
		content = getpage(word)
		if content == 0:
			mancheck(check_file = check_file, word = word, reason = "404")
		else:
			de404_file.write('\t\t"'+ word + '",\n')
			soup = BeautifulSoup(content.read(),'html.parser').__str__()
			if ('<span class="mw-headline" id="English">' not in soup):
				# no english section
				mancheck(check_file = check_file, word = word, reason = "Eng")
			else:
				for flag in flags:
					# check for flags
					if (flag in soup):
						mancheck(check_file = check_file, word = word, reason = "Flag " + flag)
						break

check_file.close()
de404_file.close()
