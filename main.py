from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.image import Image
import database # Crucial: Imports the separate database.py file

# Global app reference for dialogs and state
app = None
# Global variable to store the logged-in client's account number
CURRENT_CLIENT_ACCOUNT = ""

## 1. KIVYMD DESIGN LANGUAGE (KV)

KV = '''
#:set NORM_WIDTH 1.2
#:set NORM_POS {'center_x': 0.5, 'center_y': 0.65}
#:set BUTTON_SIZE 0.45
#:set INPUT_WIDTH 0.8 

## HOME SCREEN (Main Navigation Window)

<HomeScreen>:
    name: 'home'
    
    FloatLayout:
        MDBoxLayout:
            orientation: 'vertical'
            padding: "40dp"
            spacing: "30dp"
            size_hint_x: NORM_WIDTH 
            height: self.minimum_height
            pos_hint: NORM_POS 
            
            # Placeholder for bank_logo.png (Ensure this file exists!)
            Image:
                source: 'bank_logo.png'  
                size_hint_y: None
                height: "150dp"
                allow_stretch: True
                keep_ratio: True
            
            MDLabel:
                text: "SMB BANK"
                font_style: "H3"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                
            MDGridLayout:
                cols: 2
                spacing: "20dp"
                padding: "10dp"
                size_hint_y: None
                height: self.minimum_height
                
                ## CORE NAVIGATION (The 4 main options)
                
                MDRaisedButton:
                    text: "Create Account"
                    on_release: root.manager.current = 'create_account'
                    size_hint_x: BUTTON_SIZE
                
                MDRaisedButton:
                    text: "Client Login"
                    on_release: root.manager.current = 'client_verify'
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Agent Login"
                    on_release: root.manager.current = 'agent_verify'
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Admin Login"
                    on_release: root.manager.current = 'admin_verify'
                    size_hint_x: BUTTON_SIZE
            
            ## EXIT BUTTON HERE
            
            MDTextButton:
                text: "Exit"
                on_release: root.stop_app()
                pos_hint: {'center_x': 0.5}

## GENERIC LOGIN SCREEN

<LoginScreen>:
    login_id_input: login_id_input
    password_input: password_input
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: root.screen_title
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: login_id_input
            hint_text: root.id_hint_text
            mode: "rectangle"
            required: True
            max_text_length: 20
            input_type: 'number' if root.name in ['client_verify', 'agent_verify'] else 'text'

        MDTextField:
            id: password_input
            hint_text: "Password"
            mode: "rectangle"
            password: True
            required: True
            max_text_length: 50
            
        MDRaisedButton:
            text: "Login"
            size_hint_x: 1
            on_release: root.verify_login()

        MDTextButton:
            text: "Back to Home"
            on_release: root.manager.current = 'home'
            pos_hint: {'center_x': 0.5}

## CLIENT ACTION SCREEN (New Hub for Client)

<ClientActionScreen>:
    name: 'client_actions'
    # NEW PROPERTY BINDING
    current_balance_text: current_balance_text 
    
    FloatLayout:
        MDBoxLayout:
            orientation: 'vertical'
            padding: "40dp"
            spacing: "30dp"
            size_hint_x: NORM_WIDTH 
            height: self.minimum_height
            pos_hint: NORM_POS 
            
            MDLabel:
                text: f"Welcome, Account {root.account_number}"
                font_style: "H4"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
            
            ## NEW BALANCE DISPLAY
            
            MDLabel:
                id: current_balance_text
                text: "Fetching balance..." 
                font_style: "H6"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]

            MDGridLayout:
                cols: 2
                spacing: "10dp"
                padding: "10dp"
                size_hint_y: None
                height: self.minimum_height
                
                ## Client Actions
                
                MDRaisedButton:
                    text: "Send Money (Transfer)"
                    on_release: root.prepare_action('transfer')
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Save/Invest Money"
                    on_release: root.prepare_action('save_invest')
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Check Balance"
                    on_release: root.prepare_action('balance')
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Buy Airtime"
                    on_release: root.prepare_action('buy_airtime')
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "History Transaction"
                    on_release: root.prepare_action('history')
                    size_hint_x: BUTTON_SIZE
                    
                MDRaisedButton:
                    text: "Change Password"
                    on_release: root.prepare_action('change_password')
                    size_hint_x: BUTTON_SIZE
                    
            MDTextButton:
                text: "Apply Monthly Interest (30%)"
                on_release: root.apply_interest()
                pos_hint: {'center_x': 0.5}
            
            MDTextButton:
                text: "Logout"
                on_release: root.logout()
                pos_hint: {'center_x': 0.5}

## NEW: SAVE/INVEST SCREEN

<SaveScreen>:
    name: 'save_invest'
    account_number_input: account_number_input
    amount_input: amount_input
    savings_balance_output: savings_balance_output

    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Save/Invest Money"
            font_style: "H5"
            halign: "center"
            
        MDLabel:
            id: savings_balance_output
            text: "Savings Balance: Fetching..." 
            font_style: "H6"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            
        MDTextField:
            id: account_number_input
            hint_text: "Your Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            readonly: True

        MDTextField:
            id: amount_input
            hint_text: "Amount"
            mode: "rectangle"
            input_type: 'number'
            input_filter: 'float'
            required: True
            max_text_length: 10

        MDRaisedButton:
            text: "Move to Savings (Save)"
            size_hint_x: 1
            on_release: root.process_save()
            
        MDRaisedButton:
            text: "Withdraw from Savings"
            size_hint_x: 1
            md_bg_color: app.theme_cls.error_color
            on_release: root.process_withdraw()

        MDTextButton:
            text: "Back to Actions"
            on_release: root.manager.current = 'client_actions'
            pos_hint: {'center_x': 0.5}

## NEW: AIRTIME SCREEN

<AirtimeScreen>:
    name: 'buy_airtime'
    account_number_input: account_number_input
    amount_input: amount_input
    phone_number_input: phone_number_input

    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Buy Airtime"
            font_style: "H5"
            halign: "center"

        MDTextField:
            id: account_number_input
            hint_text: "Your Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            readonly: True

        MDTextField:
            id: phone_number_input
            hint_text: "Recipient Phone Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 15
            
        MDTextField:
            id: amount_input
            hint_text: "Amount (K)"
            mode: "rectangle"
            input_type: 'number'
            input_filter: 'float'
            required: True
            max_text_length: 10

        MDRaisedButton:
            text: "Purchase Airtime"
            size_hint_x: 1
            on_release: root.process_airtime_purchase()

        MDTextButton:
            text: "Back to Actions"
            on_release: root.manager.current = 'client_actions'
            pos_hint: {'center_x': 0.5}


## CREATE ACCOUNT SCREEN

<CreateAccountScreen>:
    name: 'create_account'
    first_name_input: first_name_input
    second_name_input: second_name_input
    phone_number_input: phone_number_input 
    deposit_input: deposit_input

    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: NORM_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Create New Account"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: first_name_input
            hint_text: "First Name"
            mode: "rectangle"
            required: True
            max_text_length: 50

        MDTextField:
            id: second_name_input
            hint_text: "Last Name"
            mode: "rectangle"
            required: True
            max_text_length: 50
            
        MDTextField: 
            id: phone_number_input
            hint_text: "Phone Number (e.g., 096/097xxxxxxx)"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 15
            
        MDTextField:
            id: deposit_input
            hint_text: "Initial Deposit (Min K10.00)"
            mode: "rectangle"
            input_type: 'number'
            input_filter: 'float' 
            required: True
            max_text_length: 10

        MDRaisedButton:
            text: "Create Account"
            size_hint_x: 1
            on_release: root.submit_account()

        MDTextButton:
            text: "Back to Home"
            on_release: root.manager.current = 'home'
            pos_hint: {'center_x': 0.5}

## GENERIC TRANSACTION SCREEN TEMPLATE

<TransactionScreen>:
    account_number_input: account_number_input
    amount_input: amount_input
    target_account_input: target_account_input if self.name == 'transfer' else None
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: root.screen_title
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: account_number_input
            hint_text: "Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            # Read-only if the user is logged in as client or agent is using it
            readonly: True if root.is_client_action or root.name in ['deposit', 'withdraw'] else False

        MDTextField:
            id: amount_input
            hint_text: "Amount"
            mode: "rectangle"
            input_type: 'number'
            input_filter: 'float'
            required: True
            max_text_length: 10
            
        MDTextField:
            id: target_account_input
            hint_text: "Recipient Account Number"
            mode: "rectangle"
            input_type: 'number'
            max_text_length: 10
            size_hint_y: 0 if root.name != 'transfer' else None
            height: "0dp" if root.name != 'transfer' else "48dp"

        MDRaisedButton:
            text: root.button_text
            size_hint_x: 1
            on_release: root.process_transaction()
        
        ## Back button logic is safe here as it doesn't use current_screen
        
        MDTextButton:
            text: "Back to Actions" if root.is_client_action else ("Back to Account" if root.name in ['deposit', 'withdraw'] else "Back to Home")
            on_release: 
                root.manager.current = 'client_actions' if root.is_client_action else \
                ('account_details' if root.name in ['deposit', 'withdraw'] else 'home')
            pos_hint: {'center_x': 0.5}

## BALANCE SCREEN

<BalanceScreen>:
    name: 'balance'
    account_number_input: account_number_input
    balance_output: balance_output
    is_client_action: False
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Check Balance"
            font_style: "H5"
            halign: "center"

        MDTextField:
            id: account_number_input
            hint_text: "Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            readonly: True if root.is_client_action else False

        MDLabel:
            id: balance_output
            text: ""
            halign: "center"
            size_hint_y: None
            height: "48dp"
            
        MDRaisedButton:
            text: "Get Balance"
            on_release: root.check_balance()
            
        MDTextButton:
            text: "Back to Actions" if root.is_client_action else "Back to Home"
            on_release: root.manager.current = 'client_actions' if root.is_client_action else 'home'
            pos_hint: {'center_x': 0.5}

## HISTORY SCREEN

<HistoryScreen>:
    name: 'history'
    account_number_input: account_number_input
    history_list: history_list
    is_client_action: False
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_x: 0.9
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        
        MDLabel:
            text: "Transaction History"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: account_number_input
            hint_text: "Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            readonly: True if root.is_client_action else False

        MDRaisedButton:
            text: "Show History"
            on_release: root.show_history()
            size_hint_y: None
            height: "48dp"

        ScrollView:
            MDList:
                id: history_list
        
        MDTextButton:
            text: "Back to Actions" if root.is_client_action else "Back"
            on_release: root.navigate_back()
            pos_hint: {'center_x': 0.5}

## CHANGE PASSWORD SCREEN

<ChangePasswordScreen>:
    name: 'change_password'
    account_number_input: account_number_input
    old_password_input: old_password_input
    new_password_input: new_password_input
    is_client_action: False

    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Change Password"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: account_number_input
            hint_text: "Your Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            readonly: True if root.is_client_action else False
            
        MDTextField:
            id: old_password_input
            hint_text: "Current Password"
            mode: "rectangle"
            password: True
            required: True
            max_text_length: 50

        MDTextField:
            id: new_password_input
            hint_text: "New Password"
            mode: "rectangle"
            password: True
            required: True
            max_text_length: 50
            
        MDRaisedButton:
            text: "Submit Change"
            size_hint_x: 1
            on_release: root.submit_change()

        MDTextButton:
            text: "Back to Actions" if root.is_client_action else "Back to Home"
            on_release: root.manager.current = 'client_actions' if root.is_client_action else 'home'
            pos_hint: {'center_x': 0.5}
            
## AGENT RESET PASSWORD SCREEN (NEW)

<ResetPasswordScreen>:
    name: 'reset_password'
    
    FloatLayout:
        MDBoxLayout:
            orientation: 'vertical'
            padding: "40dp"
            spacing: "20dp"
            size_hint: (0.9, 0.7)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

            MDLabel:
                text: "Agent Password Reset"
                font_style: 'H5'
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                
            MDTextField:
                id: account_number_input
                hint_text: "Client Account Number"
                mode: "rectangle"
                input_type: 'number'
                max_text_length: 10
                size_hint_x: INPUT_WIDTH
                pos_hint: {'center_x': 0.5}

            MDTextField:
                id: new_password_input
                hint_text: "New Password"
                password: True
                mode: "rectangle"
                size_hint_x: INPUT_WIDTH
                pos_hint: {'center_x': 0.5}

            MDTextField:
                id: confirm_password_input
                hint_text: "Confirm New Password"
                password: True
                mode: "rectangle"
                size_hint_x: INPUT_WIDTH
                pos_hint: {'center_x': 0.5}
            
            MDGridLayout:
                cols: 2
                spacing: "10dp"
                size_hint_x: INPUT_WIDTH
                pos_hint: {'center_x': 0.5}

                MDRaisedButton:
                    text: "Reset Password"
                    on_release: root.submit_reset(account_number_input.text, new_password_input.text, confirm_password_input.text)
                    md_bg_color: app.theme_cls.primary_color

                MDRaisedButton:
                    text: "Back to Agent Actions"
                    on_release: app.root.current = 'agent_actions'
                    md_bg_color: 0.5, 0.5, 0.5, 1 # Gray color


## Login Screen Definitions using inheritance

<AdminVerifyScreen@LoginScreen>:
    name: 'admin_verify'
    screen_title: "Admin Login"
    id_hint_text: "Admin ID"

<AgentVerifyScreen@LoginScreen>:
    name: 'agent_verify'
    screen_title: "Agent Login"
    id_hint_text: "Agent ID"

<ClientVerifyScreen@LoginScreen>:
    name: 'client_verify'
    screen_title: "Client Login"
    id_hint_text: "Account Number"

## Transaction Screen Definitions using inheritance

<DepositScreen@TransactionScreen>:
    name: 'deposit'
    screen_title: "Deposit Money (Agent Only)"
    button_text: "Deposit"
    is_client_action: False
    
<WithdrawScreen@TransactionScreen>:
    name: 'withdraw'
    screen_title: "Withdraw Money (Agent Only)"
    button_text: "Withdraw"
    is_client_action: False

<TransferScreen@TransactionScreen>:
    name: 'transfer'
    screen_title: "Transfer Money"
    button_text: "Transfer"
    is_client_action: True
    
## AGENT ACTION SCREEN

<AgentActionScreen>:
    name: 'agent_actions'
    account_number_input: account_number_input
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Agent Panel"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            
        MDTextField:
            id: account_number_input
            hint_text: "Customer Account Number"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10

        MDRaisedButton:
            text: "View Account Details"
            size_hint_x: 1
            on_release: root.view_account_details()
            
        ## NEW BUTTON ADDED FOR PASSWORD RESET
        
        MDRaisedButton:
            text: "RESET CLIENT PASSWORD"
            size_hint_x: 1
            on_release: root.manager.current = 'reset_password'
            
        MDTextButton:
            text: "Logout"
            on_release: root.manager.current = 'home'
            pos_hint: {'center_x': 0.5}

## ACCOUNT DETAILS SCREEN

<AccountDetailsScreen>:
    name: 'account_details'
    details_list: details_list
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_x: 0.9
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        
        MDLabel:
            text: "Customer Account Details"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
        
        ScrollView:
            MDList:
                id: details_list
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: '10dp'
            size_hint_y: None
            height: "48dp"
            padding: (0, '10dp', 0, 0)

            MDRaisedButton:
                text: "Deposit"
                on_release: root.do_agent_deposit()
                size_hint_x: 0.5

            MDRaisedButton:
                text: "Withdraw"
                on_release: root.do_agent_withdraw()
                size_hint_x: 0.5

            
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: '10dp'
            size_hint_y: None
            height: "48dp"
            padding: (0, '10dp', 0, 0)

            MDRaisedButton:
                text: "Full History"
                on_release: root.view_full_history()
                size_hint_x: 0.5
                
            MDRaisedButton:
                text: "Back to Agent Panel"
                on_release: root.manager.current = 'agent_actions'
                size_hint_x: 0.5

## ADMIN PANEL SCREEN

<AdminPanelScreen>:
    name: 'admin'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Admin Panel"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]

        MDRaisedButton:
            text: "View All Accounts"
            size_hint_x: 1
            on_release: root.view_all_accounts()
            
        MDRaisedButton:
            text: "Delete Customer Account"
            size_hint_x: 1
            on_release: root.manager.current = 'delete_account' 
            
        MDRaisedButton:
            text: "Audit Logs"
            size_hint_x: 1
            on_release: root.audit_logs_action()
            
        MDTextButton:
            text: "Logout"
            on_release: root.manager.current = 'home'
            pos_hint: {'center_x': 0.5}

## ALL ACCOUNTS SCREEN (ADMIN)

<AllAccountsScreen>:
    name: 'all_accounts'
    accounts_list: accounts_list
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "20dp"
        size_hint_x: 0.95
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        
        MDLabel:
            text: "All Bank Accounts"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
        
        ScrollView:
            MDList:
                id: accounts_list
        
        MDTextButton:
            text: "Back to Admin Panel"
            on_release: root.manager.current = 'admin'
            pos_hint: {'center_x': 0.5}

## DELETE ACCOUNT SCREEN (ADMIN)

<DeleteAccountScreen>:
    name: 'delete_account'
    account_number_input: account_number_input

    MDBoxLayout:
        orientation: 'vertical'
        padding: "40dp"
        spacing: "20dp"
        size_hint_y: None
        height: self.minimum_height
        size_hint_x: INPUT_WIDTH
        pos_hint: NORM_POS
        
        MDLabel:
            text: "Delete Customer Account"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            
        MDLabel:
            text: "WARNING: This action is irreversible and will remove all account and transaction data."
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Error"

        MDTextField:
            id: account_number_input
            hint_text: "Account Number to Delete"
            mode: "rectangle"
            input_type: 'number'
            required: True
            max_text_length: 10
            
        MDRaisedButton:
            text: "DELETE ACCOUNT"
            md_bg_color: app.theme_cls.error_color
            size_hint_x: 1
            on_release: root.confirm_delete()

        MDTextButton:
            text: "Back to Admin Panel"
            on_release: root.manager.current = 'admin'
            pos_hint: {'center_x': 0.5}
'''

