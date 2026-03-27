# Budget Tracker

A command line budget tracking tool built with Python.

## GUI Version (budget_tracker_gui.py)
- Full desktop interface built with Tkinter
- Color coded transaction rows — green for income, red for expenses
- Live summary bar showing income, expenses, and balance
- Spending by category — bar chart and pie chart
- Income vs expenses comparison chart
- Edit existing transactions
- Export to Excel with formatted headers and summary
- Export to CSV
- Dark mode toggle
- Data persists between sessions via JSON

## Features

### Command Line Version
- Add income and expense transactions
- View summary — total income, expenses, and balance
- View all transactions with category and description
- Delete transactions
- Input validation for all fields
- Data persistence — saves and loads between sessions via JSON

### GUI Version
- Full desktop interface built with Tkinter
- Color coded transaction rows — green for income, red for expenses
- Live summary bar showing income, expenses, and balance
- Add, delete, and edit transactions
- Spending by category — bar chart and pie chart using matplotlib
- Income vs expenses comparison chart with surplus/deficit indicator
- Export to Excel with formatted headers and summary totals
- Export to CSV
- Dark mode toggle
- Data persists automatically between sessions via JSON

## How to Run

**Command line version:**
```
python budget_tracker.py
```

**GUI version (recommended):**
```
python budget_tracker_gui.py
```

**Or download the executable** from the 
[Releases](https://github.com/jamesdileva/Python-Projects/releases/tag/budget-tracker-v1.0) page — no Python 
installation required. Windows only.
```

## Usage

### Command Line Version
1. Add Income — log a source of income with category and description
2. Add Expense — log an expense with category and description
3. View Summary — see total income, expenses, and current balance
4. View All Transactions — see a detailed list of every transaction
5. Delete a Transaction — remove an entry by number
6. Exit

### GUI Version
- **Add Transaction** — select type, enter category, amount, and description
- **Delete Selected** — select a row and delete it with confirmation prompt
- **Edit Selected** — opens a popup with the transaction pre-filled for editing
- **Spending Chart** — bar chart and pie chart of expenses by category
- **Income vs Expenses** — side by side comparison chart with surplus/deficit indicator
- **Export to Excel** — saves all transactions with formatted headers and summary totals
- **Export to CSV** — saves all transactions as a standard CSV file
- **Dark Mode** — toggles between light and dark theme
- All data saves automatically between sessions

## Roadmap
The following features are planned for future development:

## Roadmap
### Completed
- ✅ GUI — Tkinter desktop app
- ✅ Export to Excel and CSV
- ✅ Data persistence — JSON
- ✅ Spending charts — matplotlib bar and pie
- ✅ Edit transactions
- ✅ Dark mode toggle

### Planned
- **Dark mode polish** — full theme coverage including frames
- **Date tracking** — filter transactions by month
- **Budget limits** — spending warnings per category
- **Monthly reports** — summarize by month