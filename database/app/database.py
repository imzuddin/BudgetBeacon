import uuid
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from rich.logging import RichHandler
import logging
from models import Base


class BudgetBeaconDatabase:
    def __init__(
        self,
        logger,
        db_name,
        db_username,
        db_password,
        db_hostname="postgres",
        db_port="5432",
    ):
        self.engine = create_engine(
            f"postgresql+psycopg2://{db_username}:{db_password}@localhost:{db_port}/{db_hostname}",
            echo=False,
            future=True,
        )

        self.logger = logger
        self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def test_connection(self) -> bool:
        session_local = self.session()

        try:
            # Run a dummy query
            session_local.execute(sqlalchemy.text("SELECT 1"))
            self.logger.info(
                "[green] ✅ - Database connection [bold]Successful![/bold][/]"
            )
            return True
        except SQLAlchemyError as e:
            self.logger.error(
                f"[red] ❌ - Database connection [bold]Failed[/bold]: {e}[/]"
            )
            return False
        finally:
            session_local.close()

    def create_tables(self) -> bool:
        Base.metadata.create_all(self.engine)
        self.logger.info("[green]✅ - Table creation [bold] Successful! [/bold][/]")

    def delete_tables(self) -> bool:
        Base.metadata.drop_all(self.engine)
        self.logger.warning("[red]⚠️ - All tables [bold] Dropped! [/bold]![/]")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[RichHandler(markup=True)])

    logger = logging.getLogger("database")
    db = BudgetBeaconDatabase(logger, None, "admin", "admin")
    try:
        db.test_connection()
        db.create_tables()
    except Exception as e:
        raise (f"Error: {e}")
