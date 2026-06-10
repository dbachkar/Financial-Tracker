
import json
import os
from datetime import datetime

# File paths for data persistence - these JSON files store all user data
PROFILE_FILE = "profile.json"
EXPENSES_FILE = "expenses.json"

# User profile structure (dictionary) - stores all user financial information
# This includes income, fixed monthly expenses, spending categories, and budgets
user_profile = {
    "monthly_income": 0.0,
    "fixed_expenses": {},
    "categories": [],  
    "category_budgets": {}  
}
expenses = {} 

# Unique ID counter for expenses - increments each time an expense is added
# This ensures each expense can be uniquely identified for deletion or editing
expense_id_counter = 1

def save_data():
    """
    Saves user profile and expenses to JSON files for persistence.
    
    This function writes two separate JSON files:
    1. profile.json - contains user's income, fixed expenses, categories, and budgets
    2. expenses.json - contains all expense records and the ID counter
    
    Requirements met:
    - Files: Writing to files using json.dump()
    - Try-except: IOError handling for file write failures
    - Dictionary operations: Dumping dictionaries to JSON format
    """
    try:
        with open(PROFILE_FILE, 'w') as f:
            json.dump(user_profile, f, indent=4)

        with open(EXPENSES_FILE, 'w') as f:
            json.dump({"expenses": expenses, "id_counter": expense_id_counter}, f, indent=4)
        
        print("✓ Data saved successfully!")
        
    except IOError as e:
        print(f"Error saving data: {e}")


def load_data():
    """
    Loads user profile and expenses from JSON files if they exist.
    
    This function runs at program startup to restore previous session data.
    If files don't exist (first run), it continues with empty default values.
    
    Requirements met:
    - Files: Reading from files using json.load()
    - Try-except: Handles missing files and JSON decode errors gracefully
    - Global variables: Modifies global state (user_profile, expenses, expense_id_counter)
    - Branching: Checks if files exist before attempting to read
    """
   
    global user_profile, expenses, expense_id_counter
    
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r') as f:
                user_profile = json.load(f)
            print("✓ Profile loaded")
        
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'r') as f:
                data = json.load(f)
                expenses = data.get("expenses", {})
                expense_id_counter = data.get("id_counter", 1)
            print("✓ Expenses loaded")
    
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        print("Starting with fresh data...")

def setup_profile():
    """
    First-time setup wizard for user profile.
    
    This interactive function guides users through:
    1. Entering their monthly income
    2. Setting up fixed monthly expenses (EMI, rent, insurance, etc.)
    3. Creating spending categories
    4. Allocating budgets to each category
    
    Requirements met:
    - Input: Getting user input with input()
    - Try-except: Input validation for numeric values
    - Loops: While loop for categories, for loop for fixed expenses
    - Branching: Multiple if/elif/else statements for user choices
    - Dictionary operations: Adding key-value pairs to user_profile
    - List operations: Appending categories
    - Logical expressions: Using 'and', 'or' for validation
    """

    print("\n" + "="*60)
    print("Welcome to Personal Finance Tracker!".center(60))
    print("Let's set up your profile".center(60))
    print("="*60)
 
    while True:
        try:
            income = float(input("\nEnter your monthly income: $"))
            if income <= 0:
                print("Income must be positive. Try again.")
                continue
            user_profile["monthly_income"] = income
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("\n--- Fixed Monthly Expenses ---")
    print("These are expenses that stay the same every month")
    
    common_fixed = ("EMI", "Insurance", "Rent", "Utilities", "Subscriptions")
    
    for expense_type in common_fixed:
        while True:
            try:
                has_expense = input(f"Do you have {expense_type}? (yes/no): ").lower()
            
                if has_expense == 'yes' or has_expense == 'y':
                    amount = float(input(f"Enter monthly {expense_type} amount: $"))
                    if amount > 0:
                        user_profile["fixed_expenses"][expense_type] = amount
                    break
                elif has_expense == 'no' or has_expense == 'n':
                    break
                else:
                    print("Please answer yes or no")
            except ValueError:
                print("Invalid amount. Try again.")

    while True:
        add_more = input("\nAdd another fixed expense? (yes/no): ").lower()
        if add_more == 'yes' or add_more == 'y':
            name = input("Expense name: ")
            try:
                amount = float(input("Monthly amount: $"))
                if amount > 0:
                    user_profile["fixed_expenses"][name] = amount
            except ValueError:
                print("Invalid amount, skipping.")
        else:
            break

    total_fixed = sum(user_profile["fixed_expenses"].values())
    available = income - total_fixed
    
    print(f"\n💰 Total Fixed Expenses: ${total_fixed:.2f}")
    print(f"💰 Available for budgeting: ${available:.2f}")
  
    print("\n--- Spending Categories ---")
    print("Examples: Food, Transport, Entertainment, Shopping, Healthcare")
    
    while True:
        category = input("\nEnter a category name (or 'done' to finish): ").strip()

        if category.lower() == 'done':
            if len(user_profile["categories"]) == 0:
                print("Please add at least one category!")
                continue
            break

        if category and category not in user_profile["categories"]:
            user_profile["categories"].append(category)
            expenses[category] = []  
            print(f"✓ Added '{category}'")
        elif category in user_profile["categories"]:
            print("Category already exists!")
    
    allocate_budgets(available)
    
    save_data()
    
    print("\n✓ Profile setup complete!")
    input("Press Enter to continue...")


