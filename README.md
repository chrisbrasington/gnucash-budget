# gnuCash Budget Report
### Run:
Run with a parameter for DEMO settings and database: ./main settings_sample.yaml

### Output:

Output will show percentage bars per budget category and accounts. At this time, budget categories are static (essential, personal, income, savings) while accounts are dynamic from the settings file.
Over-budgeting is shown by a >100% bar.
```
January 2017 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      84.0  01/25/2017  EXPENSE  Dining               Fancy Resturaunt
     200.0  01/20/2017  BANK     Savings Account      Income Savings
    2000.0  01/20/2017  BANK     Checking Account     Income
      20.0  01/19/2017  EXPENSE  Video Games          Video games
    1200.0  01/18/2017  EXPENSE  Video Games          VR headset
      80.0  01/13/2017  EXPENSE  Electric             Electric
     200.0  01/06/2017  BANK     Savings Account      Income Savings
    2000.0  01/06/2017  BANK     Checking Account     Income
     100.0  01/05/2017  EXPENSE  Groceries            Not junk food
    1000.0  01/02/2017  EXPENSE  Rent                 Rent

Essentials	   1180.0 / 1500 [********  ]79% 
  Rent                    1000
  Utilities               80
  Groceries               100

Personal	   1304.0 / 1000 [**************]130% 
  Dining                  84
  Video Games             1220

Income  	   4000.0 / 4000 [**********]100%
Savings  	    400.0 /  400 [**********]100%

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
    budget: 1500
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