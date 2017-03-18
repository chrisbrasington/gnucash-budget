#!/usr/bin/python
import os, piecash, yaml, time, datetime, math, sys, calendar
from piecash import open_book, Transaction, Split, Account
from pprint import pprint

# simple account class
class account:

    def __init__(self,name, budget, amount):
        self.name = name
        self.budget = budget
        self.amount = amount
        # self.transactions = []

    # account summary printout 
    def __str__(self):
        s = '  ' + repr(self.name).strip("'").ljust(24)
        s += str(self.amount)
        return s

# monthly budget aggregation 
# build from settings file
class monthly_budget:

    def __init__(self,name, budget_file):
        self.name = name
        self.essential_accounts = []
        self.personal_accounts = []
        self.saving_accounts = []
        self.income_accounts = []
        self.essentials_budget = 0
        self.savings_budget = 0
        self.personal_budget = 0
        self.essentials = 0
        self.income_budget = 0
        self.savings = 0
        self.personal = 0
        self.income = 0

        # keep all monthly transactions disassociated from accounts
        self.transactions = []

        # add all essential accounts from file
        # add essential budget
        for a in budget_file['essentials']['accounts']:
            self.essential_accounts.append(account(name = a['name'], budget = a['budget'], amount = 0))
            self.essentials_budget += a['budget']

        # add all savings accoungs
        # add savings budget
        for a in budget_file['savings']['accounts']:
            self.saving_accounts.append(account(name = a['name'], budget = a['budget'], amount = 0))
            self.savings_budget += a['budget']

        # add personal budget (implied for all other non-essential expense accounts)
        self.personal_budget = budget_file['personal']['budget']

        # add income budget
        self.income_budget = budget_file['income']['budget']

    # add transaction to associated account
    def add_to_account(self, current_account, amount):
        # found expense account
        if current_account.type == 'EXPENSE':
            # check if essential expense account
            is_essential = False
            for a in self.essential_accounts:
                # add to essential account
                if(a.name in current_account.fullname):
                    a.amount += amount
                    self.essentials += amount
                    is_essential = True
            # not essential, is personal account
            if not is_essential:
                self.personal += amount
                # search for personal account
                found = False
                for a in self.personal_accounts:
                    # add to found personal account
                    if a.name == current_account.name:
                        found = True
                        a.amount += amount
                # add to new personal account
                if not found:
                    self.personal_accounts.append(account(name = current_account.name, budget = 0, amount = amount))
               
        # found bank (deposit)
        if current_account.type == 'BANK':
            # add to savings
            if('Savings' in current_account.fullname):
                self.savings += amount
            else:
                # found income
                self.income += amount
                found = False
                # found income account
                for a in self.income_accounts:
                    if a.name == current_account.name:
                        found = True
                        a.amount += amount
                # add to new income account
                if not found:
                    self.income_accounts.append(account(name = current_account.name, budget = 0, amount = amount))

        # elif current_account.type == 'CREDIT':
        #     print ('credit')
    
    # get percentage bar
    def get_percentage_bar(self, amount, max):
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

    # print account summary
    def print_accounts_summary(self, accounts):
        print()
        for a in accounts:
            print(a)

    # print transactions from most recent descending
    def print_transactions_desc(self):
        for t in self.transactions:
             
            # transaction amount
            print (repr(float(t.splits[splitnum].value)).rjust(10), ' ', end='')

            # transaction date
            print (repr(t.post_date.strftime("%m/%d/%Y")).rjust(10).strip("'"), ' ', end='')

            # transaction account type
            print (repr(t.splits[splitnum].account.type).strip("'").ljust(7), ' ', end='')

            # transaction account name
            print(repr(t.splits[splitnum].account.name).strip("'").ljust(20), end=' ')

            # transaction description
            print(t.description)
    
    # print full month's budget summary
    def print_summary(self):
        
        # print essential account summary
        print()
        print ('Essentials', end='')
        print('\t', repr(float(self.essentials)).rjust(8), '/', repr(self.essentials_budget).rjust(4), end=' ')        
        print(self.get_percentage_bar(self.essentials, self.essentials_budget), end = ' ')

        # print individual accounts in essentials (ordered by configuration file)
        self.print_accounts_summary(self.essential_accounts)

        # print personal accounts
        print()
        print ('Personal', end='')
        print('\t', repr(float(self.personal)).rjust(8), '/', repr(self.personal_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.personal, self.personal_budget), end = ' ')

        # sort personal accounts alphabetically
        self.personal_accounts.sort(key=lambda a: a.name)

        # print individaul accounts in personal
        self.print_accounts_summary(self.personal_accounts)

        # print income summary
        print()
        print ('Income  ', end='')
        print('\t', repr(float(self.income)).rjust(8), '/', repr(self.income_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.income, self.income_budget))

        # print savings summary
        print ('Savings  ', end='')
        print('\t', repr(float(self.savings)).rjust(8), '/', repr(self.savings_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.savings, self.savings_budget))

# print current book account balances
def printAccountBalances(book):
 	
    print()
    print ('Balances:', end=' ')
    print ("({:%b %d %Y})".format(datetime.date.today()))
    checking = book.accounts(fullname="Assets:Current Assets:Checking Account")
    savings = book.accounts(fullname="Assets:Current Assets:Savings Account")
    credit_card = book.accounts(fullname="Liabilities:Credit Card")
    
    print (repr('  Checking Account ').strip("'").ljust(26), end='')
    print (checking.get_balance())
 	
    print (repr('  Savings Account ').strip("'").ljust(26), end = '')
    print (savings.get_balance())
 	
    print (repr('  Credit Card ').strip("'").ljust(26), end = '')
    print (credit_card.get_balance())

# today
today = datetime.date.today()

# read settings
settings_file = 'settings.yaml'
with open(settings_file) as ymlfile:
	budget_file = yaml.load(ymlfile)

# book file path
book_path = budget_file['file']

# read book
try:
	book = piecash.open_book(book_path, readonly=True, open_if_lock=True)
except:
	print ('Unable to open database.')
	exit()

year = []

# command line parameter to print full year
print_full_year = False
if len(sys.argv[1:]) > 0 and str(sys.argv[1:][0]) == 'year':
    print_full_year = True

# for current month, descending in reverse for the year
for current_month in range(today.month, 0, -1):
    
    # create monthly budget from settings file
    b = monthly_budget(name = calendar.month_name[current_month], budget_file = budget_file)

    # print looping month
    date_str = str(calendar.month_name[current_month]) + ' ' + str(today.year)

    print(repr(date_str).strip("'").ljust(10), end = ' ')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # look at all transactions in reverse, retaining only this month
    for t in book.transactions[::-1]:
        if today.year == t.post_date.year and current_month == t.post_date.month:
            b.transactions.append(t)

    # sort transactions in reverse order by date
    b.transactions.sort(key=lambda t: t.post_date, reverse=True)

    for t in b.transactions:
        # only look at accounts being added into
        splitnum = t.splits[0].value < 0

        # add transaction if matching looping month
        if t.post_date.month == current_month:
            b.add_to_account(t.splits[splitnum].account, t.splits[splitnum].value)

    # print monthly transactions descending
    if t.post_date.month == today.month:
        b.print_transactions_desc()    

        # print book account balances for current month only
        printAccountBalances(book)

    # print monthly budget
    b.print_summary()
    print()

    # stop at current month or keep going
    if not print_full_year:
        break