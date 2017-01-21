#!/usr/bin/python2.7
import os, piecash, yaml, time, datetime, math, sys
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

	def output_without_bar(self):
		if max == 0:
			return ""
		s = self.name
		s += ' \t'
		if(len(s) <=5):
			s += '\t'
		if(len(s) <=12):
			s += '\t'

		s += str(self.amount) + ' '
		s += '\t'
		if(self.amount <= 1000):
			s += '\t'
		return s
		
	def __str__(self):
		s = self.output_without_bar()
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
		if(len(s)<=24):
			s += "\t"
		s += print_percentage_bar(self.amount,self.max)
		s += "\n\n"
		for a in self.accounts:
			if self.name == "Personal":
				s += '   ' + a.output_without_bar() + "\n"
			else:
				s += '   ' + str(a) + "\n"
		return s

def checkBalance(book, current_account, year, month, budget_essentials, budget_savings, budget_personal, budget_income):
	current_account = book.accounts(fullname=current_account)

	first = True
	
	for sp in reversed(current_account.splits):
		if sp.transaction.post_date.strftime('%Y') != year or sp.transaction.post_date.strftime('%b') != month :
			break; 
		if first:
			first = False
			print current_account.fullname

		print '  ', sp.value, '\t', 
		if(len(str(sp.value)) <= 3):
			print '\t',
		print sp.transaction.post_date.strftime('%b %d %Y'), 

		found = False

		for a in budget_essentials.accounts:
			if a.name in current_account.fullname:
				budget_essentials.amount += sp.value
				a.amount += sp.value
				found = True
				print '\tEssential', 
				break

		if not found:
			for a in budget_savings.accounts:
				if a.name in current_account.fullname:
					budget_savings.amount += sp.value
					a.amount += sp.value
					found = True
					print '\tSavings', 
					break
				
		if not found:
			if current_account.fullname.startswith("Assets") and "Checking" in current_account.fullname:
				if sp.value > 0:
					budget_income.amount += sp.value
					print '\tIncome\t',
				else: 
					print '\t------\t',
			elif current_account.name != "Credit Card"and not current_account.fullname.startswith("Assets"): 
				budget_personal.amount += sp.value
				
				account_exists = False
				for a in budget_personal.accounts:
					if a.name == current_account.name:
						a.amount += sp.value
						account_exists = True
						break
					
				if not account_exists:
					budget_personal.accounts.append(account(name=current_account.name, max = sp.value))
					budget_personal.accounts[-1].amount = sp.value
				
				print '\tPersonal', 

		print '\t', sp.transaction.description

	return budget_file

def printAccountBalances(book):
	
	print "{:%b %d %Y}".format(datetime.date.today()),
	print 'Balances:\n'
	checking = book.accounts(fullname="Assets:Current Assets:Checking Account")
	savings = book.accounts(fullname="Assets:Current Assets:Savings Account")
	credit_card = book.accounts(fullname="Liabilities:Credit Card")
	
	print 'Checking Account: \t',
	print checking.get_balance()
	
	print 'Savings Account: \t',
	print savings.get_balance()
	
	print 'Credit Card: \t\t',
	print credit_card.get_balance()
	
	print
	

settings_file = 'settings.yaml'
year = time.strftime('%Y')
month = time.strftime('%b')

if len(sys.argv) > 1:
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
	if a.fullname.startswith("Expenses") or a.fullname.startswith("Assets") or a.fullname.startswith("Liabilities:Credit Card"):
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

print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

printAccountBalances(book)