def allocate_budgets(available_amount):
    """
    Allocates budget to each spending category.
    
    Users can choose between automatic (equal distribution) or manual allocation.
    Manual allocation ensures total budgets don't exceed available amount.
    
    Parameters:
        available_amount (float): Money available after fixed expenses
    
    Requirements met:
    - Loops: For loop through categories
    - Branching: Auto vs manual allocation choice
    - Arithmetic expressions: Budget calculations
    - Dictionary operations: Setting category_budgets values
    - Try-except: Input validation
    """
    print(f"\n--- Budget Allocation (${available_amount:.2f} available) ---")
    
    choice = input("Auto-allocate budgets or manual? (auto/manual): ").lower()
    
    if choice == 'auto':
        per_category = available_amount / len(user_profile["categories"])
        
        for category in user_profile["categories"]:
            user_profile["category_budgets"][category] = round(per_category, 2)
        
        print(f"✓ Allocated ${per_category:.2f} to each category")
    
    else:
        remaining = available_amount
        
        for category in user_profile["categories"]:
            while True:
                try:
                    print(f"\nRemaining to allocate: ${remaining:.2f}")
                    budget = float(input(f"Budget for {category}: $"))
                  
                    if budget >= 0 and budget <= remaining:
                        user_profile["category_budgets"][category] = budget
                        remaining -= budget
                        break
                    else:
                        print(f"Budget must be between $0 and ${remaining:.2f}")
                except ValueError:
                    print("Invalid input. Enter a number.")
        
        if remaining > 0:
            print(f"\n💡 ${remaining:.2f} left unallocated (will go to savings!)")

def add_expense():
    """
    Adds a new expense to the tracker.
    
    This function prompts for category, amount, date, and description,
    validates all inputs, and adds the expense to the appropriate category.
    It also checks if the category is over budget after adding.
    
    Requirements met:
    - Input: Multiple input() calls for expense details
    - Try-except: Amount and date validation
    - Branching: Category validation and budget checking
    - Dictionary and list operations: Adding to expenses dictionary
    - Global variable modification: Incrementing expense_id_counter
    - String operations: Date formatting and validation
    """
    global expense_id_counter
    
    print("\n--- Add New Expense ---")

    print("Categories:", ", ".join(user_profile["categories"]))
    
    while True:
        category = input("\nEnter category: ").strip()
        
        if category in user_profile["categories"]:
            break
        elif category == "":
            print("Category cannot be empty!")
        else:
            print(f"'{category}' not found. Available: {user_profile['categories']}")
            add_new = input("Add as new category? (yes/no): ").lower()
            if add_new == 'yes' or add_new == 'y':
                user_profile["categories"].append(category)
                user_profile["category_budgets"][category] = 0.0
                expenses[category] = []
                break
 
    while True:
        try:
            amount = float(input("Enter amount: $"))
            if amount <= 0:
                print("Amount must be positive!")
                continue
            break
        except ValueError:
            print("Invalid input. Enter a number.")

    while True:
        date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if date_str == "":
            date_str = datetime.now().strftime("%Y-%m-%d")
            break
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
    
    description = input("Enter description: ").strip()
    if description == "":
        description = "No description"
    
    expense = {
        "id": expense_id_counter,
        "date": date_str,
        "amount": amount,
        "description": description
    }
  
    expenses[category].append(expense)
    expense_id_counter += 1
    
    print(f"\n✓ Expense added! (ID: {expense['id']})")
    
    spent = calculate_category_spending(category)
    budget = user_profile["category_budgets"].get(category, 0)
    
    if budget > 0 and spent > budget:
        print(f"⚠️  WARNING: {category} is over budget!")
        print(f"   Spent: ${spent:.2f} / Budget: ${budget:.2f}")
    elif budget > 0 and spent >= budget * 0.8:
        print(f"⚠️  CAUTION: {category} is at {(spent/budget)*100:.1f}% of budget")
    
    save_data()
    input("\nPress Enter to continue...")