## 2. PYTHON SCREEN CLASSES AND LOGIC

## DIALOG HELPER

class DialogWrapper:
    dialog = None

    def show_dialog(self, title, text, on_dismiss_callback=None):
        if self.dialog:
            self.dialog.dismiss()
        
        buttons = [
            MDFlatButton(
                text="OK", 
                on_release=lambda x: self._dismiss_and_callback(on_dismiss_callback)
            )
        ]
        
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=buttons
        )
        
        ## FIX: Schedule the open() call for the next frame
        
        Clock.schedule_once(lambda dt: self.dialog.open(), 0)

    def _dismiss_and_callback(self, callback):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if callback:
            
            ## Schedule callback to ensure it runs after dialog dismissal is complete
            
            Clock.schedule_once(lambda dt: callback(), 0) 

## CORE SCREENS

class HomeScreen(Screen):
    
    ## NEW: Method to stop the application
    
    def stop_app(self):
        MDApp.get_running_app().stop()
        
class PlaceholderScreen(Screen):
    screen_title = StringProperty("Screen")


## LOGIN / ADMIN / AGENT / CLIENT CLASSES

class LoginScreen(Screen):
    screen_title = StringProperty("Login")
    id_hint_text = StringProperty("Login ID")
    login_id_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    
    def on_enter(self, *args):
        
        ## Clear fields when screen is entered
        
        if self.login_id_input: self.login_id_input.text = ""
        if self.password_input: self.password_input.text = ""

    def verify_login(self):
        login_id = self.login_id_input.text.strip()
        password = self.password_input.text.strip()
        
        if not login_id:
            app.show_dialog("Error", f"{self.id_hint_text} is required.")
            return
            
        if not password:
            app.show_dialog("Error", "Password is required.")
            return

        if self.name == 'admin_verify' or self.name == 'agent_verify':
            
            role = 'Admin' if self.name == 'admin_verify' else 'Agent'
            
            ## Use the secure database verification for staff
            
            if database.verify_staff_login(login_id, password, role):
                target_screen = 'admin' if role == 'Admin' else 'agent_actions'
                app.show_dialog("Success", f"{role} login successful!", lambda *args: setattr(self.manager, 'current', target_screen))
            else:
               app.show_dialog("Error", f"Invalid {role} credentials.")
        
        elif self.name == 'client_verify':
            
            ## Client login now uses the secure database verification
            
            ##1. Check if the account exists and the password is correct
            
            if database.verify_client_login(login_id, password):
                global CURRENT_CLIENT_ACCOUNT
                CURRENT_CLIENT_ACCOUNT = login_id
                
                client_action_screen = self.manager.get_screen('client_actions')
                client_action_screen.account_number = login_id
                
                ## Fetch details for welcome message
                
                account_details = database.get_account_details(login_id)
                first_name = account_details[1] if account_details else "Client"
                
                app.show_dialog("Success", f"Welcome, {first_name}!", lambda *args: setattr(self.manager, 'current', 'client_actions'))
            else:
                app.show_dialog("Error", "Invalid Account Number or Password. Please create an account or try again.")

