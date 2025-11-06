import psycopg2


class DataBase:
    def __init__(self, db_name, db_user, db_pass, db_host):
        self.conn = psycopg2.connect(
            database=db_name, user=db_user, password=db_pass, host=db_host
        )

    def init_db(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS moneyAccounts (
                            moneyAccountID INTEGER PRIMARY KEY generated always as IDENTITY,
                            moneyInAccount REAL, 
                            dateCreated DATE,
                            accountActive BOOLEAN
                        )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS budgets (
                            budgetID INTEGER PRIMARY KEY generated always as IDENTITY,
                            budgetType VARCHAR,
                            bugetName VARCHAR,
                            bugetYear DATE,
                            money_account_id INTEGER REFERENCES moneyAccounts(moneyAccountID) ON DELETE CASCADE
                        )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS budgetTargets (
                            budgetTargetID INTEGER PRIMARY KEY generated always as IDENTITY,
                            budgetTargetName VARCHAR,
                            budgetTargetMonth VARCHAR,
                            budgetTargetAmount REAL,
                            budget_id INTEGER REFERENCES budgets(budgetID) ON DELETE CASCADE
                        )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS budgetEntries (
                            budgetEntryID INTEGER PRIMARY KEY generated always as IDENTITY,
                            budgetEntryName VARCHAR,
                            budgetEntryNotes TEXT,
                            budgetEntryAmount REAL,
                            budgetEntryDate DATE,
                            budget_target_id INTEGER REFERENCES budgetTargets(budgetTargetID) ON DELETE CASCADE
                        )"""
            )
            self.conn.commit()

    def modify_db(self, db_name, modification):
        pass
