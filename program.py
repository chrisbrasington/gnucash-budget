#!/usr/bin/python2.7
import os, piecash, yaml, time
from piecash import open_book, Transaction, Split, Account
#from piecash.core.factories import create_currency_from_ISO
from pprint import pprint

class account:
	name = ""
	amount = 0
	max = 0

	def __init__(self, name):
		self.name = name

	def __str__(self):
		s = self.name + ' ' + str(self.amount)
		return s

class budget:
	amount = 0
	max = 0
	name = ""
	accounts = []

	def __init__(self, name):
		self.name = name
		self.accounts = []

	def __str__(self):
		s = self.name + ' '+ str(self.amount) + "\n"
		for a in self.accounts:
			s += '   ' + str(a) + "\n"
		return s




def checkBalance(book, account, year, month, budget_essentials, budget_savings, budget_personal):
	account = book.accounts(fullname=account)

	first = True
	
	for sp in reversed(account.splits):
		if sp.transaction.enter_date.strftime('%Y') != year or sp.transaction.enter_date.strftime('%b') != month :
			break; 
		if first:
			first = False
			print account.fullname

		print '  ', sp.value, '\t', sp.transaction.enter_date.strftime('%b %d %Y'), 

		found = False

		for a in budget_essentials.accounts:
			if a.name in account.fullname:
				budget_essentials.amount += sp.value
				a.amount += sp.value
				found = True
				print '\tEssential', 
				break

		if not found:
			for a in budget_savings.accounts:
				if a.name in account.fullname:
					budget_savings.amount += sp.value
					a.amount += sp.value
					found = True
					print '\tSavings', 
					break

		# for a in budget_file['essentials']['accounts'].split(','):
		# 	if a.strip() in account.fullname:
		# 		budget_file['essentials']['value'] += sp.value
		# 		print '\tEssential', 
		# 		found = True
		# 		break

		# if not found:
		# 	for a in budget_file['savings']['accounts'].split(','):
		# 		if a.strip() in account.name:
		# 			budget_file['savings']['value'] += sp.value
		# 			print '\tSavings', 
		# 			found = False
		# 			break

		# if not found:
		# 	budget_file['personal']['value'] += sp.value
		# 	print '\tPersonal', 
		# 	found = True
		
		if not found:
			budget_personal.amount += sp.value
			print '\tPersonal', 
			found = True

		print '\t', sp.transaction.description

	return budget_file



settings_file = 'settings.yaml'
with open(settings_file) as ymlfile:
	budget_file = yaml.load(ymlfile)
	
book_path = budget_file['file']


budget_essentials = budget(name = "Essentials")
budget_savings = budget(name = "Savings")
budget_personal = budget(name = "Personal")

for a in budget_file['essentials']['accounts'].split(','):
	a = a.strip()
	budget_essentials.accounts.append(account(name=a))

for a in budget_file['savings']['accounts'].split(','):
	a = a.strip()
	budget_savings.accounts.append(account(name=a))

 # check for existance of to_account and from_account
book = piecash.open_book(book_path)

year = time.strftime('%Y')
month = time.strftime('%b')

print month, ' ', year
print

for a in book.accounts:
	if a.fullname.startswith("Expenses"):
		budget_file = checkBalance(book, a.fullname, year, month, budget_essentials, budget_savings, budget_personal)

print 
print budget_essentials

print budget_savings

print budget_personal



# print 'savings:'
# print budget_file['savings']
# print 'personal:'
# print budget_file['personal']

# a = "Groceries"
# b = "Expenses:Groceries:H-Mart"

# print a in b
