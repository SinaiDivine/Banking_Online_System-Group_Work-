import sqlite3
import random
import time
import hashlib
from datetime import datetime

DATABASE_NAME = 'smb_bank.db'
STAFF_SECRET = 'smb_staff_pass' # Simple shared secret (no longer used for default staff, but kept)
INTEREST_RATE = 0.30 # 30% monthly interest rate

def _hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def _execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Generic function to execute SQL queries."""
    conn = None
    result = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        if conn:
            conn.rollback()
        result = False
    finally:
        if conn:
            conn.close()
        return result

def setup():
    """Initializes the database, creating tables and inserting default staff accounts."""
    # 1. Accounts Table (Main bank accounts)
    _execute_query('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT,  
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            savings_balance REAL DEFAULT 0.0,
            created_at TEXT
        )
    ''')
    
    # 2. Transactions Table (History/Audit Log)
    _execute_query('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT NOT NULL,
            type TEXT NOT NULL, -- e.g., 'Deposit', 'Withdrawal', 'Transfer Out', 'Transfer In', 'Save/Invest', 'Withdraw Savings', 'Interest', 'Airtime', 'Password_Reset'
            amount REAL NOT NULL,
            target_account TEXT, -- Target of Transfer Out/In, or phone number for airtime
            timestamp TEXT,
            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
        )
    ''')
    
    # 3. Staff Table (Admin and Agent logins)
    _execute_query('''
        CREATE TABLE IF NOT EXISTS staff (
            staff_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL -- 'Admin' or 'Agent'
        )
    ''')
    
    # Insert default staff accounts with custom credentials
    admin_id = 'admin'        # Admin ID: admin
    admin_password = 'admin123'  # Admin Password: admin123
    agent_id = '100'	# Agent ID: 100
    agent_password = '456'    # Agent Password: 456
    agent_id = '200'	# Agent ID: 200
    agent_password = '456'    # Agent Password: 456
    agent_id = '300'    # Agent ID: 300
    agent_password = '456'    # Agent Password: 456
    agent_password = '456'    # Agent Password: 456
    
    hashed_admin_pass = _hash_password(admin_password)
    hashed_agent_pass = _hash_password(agent_password)
    
    # Insert Admin
    if not _execute_query("SELECT staff_id FROM staff WHERE staff_id=?", (admin_id,), fetch_one=True):
        _execute_query("INSERT INTO staff VALUES (?, ?, ?)", (admin_id, hashed_admin_pass, 'Admin'))
    
    # Insert Agent
    if not _execute_query("SELECT staff_id FROM staff WHERE staff_id=?", (agent_id,), fetch_one=True):
        _execute_query("INSERT INTO staff VALUES (?, ?, ?)", (agent_id, hashed_agent_pass, 'Agent'))
    
    print("Database setup complete: tables checked/created, default staff accounts ensured.")

# =========================================================================
# AUTHENTICATION
# =========================================================================

def verify_staff_login(staff_id, password, role):
    """Verifies staff (Admin/Agent) credentials."""
    hashed_password = _hash_password(password)
    query = "SELECT staff_id FROM staff WHERE staff_id = ? AND password_hash = ? AND role = ?"
    result = _execute_query(query, (staff_id, hashed_password, role), fetch_one=True)
    return result is not None

def verify_client_login(account_number, password):
    """Verifies client credentials."""
    hashed_password = _hash_password(password)
    query = "SELECT account_number FROM accounts WHERE account_number = ? AND password_hash = ?"
    result = _execute_query(query, (account_number, hashed_password), fetch_one=True)
    return result is not None

def change_password(account_number, old_password, new_password):
    """Verifies old password and updates to a new one (for client use)."""
    if not verify_client_login(account_number, old_password):
        return "Invalid Old Password"

    new_password_hash = _hash_password(new_password)
    query = "UPDATE accounts SET password_hash = ? WHERE account_number = ?"
    result = _execute_query(query, (new_password_hash, account_number))
    return result is True

def agent_reset_password(account_number, new_password):
    """
    Resets a client's password by an agent/admin, requiring only the account number and new password.
    Logs the action as a 'Password_Reset' transaction.
    """
    # 1. Check if the account exists
    account_check = _execute_query("SELECT account_number FROM accounts WHERE account_number = ?", (account_number,), fetch_one=True)
    if not account_check:
        return "Account Not Found"

    # 2. Hash the new password
    new_password_hash = _hash_password(new_password)

    # 3. Update the password
    query = "UPDATE accounts SET password_hash = ? WHERE account_number = ?"

    if _execute_query(query, (new_password_hash, account_number)) is not False:
        # Log this administrative action with a zero amount and 'Agent Reset' note
        log_transaction(account_number, 'Password_Reset', 0, "Agent Reset")
        return True
    else:
        return "Database Error"

# =========================================================================
# ACCOUNT MANAGEMENT
# =========================================================================

def create_new_account(first_name, last_name, phone_number, initial_deposit): 
    """Creates a new account, returns the generated account number or None on failure."""
    
    # Simple 5-digit account number generation
    while True:
        account_number = str(random.randint(20022, 99999))
        if not _execute_query("SELECT account_number FROM accounts WHERE account_number = ?", (account_number,), fetch_one=True):
            break
            
    # Initial password is the account number (must be changed later)
    initial_password_hash = _hash_password(account_number) 
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert account details (8 values)
    account_query = "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    account_params = (account_number, first_name, last_name, phone_number, initial_password_hash, initial_deposit, 0.0, created_at)
    
    if _execute_query(account_query, account_params) is not False:
        # Log the initial deposit as a transaction
        log_transaction(account_number, 'Deposit', initial_deposit, 'Initial Deposit')
        return account_number
    else:
        return None

def get_account_details(account_number):
    """Retrieves account details for the Agent Panel (6 items)."""
    query = "SELECT account_number, first_name, last_name, phone_number, balance, created_at FROM accounts WHERE account_number = ?"
    result = _execute_query(query, (account_number,), fetch_one=True)
    return result 

def get_all_accounts():
    """Retrieves all accounts for the Admin Panel (6 items)."""
    query = "SELECT account_number, first_name, last_name, phone_number, balance, created_at FROM accounts"
    return _execute_query(query, fetch_all=True)

def delete_account(account_number):
    """Deletes an account and all associated transactions."""
    if not _execute_query("SELECT account_number FROM accounts WHERE account_number = ?", (account_number,), fetch_one=True):
        return "Account Not Found"

    # Delete transactions first
    _execute_query("DELETE FROM transactions WHERE account_number = ?", (account_number,))
    # Then delete the account
    result = _execute_query("DELETE FROM accounts WHERE account_number = ?", (account_number,))
    return result is True

# =========================================================================
# BALANCE & HISTORY
# =========================================================================

def get_balance(account_number):
    """Retrieves the main account balance."""
    query = "SELECT balance FROM accounts WHERE account_number = ?"
    result = _execute_query(query, (account_number,), fetch_one=True)
    return result[0] if result else None

def get_savings_balance(account_number):
    """Retrieves the savings/investment account balance."""
    query = "SELECT savings_balance FROM accounts WHERE account_number = ?"
    result = _execute_query(query, (account_number,), fetch_one=True)
    return result[0] if result else None

def get_transaction_history(account_number, limit=20):
    """Retrieves the transaction history for an account."""
    query = "SELECT timestamp, type, amount, target_account FROM transactions WHERE account_number = ? ORDER BY timestamp DESC LIMIT ?"
    return _execute_query(query, (account_number, limit), fetch_all=True)

def log_transaction(account_number, type, amount, target=None):
    """Logs a transaction in the history table."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _execute_query(
        "INSERT INTO transactions (account_number, type, amount, target_account, timestamp) VALUES (?, ?, ?, ?, ?)",
        (account_number, type, amount, target, timestamp)
    )