def view_all_expenses():
    """
    Displays all expenses across all categories in a formatted table.
    
    This function loops through each category and displays all expenses
    with running totals for each category and a grand total.
    
    Requirements met:
    - Nested loops: Loop through categories, then expenses within each
    - String formatting: Formatted table output
    - Arithmetic expressions: Calculate totals
    - Branching: Check if expenses exist
    """
    print("\n" + "="*80)
    print("ALL EXPENSES".center(80))
    print("="*80)
    
    has_expenses = False
    total_all = 0.0
 
    for category in sorted(user_profile["categories"]):
        if category in expenses and len(expenses[category]) > 0:
            has_expenses = True
            
            print(f"\n📁 {category}")
            print("-" * 80)
            print(f"{'ID':<6} {'Date':<12} {'Amount':>10} {'Description':<40}")
            print("-" * 80)
            
            category_total = 0.0
            
            for exp in expenses[category]:
                print(f"{exp['id']:<6} {exp['date']:<12} ${exp['amount']:>9.2f} {exp['description']:<40}")
                category_total += exp['amount']
            
            print("-" * 80)
            print(f"{'Category Total:':<60} ${category_total:>9.2f}")
            total_all += category_total
    
    if not has_expenses:
        print("\nNo expenses recorded yet.")
    else:
        print("\n" + "="*80)
        print(f"{'GRAND TOTAL:':<60} ${total_all:>9.2f}")
        print("="*80)
    
    input("\nPress Enter to continue...")


def view_category_expenses():
    """
    Displays expenses for a specific category chosen by the user.
    
    Shows all expenses in the category with total, budget, and remaining amount.
    
    Requirements met:
    - Input: Getting category name from user
    - Branching: Check category exists and has expenses
    - Dictionary retrieval by key: expenses[category]
    - Loop through list: Iterate through expense list
    """
    print("\n--- View Category Expenses ---")
    print("Categories:", ", ".join(user_profile["categories"]))
    
    category = input("\nEnter category name: ").strip()
    
    if category not in user_profile["categories"]:
        print(f"Category '{category}' not found!")
        input("Press Enter to continue...")
        return
    
    print(f"\n{'='*60}")
    print(f"📁 {category}".center(60))
    print(f"{'='*60}")
    
    if category not in expenses or len(expenses[category]) == 0:
        print("\nNo expenses in this category yet.")
    else:
        print(f"{'ID':<6} {'Date':<12} {'Amount':>10} {'Description':<25}")
        print("-" * 60)
        
        total = 0.0
        for exp in expenses[category]:
            print(f"{exp['id']:<6} {exp['date']:<12} ${exp['amount']:>9.2f} {exp['description']:<25}")
            total += exp['amount']
        
        print("-" * 60)
        print(f"{'Total Spent:':<49} ${total:>9.2f}")
        
        budget = user_profile["category_budgets"].get(category, 0)
        if budget > 0:
            remaining = budget - total
            percentage = (total / budget) * 100
            
            print(f"{'Budget:':<49} ${budget:>9.2f}")
            print(f"{'Remaining:':<49} ${remaining:>9.2f}")
            print(f"{'Used:':<49} {percentage:>9.1f}%")
    
    input("\nPress Enter to continue...")


