import psycopg2
# this is bankaccount project
class BankAccount:
    def __init__(self, account_number, account_holder=None, balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance

    def get_connection(self):
        return psycopg2.connect(
            dbname="test",
            user="postgres",
            password="Welcome@123",
            host="localhost",
            port="5432"
        )

    # ✅ CREATE ACCOUNT
    def create_account(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        """
                        INSERT INTO acc_info (accountholder_name, accountnumber, amount)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (accountnumber) DO NOTHING
                        RETURNING accountnumber
                        """,
                        (self.account_holder, self.account_number, self.balance)
                    )

                    result = cur.fetchone()

                    if result is None:
                        return "Account already exists"

                    return "Account created successfully"

        except Exception as e:
            return f"Error: {e}"


    # ✅ DEPOSIT
    def deposit(self, amount):
        if amount <= 0:
            return "Deposit amount must be positive"

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        """
                        UPDATE acc_info
                        SET amount = amount + %s
                        WHERE accountnumber = %s
                        RETURNING amount
                        """,
                        (amount, self.account_number)
                    )

                    result = cur.fetchone()

                    if result is None:
                        return "Account does not exist"

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

                    cur.execute(
                        """
                        UPDATE acc_info
                        SET amount = amount - %s
                        WHERE accountnumber = %s AND amount >= %s
                        RETURNING amount
                        """,
                        (amount, self.account_number, amount)
                    )

                    result = cur.fetchone()

                    if result is None:
                        # Need to distinguish reason
                        cur.execute(
                            "SELECT 1 FROM acc_info WHERE accountnumber = %s",
                            (self.account_number,)
                        )
                        if cur.fetchone() is None:
                            return "Account does not exist"
                        else:
                            return "Insufficient balance"

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