# =========================================================================
# CORE TRANSACTION LOGIC (Agent & Client)
# =========================================================================

def deposit_money(account_number, amount):
    """Deposits money to an account."""
    if not _execute_query("SELECT account_number FROM accounts WHERE account_number = ?", (account_number,), fetch_one=True):
        return "Account Not Found"
        
    query = "UPDATE accounts SET balance = balance + ? WHERE account_number = ?"
    if _execute_query(query, (amount, account_number)) is not False:
        log_transaction(account_number, 'Deposit', amount)
        return True
    return False

def withdraw_money(account_number, amount):
    """Withdraws money from an account."""
    current_balance = get_balance(account_number)
    
    if current_balance is None:
        return "Account Not Found"
    
    if current_balance < amount:
        return "Insufficient Funds"
        
    query = "UPDATE accounts SET balance = balance - ? WHERE account_number = ?"
    if _execute_query(query, (amount, account_number)) is not False:
        log_transaction(account_number, 'Withdrawal', amount)
        return True
    return False

def transfer_money(source_acc, target_acc, amount):
    """Transfers money between two accounts."""
    if source_acc == target_acc:
        return "Cannot transfer to the same account."
        
    # Check source account
    source_balance = get_balance(source_acc)
    if source_balance is None:
        return "Source Account Not Found"
    if source_balance < amount:
        return "Insufficient Funds"
        
    # Check target account
    if get_balance(target_acc) is None:
        return "Target Account Not Found"

    # Transaction: Deduct from source and add to target (Wrapped in a single transaction for safety)
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # 1. Deduct from source
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_number = ?", (amount, source_acc))

        # 2. Add to target
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_number = ?", (amount, target_acc))

        conn.commit()

        # 3. Log transactions
        log_transaction(source_acc, 'Transfer Out', amount, target_acc)
        log_transaction(target_acc, 'Transfer In', amount, source_acc)
        
        return True
    except sqlite3.Error as e:
        print(f"Transfer Database Error (Rollback attempted): {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# =========================================================================
# SAVINGS/INVESTMENT LOGIC
# =========================================================================

def save_money(account_number, amount):
    """Moves money from main account to savings account."""
    main_balance = get_balance(account_number)
    
    if main_balance is None:
        return "Account Not Found"
        
    if main_balance < amount:
        return "Insufficient Funds"
        
    # Deduct from main, add to savings
    deduct_main_query = "UPDATE accounts SET balance = balance - ? WHERE account_number = ?"
    add_savings_query = "UPDATE accounts SET savings_balance = savings_balance + ? WHERE account_number = ?"
    
    if _execute_query(deduct_main_query, (amount, account_number)) is False: return False
    if _execute_query(add_savings_query, (amount, account_number)) is False: return False
    
    log_transaction(account_number, 'Save/Invest', amount)
    return True

def withdraw_savings(account_number, amount):
    """Moves money from savings account back to main account."""
    savings_balance = get_savings_balance(account_number)
    
    if savings_balance is None:
        return "Account Not Found"
        
    if savings_balance < amount:
        return "Insufficient Savings Funds"
        
    # Deduct from savings, add to main
    deduct_savings_query = "UPDATE accounts SET savings_balance = savings_balance - ? WHERE account_number = ?"
    add_main_query = "UPDATE accounts SET balance = balance + ? WHERE account_number = ?"
    
    if _execute_query(deduct_savings_query, (amount, account_number)) is False: return False
    if _execute_query(add_main_query, (amount, account_number)) is False: return False
    
    log_transaction(account_number, 'Withdraw Savings', amount)
    return True

def apply_monthly_interest(account_number):
    """Applies a 30% interest rate to the savings account."""
    savings_balance = get_savings_balance(account_number)
    
    if savings_balance is None:
        return "Account Not Found"
    
    if savings_balance == 0.0:
        return "No Balance to Apply Interest"
        
    interest_amount = savings_balance * INTEREST_RATE
    new_savings_balance = savings_balance + interest_amount
    
    query = "UPDATE accounts SET savings_balance = ? WHERE account_number = ?"
    
    if _execute_query(query, (new_savings_balance, account_number)) is not False:
        log_transaction(account_number, 'Interest', interest_amount)
        return interest_amount
    else:
        return "Database Error"

# =========================================================================
# AIRTIME PURCHASE LOGIC
# =========================================================================

def buy_airtime(account_number, amount, phone_number):
    """Deducts airtime cost from the main account and logs the purchase."""
    current_balance = get_balance(account_number)
    
    if current_balance is None:
        return "Account Not Found"
    
    if current_balance < amount:
        return "Insufficient Funds"
        
    # Deduct amount from main account
    query = "UPDATE accounts SET balance = balance - ? WHERE account_number = ?"
    if _execute_query(query, (amount, account_number)) is not False:
        # Log transaction with phone number as the target
        log_transaction(account_number, 'Airtime', amount, phone_number)
        return True
    return False

# Example setup call (optional, but good for testing)
if __name__ == '__main__':
    setup()
