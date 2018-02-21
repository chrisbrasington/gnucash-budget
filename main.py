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

    def __init__(self,name, month, budget_file):
        self.name = name
        self.month = month
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
        self.hourly_rate = 0
        self.debt_name = ''
        self.debt_amount = 0
        self.debt_budget = 0

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
        # assume 2 paychecks in a month (sometimes it's 3! might want to get smarter here..)
        self.income_budget = budget_file['income']['paycheck']*2

        # hourly rate is gross income / hours worked of paycheck (2 weeks)
        self.hourly_rate = budget_file['income']['gross']/80

        try:
            self.debt_name = budget_file['debt']['name']
            self.debt_budget = budget_file['debt']['budget'] + budget_file['debt']['help']
        except: 
            pass

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
        if current_account.type == 'BANK' or current_account.type == 'INCOME':
            # add to savings
            if 'Savings' in current_account.fullname:
                self.savings += amount
                self.saving_accounts.append(account(name = current_account.name, budget = 0, amount = amount))
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

        #if current_account.type == 'CREDIT':
        #    print(current_account)
        #    print(amount)
    
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
                    
            # only look at accounts being added into
            splitnum = t.splits[0].value < 0
             
            # transaction amount
            print (repr(float(t.splits[splitnum].value)).rjust(10), ' ', end='')

            # transaction date
            print (repr(t.post_date.strftime("%m/%d/%Y")).rjust(10).strip("'"), ' ', end='')

            # transaction account type
            print (repr(t.splits[splitnum].account.type).strip("'").ljust(7), ' ', end='')

            # transaction account name
            print(repr(t.splits[splitnum].account.name).strip("'").ljust(20), end=' ')

            # transaction description
            print(t.description.ljust(24), end=' ')

            hours_worked = math.floor(float(t.splits[splitnum].value)/self.hourly_rate)
            minutes_worked = math.floor(math.fabs(hours_worked-(float(t.splits[splitnum].value)/self.hourly_rate))*60)


            print(str(hours_worked) + ":" + str(minutes_worked))


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

        # print income accounts
        self.print_accounts_summary(self.income_accounts)
        print()

        # print savings summary
        print ('Savings  ', end='')
        print('\t', repr(float(self.savings)).rjust(8), '/', repr(self.savings_budget).rjust(4), end=' ')
        print(self.get_percentage_bar(self.savings, self.savings_budget))


# print savings projection
def printSavingsProjection(book, monthly_budget):
    
    savings = book.accounts(fullname="Assets:Current Assets:Savings Account")
    monthly_addative_budget = 0
    debt_bal = 0 
    
    if monthly_budget.debt_budget != 0:
        debt_bal = book.accounts(fullname='Liabilities:Loans:'+monthly_budget.debt_name).get_balance()

    debt_subtractive = 0

    debt_free = False

    print('Projection: ')

    for m in range(monthly_budget.month+1, monthly_budget.month+13-monthly_budget.month):
        monthnum = m if m <13 else m%13+1 
        year = datetime.datetime.now().year if m < 13 else datetime.datetime.now().year+1

        print('    ', year, calendar.month_name[monthnum].ljust(10), "Saving:", end = ' ')
        if(not (m == monthly_budget.month and monthly_budget.savings > monthly_budget.savings_budget)):
            monthly_addative_budget += monthly_budget.savings_budget
            print(savings.get_balance() + monthly_addative_budget, ' (+', str(monthly_addative_budget).ljust(4), ')', sep='', end = ' ')

            if debt_bal == 0:
                print()
                continue

            debt_subtractive = debt_subtractive + monthly_budget.debt_budget
            debt_bal = debt_bal - monthly_budget.debt_budget

            if(debt_bal < 0): 
                debt_subtractive = debt_subtractive - monthly_budget.debt_budget
                debt_subtractive = debt_subtractive + debt_bal + monthly_budget.debt_budget
                debt_bal = 0
            
            if not debt_free:
                print(' |  ', monthly_budget.debt_name, ': ', str(debt_bal).ljust(7), ' (-', str(debt_subtractive).ljust(4), ')', sep='')
            else:
                print()

            if debt_bal <= 0:
                debt_free = True
            
        
# print current book account balances
def printAccountBalances(book, monthly_budget):
 	
    print()
    print ('Balances:', end=' ')
    print ("({:%b %d %Y})".format(datetime.date.today()))
    checking = book.accounts(fullname="Assets:Current Assets:Checking Account")
    savings = book.accounts(fullname="Assets:Current Assets:Savings Account")
    credit_card = book.accounts(fullname="Liabilities:Credit Card")
    
    print (repr('  Credit Card ').strip("'").ljust(26), end = '')
    if(credit_card.get_balance() == 0):
        print("0")
    else:
        print (credit_card.get_balance())
    
    print (repr('  Checking Account ').strip("'").ljust(26), end='')
    print (checking.get_balance(), end='')

    # net balance
    if(credit_card.get_balance() != 0):
        print ('  (', end='')
        print(checking.get_balance()-credit_card.get_balance(), '= ',  end='')
        print(checking.get_balance(), '-', credit_card.get_balance(), end='')
        print (')')
    else:
        print()
    
    print (repr('  Savings Account ').strip("'").ljust(26), end = '')
    print (savings.get_balance())


# today
today = datetime.date.today()

# year/month override (to get different year's data)
# today = datetime.datetime.strptime('Dec 25 2016  1:33PM', '%b %d %Y %I:%M%p')

# settings file
settings_file = 'settings.yaml'

# start month is current month 
start_month = today.month 

if len(sys.argv[1:]) > 0:
    # print full year
    if str(sys.argv[1:][0]) == 'year':
        start_month = 1
        print_full_year = True
    # different settings file
    elif 'yaml' in str(sys.argv[1:][0]):
        settings_file = sys.argv[1:][0]
    else:
        try:
            start_month = (today.month - int(sys.argv[1:][0]) + 1)
        except ValueError:
            print("Failure to parse commandline argument")

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

# for current month, or January ascending to current month
for current_month in range(start_month, today.month+1, 1):
    
    # create monthly budget from settings file
    b = monthly_budget(name = calendar.month_name[current_month], month = current_month, budget_file = budget_file)

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
        splitnum = int(t.splits[0].value < 0)

        # if account is income, look at where it came from
        if t.splits[splitnum].account.type == 'BANK':

            # "from" account
            secondary = (splitnum+1)%2

            # use savings account (even if income goes directly into savings)
            if('Savings' in t.splits[splitnum].account.fullname):
                b.add_to_account(t.splits[splitnum].account, t.splits[splitnum].value)
            else:
                b.add_to_account(t.splits[secondary].account, t.splits[splitnum].value)

        # add CC reward money as income, regardless of where it goes
        elif t.splits[splitnum].account.type == 'CREDIT':
            if 'Rewards' in t.splits[splitnum].account.fullname:
                b.add_to_account(t.splits[splitnum].account, t.splits[splitnum].value)
            if 'Rewards' in t.splits[(splitnum+1)%2].account.fullname:
                b.add_to_account(t.splits[(splitnum+1)%2].account, abs(t.splits[(splitnum+1)%2].value))

        # add transaction if matching looping month
        elif t.post_date.month == current_month:
            b.add_to_account(t.splits[splitnum].account, t.splits[splitnum].value)

    # print transactions descending
    b.print_transactions_desc()    
    
    # print monthly budget
    b.print_summary()

# print book account balances for current month only
printAccountBalances(book, b)
print()

# print projection
b = monthly_budget(name = calendar.month_name[start_month], month = start_month, budget_file = budget_file)
printSavingsProjection(book, b)