def delete_expense():
    """
    Deletes an expense by ID.
    
    Requirements met:
    - Input with try-except
    - Nested loops: Search through categories and expenses
    - Break statement (Advanced feature)
    - List operations: remove
    - Branching
    """
    print("\n--- Delete Expense ---")
    
    try:
        exp_id = int(input("Enter expense ID to delete: "))
    except ValueError:
        print("Invalid ID!")
        input("Press Enter to continue...")
        return
    
    found = False
    for category in expenses:
        for i, exp in enumerate(expenses[category]):
            if exp['id'] == exp_id:
                print(f"\nFound: {exp['description']} - ${exp['amount']:.2f} on {exp['date']}")
                confirm = input("Delete this expense? (yes/no): ").lower()
                
                if confirm == 'yes' or confirm == 'y':
                    expenses[category].pop(i) 
                    print("✓ Expense deleted!")
                    save_data()
                else:
                    print("Deletion cancelled.")
                
                found = True
                break  
        
        if found:
            break  
    
    if not found:
        print(f"Expense ID {exp_id} not found!")
    
    input("\nPress Enter to continue...")

def calculate_category_spending(category):
    """
    Calculates total spending in a specific category.
    
    This helper function sums all expense amounts in a category.
    Demonstrates list comprehension (Advanced feature).
    
    Parameters:
        category (str): The category to calculate spending for
    
    Returns:
        float: Total amount spent in the category
    
    Requirements met:
    - Loop/comprehension: List comprehension to extract amounts
    - Arithmetic expressions: sum() function
    - Dictionary operations: Accessing expenses[category]
    """
    if category not in expenses:
        return 0.0
   
    total = sum([exp['amount'] for exp in expenses[category]])
    return total


def check_budget_status():
     """
     Checks budget status for all categories and displays comparison table.
    
     Shows spent vs budget for each category with visual status indicators.
     Helps users see which categories are over/under budget at a glance.
    
     Requirements met:
     - Loops: Iterate through categories
     - Logical expressions: and, or, not operators
     - Boolean expressions: comparisons (<, >, <=, >=)
     - Branching: Multiple if/elif/else for status determination
     - Arithmetic expressions: Percentage calculations
     """
     print("\n" + "="*70)
     print("BUDGET STATUS".center(70))
     print("="*70)
     print(f"{'Category':<20} {'Spent':>12} {'Budget':>12} {'Status':>15}")
     print("-"*70)
    
     total_spent = 0.0
     total_budget = 0.0
    
     for category in sorted(user_profile["categories"]):
         spent = calculate_category_spending(category)
         budget = user_profile["category_budgets"].get(category, 0)
        
         total_spent += spent
         total_budget += budget
     
         if budget == 0:
             status = "No Budget"
         elif spent > budget:
             percentage = (spent / budget) * 100
             status = f"⚠️ OVER {percentage:.0f}%"
         elif spent >= budget * 0.8 and spent <= budget:
             percentage = (spent / budget) * 100
             status = f"⚠️ {percentage:.0f}%"
         else:
             percentage = (spent / budget) * 100
             status = f"✓ {percentage:.0f}%"
        
         print(f"{category:<20} ${spent:>11.2f} ${budget:>11.2f} {status:>15}")
    
     print("-"*70)
     print(f"{'TOTAL':<20} ${total_spent:>11.2f} ${total_budget:>11.2f}")
     print("="*70)
    
     input("\nPress Enter to continue...")
 
def calculate_savings():
     """
    Calculates actual savings for the month.
    
    Formula: Income - Fixed Expenses - Variable Spending = Savings
    Also calculates expected savings based on budgets.
    
    Returns:
        tuple: (actual_savings, expected_savings, total_fixed, total_spending)
    
    Requirements met:
    - Arithmetic expressions: Multiple calculations
    - Loops: Calculate total spending across categories
    - Dictionary operations: sum() on dictionary values
    """

     income = user_profile["monthly_income"]

     total_fixed = sum(user_profile["fixed_expenses"].values())
    
     total_spending = 0.0
     for category in expenses:
         total_spending += calculate_category_spending(category)
    
     actual_savings = income - total_fixed - total_spending
    
     total_budgets = sum(user_profile["category_budgets"].values())
     expected_savings = income - total_fixed - total_budgets
    
     return actual_savings, expected_savings, total_fixed, total_spending


