import psycopg
from psycopg import sql

class BudgetDatabase:
    def __init__(self, logger, db_name, db_username, db_password, db_hostname='postgres'):
        self.logger = logger 
        self.db_hostname = db_hostname
        self.db_name = db_name
        self.db_username = db_username
        self.db_password = db_password

        self.conn = psycopg.Connection.connect(
            host=self.db_hostname,
            database=self.db_name,
            user=self.db_username,
            password=self.db_password
        )

        self.cur = psycopg.ClientCursor(self.conn)
        self.budget_table = "budgets"
    
    def create_db_tables(self):
        self.create_users_table()
        self.create_budget_table()
        self.create_transaction_table()
        self.create_debts_table()
        self.create_categories_table()
        
    def create_users_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                f_name VARCHAR(20) NOT NULL,
                l_name VARCHAR(20) NOT NULL,
                email VARCHAR(50) NOT NULL UNIQUE, 
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "users")

    def create_budget_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS budgets (
                budget_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                total_amount NUMERIC(10, 2) NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "budgets")

    def create_transaction_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                category_id INTEGER NOT NULL REFERENCES categories(category_id),
                amount NUMERIC(10, 2) NOT NULL,
                description VARCHAR(500),
                date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "transactions")

    def create_debts_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS debts (
                debt_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                counter_party VARCHAR(50) NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                is_owed BOOLEAN NOT NULL,
                due_date TIMESTAMP,
                description VARCHAR(500),
                status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'paid', 'canceled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "debts")

    def create_categories_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(500),
                parent_id INTEGER REFERENCES categories(category_id),
                status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "categories")
    
    def _execute_command(self, command, table_name):
        """Helper function to execute SQL commands with error handling."""
        try:
            self.cur.execute(command)
            self.conn.commit()
            self.logger.info(f"Table '{table_name}' created successfully.")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error creating table '{table_name}': {e}")