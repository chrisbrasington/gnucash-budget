#!/usr/bin/python2.7
import os, piecash, yaml, time, math, sys
from piecash import open_book, Transaction, Split, Account
from pprint import pprint

def print_percentage_bar(amount, max):
	str = "0%"
	range_max = 0
	if amount != 0 and max != 0:
		str = "{0:.0f}%".format((amount/max)*100)
		range_max = int(math.ceil((amount/max)*100 / 10)) 
	s = '['
	i = 0
	for x in range(0, range_max):
		s += '*'
		i += 1
	for x in range(i, 10):
		s += ' '
	s += ']'
	s += str
	return s

class account:
	amount = 0
	max = 0
	name = ""

	def __init__(self, name):
		self.name = name

	def __init__(self, name, max):
		self.name = name
		self.max = max

	def __str__(self):
		s = self.name
		if(len(s) <=3):
			s += ' \t'
		if(len(s) <=12):
			s += ' \t'

		s += str(self.amount) + ' '
		s += '\t'

		s += print_percentage_bar(self.amount, self.max)
		return s

class budget:
	amount = 0
	max = 0
	name = ""
	accounts = []

	def __init__(self, name):
		self.name = name
		self.accounts = []

	def __init__(self, name, max):
		self.name = name
		self.max = max
		self.accounts = []

	def __str__(self):
		s = self.name + ' '+ str(self.amount) 
		s += " / " + str(self.max)
		s += "\t"
		s += print_percentage_bar(self.amount,self.max) + "\n"
		for a in self.accounts:
			s += '   ' + str(a) + "\n"
		return s

def checkBalance(book, account, year, month, budget_essentials, budget_savings, budget_personal, budget_income):
	account = book.accounts(fullname=account)

	first = True
	
	for sp in reversed(account.splits):
		if sp.transaction.post_date.strftime('%Y') != year or sp.transaction.post_date.strftime('%b') != month :
			break; 
		if first:
			first = False
			print account.fullname

		print '  ', sp.value, '\t', 
		if(len(str(sp.value)) <= 3):
			print '\t',
		print sp.transaction.post_date.strftime('%b %d %Y'), 

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
				
		if not found:
			if account.fullname.startswith("Assets") and "Checking" in account.fullname:
				if sp.value > 0:
					budget_income.amount += sp.value
				print '\tIncome\t', 
			else: 
				budget_personal.amount += sp.value
				print '\tPersonal', 

		print '\t', sp.transaction.description

	return budget_file

settings_file = 'settings.yaml'
year = time.strftime('%Y')
month = time.strftime('%b')

if sys.argv > 0:
	print 'DEMO MODE'
	settings_file = 'settings_sample.yaml'
	year = '2017'
	month = 'Jan'


with open(settings_file) as ymlfile:
	budget_file = yaml.load(ymlfile)
	
book_path = budget_file['file']

budget_essentials = budget(name = "Essentials", max = budget_file['essentials']['budget'])

budget_savings = budget(name = "Savings", max = budget_file['savings']['budget'])

budget_personal = budget(name = "Personal", max = budget_file['personal']['budget'])

budget_income = budget(name = "Income", max = budget_file['income']['budget'])

for a in budget_file['essentials']['accounts']:
	budget_essentials.accounts.append(account(name=a['name'], max = a['budget']))


for a in budget_file['savings']['accounts']:
	budget_savings.accounts.append(account(name=a['name'], max = a['budget']))

# check for existance of to_account and from_account
try: 
	book = piecash.open_book(book_path, readonly=True, open_if_lock=True)
except:
	print 'Unable to open database.'
	exit()

print '\nBudget: ', month, ' ', year
print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

accounts = []

for a in book.accounts:
	if a.fullname.startswith("Expenses") or a.fullname.startswith("Assets"):
		accounts.append(a.fullname)
#	if a.fullname.startswith("Assets"):
#		budget_file = checkBalance(book, a.fullname, year, month, budget_essentials, budget_savings, budget_personal, budget_income)

accounts.sort()

for a in accounts:
	budget_file = checkBalance(book, a, year, month, budget_essentials, budget_savings, budget_personal, budget_income)

print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

print 
print budget_essentials

print budget_personal

print budget_income

print budget_savings
