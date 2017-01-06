# gnuCash Budget Report
### Run:
Run with a parameter for DEMO settings and database: ./program demo

### Output:

Output will show percentage bars per budget category and accounts. At this time, budget categories are static while accounts are dynamic from the settings file.
Over-budgeting is shown by a >100% bar.
```
Essentials 1180 / 1500	[********  ]79%
   Rent 	1000 	    [**********]100%
   Utilities 	80 	    [********  ]80%
   Groceries 	100 	[***       ]25%

Personal 1284 / 1000	[*************]128%

Income 4000 / 4000	    [**********]100%

Savings 400 / 400	    [**********]100%
   Savings 	400 	    [**********]100%

```
Transactions are also shown. Accounts for the active month in descending order. Transactions in accounts will be in latest to oldest.
```
DEMO MODE
Budget:  Jan   2017
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Assets:Current Assets:Checking Account
   -80 		Jan 13 2017 	Income		Electric
   -1000 	Jan 02 2017 	Income		Rent
   -200 	Jan 20 2017 	Income		Income Savings
   -200 	Jan 06 2017 	Income		Income Savings
   2000 	Jan 20 2017 	Income		Income
   2000 	Jan 06 2017 	Income		Income
Assets:Current Assets:Savings Account
   200 		Jan 20 2017 	Savings 	Income Savings
   200 		Jan 06 2017 	Savings 	Income Savings
Expenses:Dining
   84 		Jan 25 2017 	Personal 	Fancy Resturaunt
Expenses:Groceries
   100 		Jan 05 2017 	Essential 	Not junk food
Expenses:Rent
   1000 	Jan 02 2017 	Essential 	Rent
Expenses:Utilities:Electric
   80 		Jan 13 2017 	Essential 	Electric
Expenses:Video Games
   1200 	Jan 18 2017 	Personal 	VR headset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```
### Settings Setup:
Settings file is organized with 50/20/30 budgeting in mind. 50% to essentials, 20% to savings, 30% personal (other). (You could set areas to 0 budget). Income has an expected positive amount.

```
file : 'sample.gnucash'

essentials:
    accounts: 
        - name: Rent
          budget: 1000
        - name: Utilities
          budget: 100
        - name: Groceries
          budget: 400
    budget: 1100 #total
savings:
    accounts: 
        - name: Savings
          budget: 400
    budget: 400
personal:
    #   personal is implied every other accounts
    budget: 1000
income:
    budget: 4000

```
