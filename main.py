#!/usr/bin/python
import os, piecash, yaml, time, datetime, math, sys, calendar
from piecash import open_book, Transaction, Split, Account
from pprint import pprint

class account:

    def __init__(self,name, budget):
        self.name = name
        self.budget = budget
        self.amount = 0


class monthly_budget:

    def __init__(self,name, budget_file):
        self.name = name
        self.essential_accounts = []
        self.saving_accounts = []
        self.essentials_budget = 0
        self.savings_budget = 0
        self.personal_budget = 0
        self.income_budget = 0
        self.essentials = 0
        self.savings = 0
        self.personal = 0
        self.income = 0

        for a in budget_file['essentials']['accounts']:
            self.essential_accounts.append(account(name = a['name'], budget = a['budget']))
            self.essentials_budget += a['budget']

        for a in budget_file['savings']['accounts']:
            self.saving_accounts.append(account(name = a['name'], budget = a['budget']))
            self.savings_budget += a['budget']

        self.personal_budget = budget_file['personal']['budget']
        self.income_budget = budget_file['income']['budget']

    def add_to_account(self, account,amount):
        if account.type == 'EXPENSE':
            is_essential = False
            for a in self.essential_accounts:
                if(a.name in account.fullname):
                    a.amount += amount
                    self.essentials += amount
                    is_essential = True
            if not is_essential:
                self.personal += amount
        if account.type == 'BANK':
            if('Savings' in account.fullname):
                self.savings += amount
            else:
                self.income += amount
        # elif account.type == 'CREDIT':
        #     print ('credit')
    
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
    
    def print_result(self):
        print()
        print ('Essentials', end='')
        print('\t', repr(float(self.essentials)).rjust(8), '/', repr(self.essentials_budget).rjust(4), end=' ')        
        print(self.get_percentage_bar(self.essentials, self.essentials_budget))

        print ('Personal', end='')
        print('\t', repr(float(self.personal)).rjust(8), '/', repr(self.personal_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.personal, self.personal_budget))

        print ('Income  ', end='')
        print('\t', repr(float(self.income)).rjust(8), '/', repr(self.income_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.income, self.income_budget))

        print ('Savings  ', end='')
        print('\t', repr(float(self.savings)).rjust(8), '/', repr(self.savings_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.savings, self.savings_budget))


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

# for current month, descending in reverse for the year
for current_month in range(today.month, 0, -1):
    
    # create monthly budget from settings file
    b = monthly_budget(name = calendar.month_name[current_month], budget_file = budget_file)

    # print looping month
    print(calendar.month_name[current_month], today.year)

    transactions = []

    # look at all transactions in reverse, retaining only this month
    for t in book.transactions[::-1]:
        if today.year == t.post_date.year and current_month == t.post_date.month:
            transactions.append(t)

    # sort transactions in reverse order by date
    transactions.sort(key=lambda t: t.post_date, reverse=True)

    for t in transactions:
        # only look at accounts being added into
        splitnum = t.splits[0].value < 0

        if t.post_date.month == today.month:
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


        # add transaction if matching looping month
        if t.post_date.month == current_month:
            b.add_to_account(t.splits[splitnum].account, t.splits[splitnum].value)
        
    # print monthly budget
    b.print_result()
    print()