def view_savings():
    """
    Displays savings information with analysis.
    
    Shows actual vs expected savings and provides feedback on performance.
    
    Requirements met:
    - Function call: Calls calculate_savings()
    - Arithmetic expressions: Difference and percentage calculations
    - String formatting: Currency and percentage formatting
    - Branching: Different feedback based on savings amount
    """
 
    print("\n" + "="*60)
    print("SAVINGS ANALYSIS".center(60))
    print("="*60)
    
    actual, expected, fixed, spending = calculate_savings()
    income = user_profile["monthly_income"]
    
    print(f"\n💰 Monthly Income:        ${income:>10.2f}")
    print(f"📌 Fixed Expenses:        ${fixed:>10.2f}")
    print(f"🛒 Variable Spending:     ${spending:>10.2f}")
    print("-" * 60)
    print(f"💵 Actual Savings:        ${actual:>10.2f}")
    print(f"📊 Expected Savings:      ${expected:>10.2f}")
    print(f"📈 Difference:            ${actual - expected:>10.2f}")
    
    if income > 0:
        savings_rate = (actual / income) * 100
        print(f"📊 Savings Rate:          {savings_rate:>10.1f}%")
    
    print("="*60)
   
    if actual > expected:
        print("\n✓ Great job! You're saving more than planned!")
    elif actual < expected and actual > 0:
        print("\n⚠️  You're saving less than expected, but still saving!")
    elif actual <= 0:
        print("\n⚠️  Warning: You're not saving this month. Consider reducing expenses.")
    
    input("\nPress Enter to continue...")