## Specific Login Classes

class AdminVerifyScreen(LoginScreen): pass
class AgentVerifyScreen(LoginScreen): pass
class ClientVerifyScreen(LoginScreen): pass


## CLIENT ACTION SCREEN LOGIC

class ClientActionScreen(Screen):
    account_number = StringProperty("")
    
    ## NEW PROPERTY
    
    current_balance_text = ObjectProperty(None)

    def on_enter(self, *args):
        global CURRENT_CLIENT_ACCOUNT
        
        ## Complete the on_enter logic to set the account and refresh the balance
        
        if CURRENT_CLIENT_ACCOUNT:
            self.account_number = CURRENT_CLIENT_ACCOUNT
            self.update_balance_display()
        else:
            
            ## Safety check: if somehow not logged in, go back home
            
            self.manager.current = 'home'
    
    def update_balance_display(self):
        """Fetches and updates the balance label."""
        balance = database.get_balance(self.account_number)
        if balance is not None:
            self.current_balance_text.text = f"Current Balance: K{balance:,.2f}"
        else:
            self.current_balance_text.text = "Error fetching balance."
            
    ## NEW: Apply Interest function
    
    def apply_interest(self):
        result = database.apply_monthly_interest(self.account_number)
        
        if isinstance(result, float): 
        
            ## Update main balance just in case a future feature requires it, but mainly a dialog.
            
            self.update_balance_display() 
            app.show_dialog("Interest Applied", f"Monthly interest of K{result:,.2f} (30%) applied to your savings account!", lambda *args: self.prepare_action('save_invest')) 
            ## Go to save screen to see new balance
            
        elif result == "No Balance to Apply Interest":
            app.show_dialog("Info", "Your savings balance is zero, no interest applied.")
        else:
            app.show_dialog("Error", "Failed to apply interest. Account not found or database error.")

    def prepare_action(self, screen_name):
        """Pre-fills the account number and navigates to the selected action screen."""
        screen = self.manager.get_screen(screen_name)
        screen.is_client_action = True
        
        if hasattr(screen, 'account_number_input'):
            screen.account_number_input.text = self.account_number
            
        if screen_name == 'balance':
            
            ## Note: The balance screen's check_balance() handles both pre-filled and manual checks
            
            screen.check_balance()
        elif screen_name == 'history':
            
            ## The history screen's show_history() handles both pre-filled and manual checks
            
            screen.show_history()
        elif screen_name == 'change_password':
            
            ## Pre-fill for change password screen
            
            screen.account_number_input.text = self.account_number
        elif screen_name == 'save_invest':
            screen.update_savings_balance()
        elif screen_name == 'buy_airtime':
            if hasattr(screen, 'amount_input'): screen.amount_input.text = ""
            if hasattr(screen, 'phone_number_input'): screen.phone_number_input.text = ""
        else:
            if hasattr(screen, 'amount_input'): screen.amount_input.text = ""
            if hasattr(screen, 'target_account_input'): screen.target_account_input.text = ""
            
        self.manager.current = screen_name

    def logout(self):
        global CURRENT_CLIENT_ACCOUNT
        CURRENT_CLIENT_ACCOUNT = ""
        self.account_number = ""
        self.manager.current = 'home'

