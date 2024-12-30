import psycopg
from psycopg import sql

class BudgetDatabase:
    def __init__(self, logger, db_name, db_username, db_password, db_port, db_hostname='localhost'):
        self.logger = logger 

        print(f"DB Name: {db_name}")
        print(f"DB User: {db_username}")
        print(f"DB Port: {db_password}")
        print(f"DB Port: {db_port}")
        print(f"DB Hostname: {db_hostname}")

        self.db_hostname = db_hostname
        self.db_name = db_name
        self.db_username = db_username
        self.db_password = db_password
        self.db_port = db_port

        self.conn = psycopg.Connection.connect(f"""
            host={self.db_hostname}
            port={self.db_port}
            dbname={self.db_name}
            user={self.db_username}
            password={self.db_password}
        """)

        print(self.conn)

        self.cur = psycopg.ClientCursor(self.conn)
        self.budget_table = "budget_table"

        print(self.cur)
    
    def create_db_tables(self):
        self.drop_all_tables()
        self.create_users_table()
        self.create_budget_table()
        self.create_projects_table()
        self.create_categories_table()
        self.create_transaction_table()
        self.create_counter_party_table()
        self.create_debts_table()
        self.create_bridge_budget_categories_table()
        self.create_bridge_project_categories_table()
        #self.create_aggregation_core_table()
        #self.create_aggregation_debt_table()
        #self.create_aggregation_budget_table()
        #self.create_aggregation_transacion_table()

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

    def create_projects_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS projects (
                project_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                target_amount NUMERIC(10, 2) NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('in-progress', 'complete')),
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "projects")


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
                counter_party VARCHAR(50) NOT NULL REFERENCES counter_party(party_id),
                amount NUMERIC(10, 2) NOT NULL,
                is_owed BOOLEAN NOT NULL,
                due_date TIMESTAMP,
                description VARCHAR(500),
                status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'paid', 'canceled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "debts")

    def create_counter_party_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS counter_party (
                party_id VARCHAR(50) PRIMARY KEY,
                payment_method VARCHAR(10) NOT NULL CHECK (payment_method IN ('e-transfer', 'debit', 'credit')),
                email VARCHAR(50)
            )
        """
        self._execute_command(command, "counter_party")

    def create_categories_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(500),
                parent_id INTEGER REFERENCES categories(category_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "categories")

    def create_bridge_budget_categories_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS budget_categories (
                budget_category_id SERIAL PRIMARY KEY,
                budget_id INTEGER NOT NULL REFERENCES budgets(budget_id),
                category_id INTEGER NOT NULL REFERENCES categories(category_id),
                amount NUMERIC(10, 2) NOT NULL,
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "budget_categories")

    def create_bridge_project_categories_table(self):
        command = """
            CREATE TABLE IF NOT EXISTS project_categories (
                project_category_id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(project_id),
                category_id INTEGER NOT NULL REFERENCES categories(category_id),
                amount NUMERIC(10, 2) NOT NULL,
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self._execute_command(command, "project_categories")
    def _execute_command(self, command, table_name):
        """Helper function to execute SQL commands with error handling."""
        try:
            self.cur.execute(command)
            self.conn.commit()
            print(f"Table '{table_name}' created successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating table '{table_name}': {e}")

    def drop_all_tables(self):
        """Drops all tables in the connected PostgreSQL database."""
        try:
            # Query to get all table names
            query = """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public';
            """
            self.cur.execute(query)
            tables = self.cur.fetchall()

            # Generate DROP TABLE statements for each table
            for table in tables:
                table_name = table[0]
                print(f"Dropping table: {table_name}")
                self.cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

            self.conn.commit()
            print("All tables dropped successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error dropping tables: {e}")