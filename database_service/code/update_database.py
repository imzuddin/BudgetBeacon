import os
from budget_database import BudgetDatabase

def init_walkthrough_db(db_host='postgres'):
    try:
        db = BudgetDatabase(os.environ.get("POSTGRES_DB"),
                            os.environ.get("POSTGRES_USER"),
                            os.environ.get("POSTGRES_PASSWORD"),
                            db_hostname=db_host)
        db.create_db_tables()
    except Exception as e:
        print("Error")

if __name__ == '__main__':
    init_walkthrough_db()