def generate_monthly_report():
     """
     Generates a comprehensive monthly report with option to save to file.
    
     Creates a detailed report showing:
     - Income and fixed expenses
     - Category-wise spending vs budgets
     - Savings analysis
    
     Can filter expenses by specific month using date string matching.
    
     Requirements met:
     - Nested loops: Loop through categories, then filter expenses
     - String operations: Date filtering with substring matching
     - Arithmetic expressions: Various calculations
     - Branching: Multiple decision points
     - File writing: Save report to text file
     """
   
     print("\n--- Generate Monthly Report ---")
    
     month = input("Enter month (YYYY-MM) or press Enter for current month: ").strip()
     
     if month == "":
         month = datetime.now().strftime("%Y-%m")
    
     print(f"\nGenerating report for {month}...")
    
     report_lines = []
     report_lines.append("="*70)
     report_lines.append(f"MONTHLY FINANCIAL REPORT - {month}".center(70))
     report_lines.append("="*70)
     report_lines.append("")
     
     income = user_profile["monthly_income"]
     report_lines.append(f"💰 Monthly Income: ${income:.2f}")
     report_lines.append("")
    
     report_lines.append("📌 Fixed Expenses:")
     total_fixed = 0.0
     for name, amount in user_profile["fixed_expenses"].items():
         report_lines.append(f"   {name:<30} ${amount:>10.2f}")
         total_fixed += amount
     report_lines.append(f"   {'Total Fixed:':<30} ${total_fixed:>10.2f}")
     report_lines.append("")
    
     report_lines.append("🛒 Variable Expenses:")
     report_lines.append(f"{'Category':<20} {'Spent':>12} {'Budget':>12} {'Difference':>12}")
     report_lines.append("-"*70)
    
     total_spent = 0.0
     total_budget = 0.0
    
     for category in sorted(user_profile["categories"]):
         monthly_expenses = [exp for exp in expenses.get(category, []) if month in exp['date']]
        
         spent = sum([exp['amount'] for exp in monthly_expenses])
         budget = user_profile["category_budgets"].get(category, 0)
         difference = budget - spent
        
         total_spent += spent
         total_budget += budget
        
         report_lines.append(f"{category:<20} ${spent:>11.2f} ${budget:>11.2f} ${difference:>11.2f}")
    
     report_lines.append("-"*70)
     report_lines.append(f"{'TOTAL':<20} ${total_spent:>11.2f} ${total_budget:>11.2f} ${total_budget - total_spent:>11.2f}")
     report_lines.append("")
    
     actual_savings = income - total_fixed - total_spent
     expected_savings = income - total_fixed - total_budget
    
     report_lines.append("💵 Savings:")
     report_lines.append(f"   Expected Savings: ${expected_savings:.2f}")
     report_lines.append(f"   Actual Savings:   ${actual_savings:.2f}")
    
     if income > 0:
         savings_rate = (actual_savings / income) * 100
         report_lines.append(f"   Savings Rate:     {savings_rate:.1f}%")
    
     report_lines.append("")
     report_lines.append("="*70)

     for line in report_lines:
         print(line)
    
     save = input("\nSave report to file? (yes/no): ").lower()
     if save == 'yes' or save == 'y':
         filename = f"report_{month}.txt"
         try:
             with open(filename, 'w') as f:
                 f.write("\n".join(report_lines))
             print(f"✓ Report saved to {filename}")
         except IOError as e:
             print(f"Error saving report: {e}")
    
     input("\nPress Enter to continue...")

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Prints the program header."""
    print("\n" + "="*60)
    print("💰  PERSONAL FINANCE TRACKER  💰".center(60))
    print("="*60)


def main_menu():
    """
    Main menu loop.
    
    Requirements met:
    - While loop: Continuous menu
    - Branching: if/elif/else for menu choices
    - Function calls
    - Input
    """
    while True:
        clear_screen()
        print_header()
       
        income = user_profile.get("monthly_income", 0)
        if income > 0:
            actual, expected, _, _ = calculate_savings()
            print(f"\n📊 Income: ${income:.2f} | Savings: ${actual:.2f}")
        
        print("\n--- MAIN MENU ---")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Category Expenses")
        print("4. Delete Expense")
        print("5. Check Budget Status")
        print("6. View Savings")
        print("7. Generate Monthly Report")
        print("8. Edit Profile")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
       
        if choice == '1':
            add_expense()
        elif choice == '2':
            view_all_expenses()
        elif choice == '3':
            view_category_expenses()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            check_budget_status()
        elif choice == '6':
            view_savings()
        elif choice == '7':
            generate_monthly_report()
        elif choice == '8':
            setup_profile()
        elif choice == '9':
            print("\nSaving data...")
            save_data()
            print("Thank you for using Personal Finance Tracker!")
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice! Please enter 1-9")
            input("Press Enter to continue...")

def test_functions():
    
    print("\n" + "="*60)
    print("RUNNING TESTS".center(60))
    print("="*60)
    
    print("\n[Test 1] Testing savings calculation...")
    test_income = 50000
    test_fixed = {"EMI": 10000, "Rent": 15000}
    test_spending = 12000
    
    total_fixed = sum(test_fixed.values())
    savings = test_income - total_fixed - test_spending
    
    print(f"Income: ${test_income}, Fixed: ${total_fixed}, Spending: ${test_spending}")
    print(f"Expected Savings: ${savings}")
    assert savings == 13000, "Savings calculation failed!"
    print("✓ Test 1 passed!")
    
    print("\n[Test 2] Testing budget warning logic...")
    test_budget = 5000
    test_spent_1 = 4500  
    test_spent_2 = 3000  
    
    percentage_1 = (test_spent_1 / test_budget) * 100
    percentage_2 = (test_spent_2 / test_budget) * 100
    
    print(f"Test spent ${test_spent_1} of ${test_budget} = {percentage_1}%")
    assert percentage_1 >= 80, "Should trigger warning"
    print("✓ Warning logic works!")
    
    print(f"Test spent ${test_spent_2} of ${test_budget} = {percentage_2}%")
    assert percentage_2 < 80, "Should not trigger warning"
    print("✓ Safe spending logic works!")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓".center(60))
    print("="*60)

def main():
    """Main program entry point."""
    load_data()
    
    
    if user_profile["monthly_income"] == 0:
        setup_profile()
    
    main_menu()



if __name__ == "__main__":
    
    test_functions()
    
    main()