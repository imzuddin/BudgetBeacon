import os
from budget_database import BudgetDatabase

def init_walkthrough_db(db_host='localhost'):
    try:
        db = BudgetDatabase(None,
                            os.environ.get("POSTGRES_DB"),
                            os.environ.get("POSTGRES_USER"),
                            os.environ.get("POSTGRES_PASSWORD"),
                            os.environ.get("POSTGRES_PORT"),
                            db_hostname=db_host)
        db.create_db_tables()
    except Exception as e:
        print("Error")

if __name__ == '__main__':
    print("Starting DB")
    init_walkthrough_db(os.environ.get("POSTGRES_HOST"))
    print("Done Starting DB")