## SAVE SCREEN LOGIC

class SaveScreen(Screen):
    account_number_input = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    savings_balance_output = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        
        ## Clear fields and update balance when screen is entered
        
        if self.amount_input: self.amount_input.text = ""
        self.update_savings_balance()

    def update_savings_balance(self):
        acc_num = self.account_number_input.text.strip()
        if acc_num:
            balance = database.get_savings_balance(acc_num)
            if balance is not None:
                self.savings_balance_output.text = f"Savings Balance: K{balance:,.2f}"
            else:
                self.savings_balance_output.text = "Error fetching balance."
        else:
        	self.savings_balance_output.text = "Savings Balance: N/A"

    def _get_amount(self):
        amount_text = self.amount_input.text.strip()
        if not amount_text:
            app.show_dialog("Error", "Amount is required.")
            return None
        try:
            amount = float(amount_text)
            if amount <= 0:
                app.show_dialog("Error", "Amount must be greater than zero.")
                return None
            return amount
        except ValueError:
            app.show_dialog("Error", "Invalid amount.")
            return None

    def _handle_result(self, result, success_title, success_text):
        if result is True:
            self.amount_input.text = ""
            
            ## Update current screen display
            
            self.update_savings_balance()
            
            ## Update main client action screen display
            
            self.manager.get_screen('client_actions').update_balance_display() 
            app.show_dialog(success_title, success_text)
        elif result in ["Insufficient Funds", "Insufficient Savings Funds"]:
            app.show_dialog("Error", f"Transaction failed: {result.replace('Funds', ' funds')}.")
        elif "Account Not Found" in result:
            app.show_dialog("Error", f"Transaction failed: {result}.")
        else:
            app.show_dialog("Error", "Transaction failed due to a database error.")

    def process_save(self):
        acc_num = self.account_number_input.text.strip()
        amount = self._get_amount()
        if amount is None: return

        result = database.save_money(acc_num, amount)
        self._handle_result(result, "Save Successful", f"K{amount:,.2f} moved to Savings/Investment.")

    def process_withdraw(self):
        acc_num = self.account_number_input.text.strip()
        amount = self._get_amount()
        if amount is None: return

        result = database.withdraw_savings(acc_num, amount)
        self._handle_result(result, "Withdrawal Successful", f"K{amount:,.2f} moved from Savings/Investment to your main account.")

