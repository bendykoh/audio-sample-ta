from app.db.database import engine
from sqlalchemy import inspect, text


def test_connection():
    try:
        # Test the connection
        with engine.connect() as connection:
            print("Successfully connected to the database!")

            # Get all table names
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")

            # For each table, show row count
            for table in tables:
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))  # noqa: E501
                count = result.scalar()
                print(f"\nNumber of rows in {table}: {count}")

    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")


if __name__ == "__main__":
    test_connection()
