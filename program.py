#!/usr/bin/python2.7
import os, piecash, yaml, time, math
from piecash import open_book, Transaction, Split, Account
from pprint import pprint

class account:
	amount = 0
	max = 0
	name = ""

	def percentage(self):
		if self.amount == 0 or self.max == 0:
			return "0%"
		return "{0:.0f}%".format((self.amount/self.max)*100)

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

		percent = int(self.percentage().rstrip("%"))

		if(self.amount < 1000):
			s += '\t'
		s += '['

		i = 0

		range_max = int(math.ceil(percent / 10.0)) 

		for x in range(0, range_max):
			s += '-'
			i += 1
		for x in range(i, 10):
			s += ' '
		s += ']'

		s += str(self.percentage())
		return s

class budget:
	amount = 0
	max = 0
	name = ""
	accounts = []

	def percentage(self):
		if self.amount == 0 or self.max == 0:
			return "0%"
		return "{0:.0f}%".format((self.amount/self.max)*100)

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
		s += "\n"
		s += str(self.percentage()) + "\n\n"
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


budget_essentials = budget(name = "Essentials", max = budget_file['essentials']['budget'])

budget_savings = budget(name = "Savings", max = budget_file['savings']['budget'])

budget_personal = budget(name = "Personal", max = budget_file['personal']['budget'])

budget_income = budget(name = "Income", max = budget_file['income']['budget'])

for a in budget_file['essentials']['accounts']:
	budget_essentials.accounts.append(account(name=a['name'], max = a['budget']))


for a in budget_file['savings']['accounts']:
	budget_savings.accounts.append(account(name=a['name'], max = a['budget']))

 # check for existance of to_account and from_account
book = piecash.open_book(book_path)

year = time.strftime('%Y')
month = time.strftime('%b')

print month, ' ', year
print
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

for a in book.accounts:
	if a.fullname.startswith("Expenses"):
		budget_file = checkBalance(book, a.fullname, year, month, budget_essentials, budget_savings, budget_personal)

print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

print 
print budget_essentials

print budget_personal

print budget_income

print budget_savings
