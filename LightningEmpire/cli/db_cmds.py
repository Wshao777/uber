import typer
from sqlalchemy import create_engine, text
import pathlib

# Define the path to the database and schema relative to this script
DB_DIR = pathlib.Path(__file__).parent.parent / "db"
DB_PATH = DB_DIR / "lightning_empire.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

db_app = typer.Typer()

def translate_to_sqlite(sql_script: str) -> str:
    """Translates PostgreSQL specific syntax in a SQL script to SQLite compatible syntax."""
    return (
        sql_script.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        .replace("DECIMAL(10,2)", "REAL")
        .replace("NOW()", "CURRENT_TIMESTAMP")
        .replace("JSONB", "TEXT")
    )

@db_app.command("init")
def init_db(
    db_type: str = typer.Option("sqlite", "--db", help="The type of database to initialize (e.g., 'sqlite', 'postgres').")
):
    """
    Initializes the database by creating tables from schema.sql.
    """
    if db_type.lower() != "sqlite":
        print(f"Error: Currently, only 'sqlite' is supported. You provided '{db_type}'.")
        raise typer.Exit(code=1)

    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")

        with open(SCHEMA_PATH, "r") as f:
            schema_sql = f.read()

        # Translate to SQLite compatible SQL
        sqlite_sql = translate_to_sqlite(schema_sql)

        # Split into individual statements
        statements = [s.strip() for s in sqlite_sql.split(';') if s.strip()]

        with engine.connect() as connection:
            # Execute each statement individually
            for statement in statements:
                connection.execute(text(statement))

        print(f"✅ Database '{DB_PATH.name}' initialized successfully in '{DB_DIR}'.")
        print("Tables created based on schema.sql (with SQLite translation).")

    except FileNotFoundError:
        print(f"Error: Schema file not found at '{SCHEMA_PATH}'")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
        raise typer.Exit(code=1)
