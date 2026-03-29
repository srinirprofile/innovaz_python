import psycopg2

class BankAccount:
    def __init__(self, account_number, account_holder, balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance

        # Establish connection to PostgreSQL
        self.conn = psycopg2.connect(
            dbname="test",
            user="postgres",
            password="Welcome@123",
            host="localhost",  # or your host
            port="5432"  # or your port
        )
        self.cur = self.conn.cursor()

        # Check if account exists
        self.account_exists = self.check_account_exists()

    def check_account_exists(self):
        # Check if account exists in the database
        self.cur.execute("SELECT COUNT(*) FROM acc_info WHERE accountnumber = %s", (self.account_number,))
        count = self.cur.fetchone()[0]
        return count > 0


    def deposit(self, amount):
        try:
            if self.account_exists:
                if amount > 0:
                    # Fetch the current amount from the database
                    self.cur.execute("SELECT amount FROM acc_info WHERE accountnumber = %s", (self.account_number,))
                    current_amount = self.cur.fetchone()[0]
                    
                    # Update the balance with the fetched amount and the deposit
                    new_balance = current_amount + amount
                    
                    # Update the amount in the database
                    self.cur.execute("UPDATE acc_info SET amount = %s WHERE accountnumber = %s", (new_balance, self.account_number))
                    self.conn.commit()
                    print(f"Deposit of ${amount} successful. New balance: ${new_balance}")
                else:
                    print("Deposit amount must be positive.")
            else:
                print("Account does not exist. Please create an account.")
        finally:
            self.closing()


    def withdraw(self, amount):
        try:            
            if self.account_exists:
                if amount > 0:
                    # Fetch the current amount from the database
                    self.cur.execute("SELECT amount FROM acc_info WHERE accountnumber = %s", (self.account_number,))
                    current_amount = self.cur.fetchone()[0]
                    
                    if amount <= current_amount:
                        # Calculate new balance after withdrawal
                        new_balance = current_amount - amount
                        
                        # Update the amount in the database
                        self.cur.execute("UPDATE acc_info SET amount = %s WHERE accountnumber = %s", (new_balance, self.account_number))
                        self.conn.commit()
                        print(f"Withdrawal of ${amount} successful. New balance: ${new_balance}")
                    else:
                        print("Withdrawal amount exceeds account balance.")
                else:
                    print("Withdrawal amount must be positive.")
            else:
                print("Account does not exist. Please create an account.")
        finally:
            self.closing()


    def check_balance(self):
        try:            
            if self.account_exists:
                # Fetch the amount from the database for the respective account
                self.cur.execute("SELECT amount FROM acc_info WHERE accountnumber = %s", (self.account_number,))
                amount = self.cur.fetchone()[0]
                print(f"Account balance: ${amount}")
            else:
                print("Account does not exist. Please create an account.")
        finally:
            self.closing()

    def create_account(self):
        try:
            if not self.account_exists:
                # Insert new account into the database
                self.cur.execute("INSERT INTO acc_info (accountholder_name,accountnumber, amount) VALUES (%s, %s, %s)", (self.account_holder,self.account_number, self.balance))
                self.conn.commit()
                self.account_exists = True
                print("Account created successfully.")
            else:
                print("Account already exists.")
        finally:
            self.closing()
    def closing(self):
        # Close cursor and connection when object is destroyed
        self.cur.close()
        self.conn.close()