## AIRTIME SCREEN LOGIC

class AirtimeScreen(Screen):
    account_number_input = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    phone_number_input = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        if self.amount_input: self.amount_input.text = ""
        if self.phone_number_input: self.phone_number_input.text = ""

    def process_airtime_purchase(self):
        acc_num = self.account_number_input.text.strip()
        phone_number = self.phone_number_input.text.strip()
        amount_text = self.amount_input.text.strip()

        if not all([acc_num, phone_number, amount_text]):
            app.show_dialog("Error", "All fields are required.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                app.show_dialog("Error", "Amount must be greater than zero.")
                return
        except ValueError:
            app.show_dialog("Error", "Invalid amount.")
            return

        ## Basic phone number validation (just checks length)
        
        if not phone_number.isdigit() or len(phone_number) < 8:
            app.show_dialog("Error", "Invalid phone number.")
            return

        result = database.buy_airtime(acc_num, amount, phone_number)
        
        if result is True:
            self.amount_input.text = ""
            self.phone_number_input.text = ""
            
            ## Update main client action screen display
            
            self.manager.get_screen('client_actions').update_balance_display() 
            app.show_dialog("Purchase Successful", f"K{amount:,.2f} airtime sent to {phone_number}.")
        elif result == "Insufficient Funds":
            app.show_dialog("Error", "Purchase failed: Insufficient funds.")
        elif result == "Account Not Found":
            app.show_dialog("Error", "Purchase failed: Account not found.")
        else:
            app.show_dialog("Error", "Purchase failed due to a database error.")


## CREATE ACCOUNT SCREEN

class CreateAccountScreen(Screen):
    first_name_input = ObjectProperty(None)
    second_name_input = ObjectProperty(None)
    phone_number_input = ObjectProperty(None)
    deposit_input = ObjectProperty(None)

    def on_enter(self, *args):
        if self.first_name_input: self.first_name_input.text = ""
        if self.second_name_input: self.second_name_input.text = ""
        if self.phone_number_input: self.phone_number_input.text = ""
        if self.deposit_input: self.deposit_input.text = ""

    def submit_account(self):
        first_name = self.first_name_input.text.strip()
        second_name = self.second_name_input.text.strip()
        phone_number = self.phone_number_input.text.strip()
        deposit_text = self.deposit_input.text.strip()

        if not all([first_name, second_name, phone_number, deposit_text]):
            app.show_dialog("Error", "All fields are required.")
            return
            
        try:
            initial_deposit = float(deposit_text)
            if initial_deposit < 10.00:
                app.show_dialog("Error", "Minimum initial deposit is K10.00.")
                return
        except ValueError:
            app.show_dialog("Error", "Invalid deposit amount. Ensure you use numbers and a dot for decimals.") 
            return

        new_account_number = database.create_new_account(
            first_name, 
            second_name, 
            phone_number, 
            initial_deposit
        )

        if new_account_number:
            self.first_name_input.text = ""
            self.second_name_input.text = ""
            self.phone_number_input.text = "" 
            self.deposit_input.text = ""
            app.show_dialog(
                "Success!", 
                f"Account created for {first_name} {second_name}.\nYour account number is: {new_account_number}\n\nYour temporary password is your account number. Please change it immediately.", 
                lambda *args: setattr(self.manager, 'current', 'home')
            )
        else:
            app.show_dialog("Error", "Failed to create account. Check database connection/initialization.")

## TRANSACTION LOGIC

class TransactionScreen(Screen):
    screen_title = StringProperty("Transaction")
    button_text = StringProperty("Submit")
    account_number_input = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    target_account_input = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        if self.amount_input: self.amount_input.text = ""
        if self.target_account_input: self.target_account_input.text = ""

    def _handle_result(self, result, success_title, success_text, success_screen):
        if result is True:
            
            ## Clear amount/target fields after successful transaction
            
            if self.amount_input: self.amount_input.text = ""
            if self.target_account_input: self.target_account_input.text = ""
            
            ## If Client action, update the client's balance display
            
            if self.is_client_action:
                self.manager.get_screen('client_actions').update_balance_display()
            
            app.show_dialog(success_title, success_text, lambda *args: setattr(self.manager, 'current', success_screen))
        elif result == "Insufficient Funds":
            app.show_dialog("Error", "Transaction failed: Insufficient funds.")
        elif result == "Source Account Not Found":
            app.show_dialog("Error", "Transaction failed: Source account not found.")
        elif result == "Target Account Not Found":
            app.show_dialog("Error", "Transaction failed: Target account not found.")
        elif result == "Account Not Found": 
        
        ## Used by deposit/withdraw/save/airtime if acc_num is missing
        
             app.show_dialog("Error", "Transaction failed: Account not found.")
        elif result == "Cannot transfer to the same account.":
            app.show_dialog("Error", result)
        elif result is False:
            app.show_dialog("Error", "Transaction failed due to a database error.")
        else:
            app.show_dialog("Error", "An unknown error occurred.")
    
    def process_transaction(self):
        account_number = self.account_number_input.text.strip() if self.account_number_input else ""
        amount_text = self.amount_input.text.strip() if self.amount_input else ""
        
        success_screen = 'client_actions' if self.is_client_action else ('account_details' if self.name in ['deposit', 'withdraw'] else 'home')
        
        if not all([account_number, amount_text]):
            app.show_dialog("Error", "Account and Amount fields are required.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                app.show_dialog("Error", "Amount must be greater than zero.")
                return
        except ValueError:
            app.show_dialog("Error", "Invalid amount. Ensure you use numbers and a dot for decimals.")
            return

        if self.name == 'deposit':
            result = database.deposit_money(account_number, amount)
            self._handle_result(result, "Deposit Successful", f"K{amount:,.2f} deposited to account {account_number}.", success_screen)
        elif self.name == 'withdraw':
            result = database.withdraw_money(account_number, amount)
            self._handle_result(result, "Withdrawal Successful", f"K{amount:,.2f} withdrawn from account {account_number}.", success_screen)
        elif self.name == 'transfer':
            target_account = self.target_account_input.text.strip()
            if not target_account:
                app.show_dialog("Error", "Recipient Account Number is required for transfer.")
                return
            result = database.transfer_money(account_number, target_account, amount)
            self._handle_result(result, "Transfer Successful", f"K{amount:,.2f} transferred from {account_number} to {target_account}.", success_screen)

class DepositScreen(TransactionScreen): pass
class WithdrawScreen(TransactionScreen): pass
class TransferScreen(TransactionScreen): pass

## BALANCE SCREEN

class BalanceScreen(Screen):
    account_number_input = ObjectProperty(None)
    balance_output = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        
        ## Clear fields only if not pre-filled by client action screen
        
        if not self.is_client_action and self.account_number_input: self.account_number_input.text = ""
        if self.balance_output: self.balance_output.text = ""

    def check_balance(self):
        account_number = self.account_number_input.text.strip() if self.account_number_input else ""
        
        ## Original logic retained: If the account number is pre-filled (client access) and already checked, don't re-check
        
        if self.is_client_action and self.balance_output.text and self.balance_output.text != "Error fetching balance.": 
            return

        if not account_number:
            app.show_dialog("Error", "Account Number is required.")
            return

        balance = database.get_balance(account_number)
        
        if balance is not None:
            self.balance_output.text = f"Current Balance:\nK{balance:,.2f}"
            
            ## If balance is checked manually from home screen, show success dialog
            
            if not self.is_client_action:
                 app.show_dialog("Balance Check", f"Account {account_number} balance is K{balance:,.2f}.")
        else:
            self.balance_output.text = "Account not found."
            app.show_dialog("Error", f"Account {account_number} not found.")

## HISTORY SCREEN

class HistoryScreen(Screen):
    account_number_input = ObjectProperty(None)
    history_list = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        if not self.is_client_action and self.history_list:
            self.history_list.clear_widgets()

    def show_history(self):
        account_number = self.account_number_input.text.strip() if self.account_number_input else ""
        
        if not account_number:
            app.show_dialog("Error", "Account Number is required.")
            return

        history = database.get_transaction_history(account_number, limit=20)
        self.history_list.clear_widgets()

        if history:
            self.history_list.add_widget(
                OneLineListItem(text="Date/Time | Type | Amount | Target", theme_text_color='Secondary')
            )
            for item in history:
                timestamp, type, amount, target = item
                
                ## Format for display
                
                prefix = "+" if type in ['Deposit', 'Transfer In', 'Interest', 'Withdraw Savings'] else "-"
                
                if type == 'Transfer Out':
                    details = f" to {target}" if target else ""
                    display_type = 'Transfer Out'
                elif type == 'Transfer In':
                    details = f" from {target}" if target else ""
                    display_type = 'Transfer In'
                elif type == 'Airtime':
                    details = f" to {target}" if target else ""
                    display_type = 'Airtime Purchase'
                elif type == 'Save/Invest':
                    details = " to Savings"
                    display_type = 'Save/Invest'
                elif type == 'Withdraw Savings':
                    details = " from Savings"
                    display_type = 'Withdraw Savings'
                elif type == 'Password_Reset':
                    details = " (Agent Action)"
                    display_type = 'Password Reset'
                    prefix = ""
                else:
                    details = ""
                    display_type = type ## Should not happen, but safe fallback
                
                text = f"{timestamp[:16]} | {display_type}: {prefix}K{amount:,.2f}{details}"
                self.history_list.add_widget(
                    OneLineListItem(
                        text=text,
                        theme_text_color='Primary'
                    )
                )
        else:
            self.history_list.add_widget(
                OneLineListItem(text="No transactions found for this account.")
            )

    ## NEW METHOD TO HANDLE BACK BUTTON NAVIGATION
    
    def navigate_back(self):
        
        """Custom back navigation based on context (Client vs. Agent)."""
        
        if self.is_client_action:
            self.manager.current = 'client_actions'
        elif self.manager.has_screen('account_details') and self.manager.get_screen('account_details').current_account_number:
            self.manager.current = 'account_details'
        else:
            self.manager.current = 'home'

## CHANGE PASSWORD SCREEN

class ChangePasswordScreen(Screen):
    account_number_input = ObjectProperty(None)
    old_password_input = ObjectProperty(None)
    new_password_input = ObjectProperty(None)
    is_client_action = BooleanProperty(False)

    def on_enter(self, *args):
        
        ## Only clear account number if it's NOT a client action (which pre-fills it)
        
        if not self.is_client_action:
            if self.account_number_input: self.account_number_input.text = ""
            
        ## Always clear password fields
        
        if self.old_password_input: self.old_password_input.text = ""
        if self.new_password_input: self.new_password_input.text = ""

    def submit_change(self):
        account_number = self.account_number_input.text.strip()
        old_password = self.old_password_input.text.strip()
        new_password = self.new_password_input.text.strip()

        if not all([account_number, old_password, new_password]):
            app.show_dialog("Error", "All fields are required.")
            return

        ## Use the updated database function
        
        result = database.change_password(account_number, old_password, new_password)
        
        success_screen = 'client_actions' if self.is_client_action else 'home'

        if result is True:
            
            ## FIX: If changing password from client screen, clear global credentials to force re-login
            
            if self.is_client_action:
                global CURRENT_CLIENT_ACCOUNT
                CURRENT_CLIENT_ACCOUNT = "" ## Logs the client out
                success_screen = 'client_verify' ## Force user back to client login
                app.show_dialog("Success", "Password changed successfully! Please log in again with your new password.", lambda *args: setattr(self.manager, 'current', success_screen))
            else:
            	app.show_dialog("Success", "Password changed successfully!", lambda *args: setattr(self.manager, 'current', success_screen))
        elif result == "Invalid Old Password":
            app.show_dialog("Error", "Password change failed: Invalid current password or account number.")
        else:
            app.show_dialog("Error", "An unknown error occurred during password change.")
            
## AGENT RESET PASSWORD SCREEN LOGIC (NEW)

class ResetPasswordScreen(Screen):
    def submit_reset(self, account_number, new_password, confirm_password):
        account_number = account_number.strip()
        new_password = new_password.strip()
        confirm_password = confirm_password.strip()

        if not account_number or not new_password or not confirm_password:
            app.show_dialog("Error", "All fields are required.")
            return

        if new_password != confirm_password:
            app.show_dialog("Error", "New Password and Confirm Password do not match.")
            return

        ## Call the new database function
        
        result = database.agent_reset_password(account_number, new_password)

        if result is True:
            
            ## Clear fields (assuming IDs are set in KV)
            
            self.manager.get_screen('reset_password').ids.account_number_input.text = ""
            self.manager.get_screen('reset_password').ids.new_password_input.text = ""
            self.manager.get_screen('reset_password').ids.confirm_password_input.text = ""
            app.show_dialog("Success", f"Password for account {account_number} reset successfully! The client can now log in with the new password.", lambda *args: setattr(self.manager, 'current', 'agent_actions'))
        else:
            app.show_dialog("Error", f"Password reset failed: {result}")


## AGENT ACTION SCREENS

class AgentActionScreen(Screen):
    account_number_input = ObjectProperty(None)
    
    def view_account_details(self):
        account_number = self.account_number_input.text.strip()
        if not account_number:
            app.show_dialog("Error", "Please enter a Customer Account Number.")
            return
            
        details = database.get_account_details(account_number)
        
        if details:
            details_screen = self.manager.get_screen('account_details')
            details_screen.display_details(details)
            self.manager.current = 'account_details'
        else:
            app.show_dialog("Error", f"Account Number {account_number} not found.")

class AccountDetailsScreen(Screen):
    details_list = ObjectProperty(None)
    current_account_number = StringProperty("")
    
    def display_details(self, details):
        
        ## The structure is: (acc_num, first_name, last_name, phone_number, balance, created_at)
        
        acc_num, first_name, last_name, phone_number, balance, created_at = details
        
        self.current_account_number = str(acc_num)
        self.details_list.clear_widgets()
        self.details_list.add_widget(OneLineListItem(text=f"Account Number: {acc_num}"))
        self.details_list.add_widget(OneLineListItem(text=f"Name: {first_name} {last_name}"))
        self.details_list.add_widget(OneLineListItem(text=f"Phone Number: {phone_number}"))
        self.details_list.add_widget(OneLineListItem(text=f"Balance: K{balance:,.2f}"))
        self.details_list.add_widget(OneLineListItem(text=f"Created: {created_at[:16]}"))

    def _prepare_transaction_screen(self, screen_name):
        if not self.current_account_number:
            app.show_dialog("Error", "No account loaded for transaction.")
            return False
            
        trans_screen = self.manager.get_screen(screen_name)
        trans_screen.is_client_action = False
        trans_screen.account_number_input.text = self.current_account_number
        if hasattr(trans_screen, 'amount_input'): trans_screen.amount_input.text = ""
        return True

    def do_agent_deposit(self):
        if self._prepare_transaction_screen('deposit'):
            self.manager.current = 'deposit'

    def do_agent_withdraw(self):
        if self._prepare_transaction_screen('withdraw'):
            self.manager.current = 'withdraw'

    def view_full_history(self):
        if self.current_account_number:
            history_screen = self.manager.get_screen('history')
            history_screen.account_number_input.text = self.current_account_number
            history_screen.is_client_action = False
            ## Schedule show_history call to ensure screen properties are updated
            
            Clock.schedule_once(lambda dt: history_screen.show_history(), 0.1) 
            self.manager.current = 'history'
        else:
            app.show_dialog("Error", "No account loaded for history.")

## ADMIN ACTION SCREENS

class AdminPanelScreen(Screen):
    def view_all_accounts(self):
        all_accounts = database.get_all_accounts()
        all_acc_screen = self.manager.get_screen('all_accounts')
        all_acc_screen.display_accounts(all_accounts)
        self.manager.current = 'all_accounts'
        
    def audit_logs_action(self):
        """Displays a dialog for the unimplemented audit feature."""
        app.show_dialog("Info", "Audit Logs not yet implemented.")

class AllAccountsScreen(Screen):
    accounts_list = ObjectProperty(None)
    
    def display_accounts(self, accounts):
        self.accounts_list.clear_widgets()
        
        if accounts:
            self.accounts_list.add_widget(
                OneLineListItem(text="Account No: | Name | Phone | Balance | Created", theme_text_color='Secondary')
            )
            for acc in accounts:
                acc_num, first_name, last_name, phone_number, balance, created_at = acc
                text = f"{acc_num} | {first_name} {last_name} | {phone_number} | K{balance:,.2f} | {created_at[:10]}"
                self.accounts_list.add_widget(
                    OneLineListItem(text=text)
                )
        else:
            self.accounts_list.add_widget(
                OneLineListItem(text="No accounts found in the database.")
            )

class DeleteAccountScreen(Screen):
    account_number_input = ObjectProperty(None)
    
    def on_enter(self, *args):
        if self.account_number_input: self.account_number_input.text = ""

    def confirm_delete(self):
        account_number = self.account_number_input.text.strip()
        
        if not account_number:
            app.show_dialog("Error", "Please enter the Account Number to delete.")
            return

        def delete_confirmed(instance):
            result = database.delete_account(account_number)
            if result is True:
                app.show_dialog("Success", f"Account {account_number} and all transactions have been deleted.")
                self.account_number_input.text = ""
            elif result == "Account Not Found":
                app.show_dialog("Error", f"Account {account_number} not found.")
            else:
                app.show_dialog("Error", "Database error during deletion.")

        app.dialog = MDDialog(
            title="Confirm Deletion",
            text=f"Are you sure you want to permanently delete account: {account_number}? This cannot be undone.",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: app.dialog.dismiss()),
                MDRaisedButton(text="DELETE", md_bg_color=MDApp.get_running_app().theme_cls.error_color, on_release=lambda x: [app.dialog.dismiss(), delete_confirmed(x)])
            ]
        )
        
        ## Apply the fix for the confirmation dialog as well
        
        Clock.schedule_once(lambda dt: app.dialog.open(), 0) 

