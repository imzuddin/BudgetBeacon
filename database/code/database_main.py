from database_initialisation import DataBase


def main():
    db = DataBase(
        db_name="postgres", db_host="postgres", db_user="temp", db_pass="temp"
    )
    db.init_db()


if __name__ == "__main__":
    main()

    while True:
        pass
