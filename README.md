# Name: MOSES PHIRI
# Student number: 2023053332
# Intake Jan 2024
# Institution: Rockview University 

📘 SMB BANK – Mobile Banking System (KivyMD + SQLite)

SMB Bank is a fully functional mobile banking application built using Python, KivyMD, and SQLite.
It allows clients, agents, and administrators to perform secure banking operations such as:

Creating accounts

Logging in with hashed passwords

Deposits & Withdrawals

Transfers

Savings/Investment

Airtime purchases

Admin management (view/delete accounts)

Agent password reset

Transaction history logging

Interest application (30% monthly)


This README provides a full guide on installation, configuration, project structure, features, and usage.

📂 Project Structure

SMB_BANK
│── main.py               # Main KivyMD Application
│── database.py           # SQLite database handler and all backend logic
│── smb_bank.db           # Auto-generated SQLite database
│── bank_logo.png         # App logo (required)
│── README.md             # Documentation

🧰 Technologies Used

Component	Technology

UI Framework	KivyMD
Core Language	Python 3
Database	SQLite
Password Security	SHA-256 hashing
Transaction Logging	Custom SQLite logs

📦 Features Overview

👤 Client Features

Create new account with:

Auto-generated 5-digit account number

Initial deposit minimum K10

Auto-generated initial password (same as account number)

Login with hashed password

View real-time balance

Send money (transfer)

Save/Invest money

Withdraw savings back to main account

Buy Airtime

Check transaction history

Change password (forces logout)

Receive monthly savings interest (30%)

🧑‍💻 Agent Features

Agents log in using pre-configured staff credentials.

Default agent accounts:

ID: 100 | Password: 456

ID: 200 | Password: 456

ID: 300 | Password: 456

Agent actions:

View client account details

Deposit or withdraw on behalf of clients

View full transaction history

Reset client password (logged as a transaction)

🛡️ Admin Features

Default admin account:

ID: admin

Password: admin123

Admin actions:

View all accounts in the database

Delete customer accounts (with transactions)

View audit logs (coming soon)

🏦 Database System

The database contains three main tables:

✔️ accounts

Stores all customer account information:

Column	Description

account_number	5-digit unique ID
first_name	Customer first name
last_name	Customer last name
phone_number	Mobile number
password_hash	SHA-256 encrypted password
balance	Main account balance
savings_balance	Savings/Investment balance
created_at	Timestamp

✔️ transactions

Stores every transaction:

Deposits

Withdrawals

Transfers

Savings

Airtime

Interest

Password resets

✔️ staff

Stores admins and agents with passwords.

⚙️ Installation Guide

📱 Option 1 — Running on Android (Termux + Ubuntu)

1. Install Termux

Download from F-Droid (recommended).

2. Install Ubuntu in Termux

Use proot-distro:

pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

3. Install Python + Kivy dependencies

apt update
apt install python3 python3-pip
pip install kivy kivymd

4. Copy your project files into Ubuntu

Place main.py and database.py inside a folder.

5. Run database initialization

python3 database.py

6. Run the app

python3 main.py

💻 Option 2 — Running on PC (Windows/Linux)

Install dependencies:

pip install kivy kivymd

Run:

python main.py

🔐 Security Features

✔️ Passwords are hashed using SHA-256

No raw passwords stored.

✔️ Failed login attempts handled with error messages

Client, agent, and admin validations are separate.

✔️ Agents cannot view or change admin accounts

Role-based logic enforced.

✔️ Every action is logged

ALL transactions (including password resets) are stored.

📊 Core Banking Logic

✔️ Deposits

Adds money to account balance.

✔️ Withdrawals

Checks available balance before subtracting.

✔️ Transfers

Cannot transfer to same account

Validates both accounts

Logs both transfer-in and transfer-out

✔️ Savings & Investment

Customers can:

Save money from main → savings

Withdraw money from savings → main

Apply monthly interest (30%)

All savings are logged

🧾 Transaction Types Logged

Type	Description

Deposit	Client or agent deposit
Withdrawal	Client or agent withdrawal
Transfer Out	Sent money
Transfer In	Received money
Save/Invest	Moved money to savings
Withdraw Savings	Moved money back to main
Interest	Monthly savings interest
Airtime	Bought airtime
Password_Reset	Agent resets password

🖼️ UI Screens Overview

Included Screens:

Home Screen

Create Account

Client Login

Client Action Dashboard

Admin Login

Agent Login

Deposit/Withdraw

Transfer Money

Savings/Investment

Airtime Purchase

Change Password

Transaction History

All Accounts (Admin)

Account Details (Agent)

Delete Account (Admin)

Agent Reset Password

🚀 How to Use the App

1. Run the application

python main.py

2. Home Screen options:

Create Account

Client Login

Agent Login

Admin Login

3. Follow the prompts

The app guides each user type through appropriate workflows.

🧪 Testing the App

Test Login Credentials

Role	ID	Password

Admin	admin	admin123
Agent	100	456
Agent	200	456
Agent	300	456
Client	Auto-created	Account Number

📝 Future Improvements

Planned upgrades:

Implement audit logs for admin
Add mobile money integrations
Improve UI animations

Export transaction history to PDF

Add email/SMS notifications

🧑‍💻 Author

Developed by: SINAI (SMB TEAM)
Platform: Python + KivyMD Banking App

✍🏻 Conclusion

This system provides a complete mini-banking platform with:

✔ Secure authentication
✔ Full transaction management
✔ Agent/Admin control
✔ Savings and investment logic
✔ Clean UI using KivyMD
✔ SQLite backend with logging