## 3. APP CLASS AND MAIN EXECUTION

class SmbBankApp(MDApp, DialogWrapper):

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Pink"
        self.theme_cls.theme_style = "Dark" ## Optional: For a modern dark theme
        global app
        app = self
        
        ## Build the KV layout
        screen_manager = Builder.load_string(KV)
        
        ## Manually add screens
        sm = ScreenManager(transition=FadeTransition())
        
        ## Home and Create
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CreateAccountScreen(name='create_account'))
        
        ## Client Screens
        sm.add_widget(ClientVerifyScreen(name='client_verify')) 
        sm.add_widget(ClientActionScreen(name='client_actions'))
        
        ## Admin/Agent Screens
        sm.add_widget(AdminVerifyScreen(name='admin_verify'))
        sm.add_widget(AdminPanelScreen(name='admin'))
        sm.add_widget(AccountDetailsScreen(name='account_details')) 
        sm.add_widget(AgentVerifyScreen(name='agent_verify'))
        sm.add_widget(AgentActionScreen(name='agent_actions'))
        sm.add_widget(AllAccountsScreen(name='all_accounts'))
        sm.add_widget(DeleteAccountScreen(name='delete_account'))

        ## Transaction Screens
        sm.add_widget(DepositScreen(name='deposit'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(TransferScreen(name='transfer'))
        sm.add_widget(BalanceScreen(name='balance')) 
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(ChangePasswordScreen(name='change_password'))
        
        ## NEW SCREENS
        sm.add_widget(SaveScreen(name='save_invest')) 
        sm.add_widget(AirtimeScreen(name='buy_airtime'))
        
        ## NEW AGENT RESET PASSWORD SCREEN
        
        sm.add_widget(ResetPasswordScreen(name='reset_password'))

        return sm

if __name__ == '__main__':
    try:
        
        ## NOTE: Ensure you run database.py once before running main.py 
        ## or ensure 'database.py' is in the same directory.
        
        database.setup() 
    except ImportError:
        print("ERROR: Could not import 'database.py'. Ensure the file is present in the same directory.")
        exit()
    except AttributeError as e:
         print(f"ERROR: The 'database.py' file seems incomplete or has missing functions: {e}")
         exit()
         
    SmbBankApp().run()
