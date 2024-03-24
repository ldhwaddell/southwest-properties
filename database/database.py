from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


from models import Base


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.session = sessionmaker(bind=self.engine)

    def create_tables(self):
        # This will create the tables if they don't exist, based on the models defined in Base's subclasses
        Base.metadata.create_all(self.engine)

    def show_tables(self):
        inspector = inspect(self.engine)

        # inspector = Inspector.from_engine(self.engine)
        tables = inspector.get_table_names()

        print(f"Tables in the database: {tables}")


# Example usage
if __name__ == "__main__":
    db = Database("sqlite:///southwest.db")
    db.create_tables()
