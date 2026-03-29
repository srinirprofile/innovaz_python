# same project in snowflake
# !pip install snowflake-connector-python

import snowflake.connector

class BankAccount:
    def __init__(self, account_number, account_holder=None, balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance

    def get_connection(self):
        return snowflake.connector.connect(
            user='SRINIVASTABDEV',
            password='Srinivastabdev@2026',
            account='huc54422.us-east-1',   # e.g. abc-xyz.snowflakecomputing.com
            warehouse='COMPUTE_WH',
            database='python_project_db',
            schema='PUBLIC'
        )

    # ✅ CREATE ACCOUNT (Using MERGE instead of ON CONFLICT)
    def create_account(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(f"""
                        MERGE INTO acc_info t
                        USING (SELECT '{self.account_number}' AS accountnumber) s
                        ON t.accountnumber = s.accountnumber
                        WHEN NOT MATCHED THEN
                            INSERT (accountnumber, accountholder_name, amount)
                            VALUES ('{self.account_number}', '{self.account_holder}', {self.balance})
                    """)

                    # Check if inserted
                    cur.execute(
                        "SELECT COUNT(*) FROM acc_info WHERE accountnumber = %s",
                        (self.account_number,)
                    )
                    result = cur.fetchone()

                    if result[0] == 1:
                        return "Account created successfully"
                    else:
                        return "Account already exists"

        except Exception as e:
            return f"Error: {e}"

    # ✅ DEPOSIT
    def deposit(self, amount):
        if amount <= 0:
            return "Deposit amount must be positive"

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute("""
                        UPDATE acc_info
                        SET amount = amount + %s
                        WHERE accountnumber = %s
                    """, (amount, self.account_number))

                    if cur.rowcount == 0:
                        return "Account does not exist"

                    # Fetch updated balance
                    cur.execute(
                        "SELECT amount FROM acc_info WHERE accountnumber = %s",
                        (self.account_number,)
                    )
                    result = cur.fetchone()

                    return f"Deposit successful. New balance: {result[0]}"

        except Exception as e:
            return f"Error: {e}"

    # ✅ WITHDRAW
    def withdraw(self, amount):
        if amount <= 0:
            return "Withdrawal amount must be positive"

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute("""
                        UPDATE acc_info
                        SET amount = amount - %s
                        WHERE accountnumber = %s AND amount >= %s
                    """, (amount, self.account_number, amount))

                    if cur.rowcount == 0:
                        # Check reason
                        cur.execute(
                            "SELECT amount FROM acc_info WHERE accountnumber = %s",
                            (self.account_number,)
                        )
                        result = cur.fetchone()

                        if result is None:
                            return "Account does not exist"
                        else:
                            return "Insufficient balance"

                    # Fetch updated balance
                    cur.execute(
                        "SELECT amount FROM acc_info WHERE accountnumber = %s",
                        (self.account_number,)
                    )
                    result = cur.fetchone()

                    return f"Withdrawal successful. New balance: {result[0]}"

        except Exception as e:
            return f"Error: {e}"

    # ✅ CHECK BALANCE
    def check_balance(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        "SELECT amount FROM acc_info WHERE accountnumber = %s",
                        (self.account_number,)
                    )

                    result = cur.fetchone()

                    if result is None:
                        return "Account does not exist"

                    return f"Account balance: {result[0]}"

        except Exception as e:
            return f"Error: {e}"