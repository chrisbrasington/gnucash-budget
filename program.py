#!/usr/bin/python2.7
import os, piecash, yaml, time
from piecash import open_book, Transaction, Split, Account
#from piecash.core.factories import create_currency_from_ISO

def checkBalance(book, account, year, month):
	account = book.accounts(fullname=account)

	first = True
	
	for sp in reversed(account.splits):
		if sp.transaction.enter_date.strftime('%Y') != year or sp.transaction.enter_date.strftime('%b') != month :
			break; 
		if first:
			first = False
			print account.name
			
		print '  ', sp.transaction.description, '\t', sp.value, '\t', sp.transaction.enter_date.strftime('%b %d %Y')

settings_file = 'settings.yaml'
with open(settings_file) as ymlfile:
	settings = yaml.load(ymlfile)
	
book_path = settings['file']

 # check for existance of to_account and from_account
book = piecash.open_book(book_path)

year = time.strftime('%Y')
month = time.strftime('%b')

print month, ' ', year

for a in book.accounts:
	if a.fullname.startswith("Expenses"):
		checkBalance(book, a.fullname, year, month)
	
