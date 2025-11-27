from flask import g, current_app, has_app_context, has_request_context
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Global placeholders
engine = None
Session = None

def create_db_engine():
    """
    Create a SQLAlchemy engine connected to the SQLite database with foreign keys enabled.
    Sets up a scoped session for Flask and a thread-safe session factory.
    """
    global engine, Session

    #Determine database name
    db_name = "parkinsons_data.db"
    if has_app_context():
        db_name = current_app.config.get("DB_NAME", db_name)

    engine = create_engine(f"sqlite:///{db_name}", echo=True)

    # Enable SQLite foreign keys
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    # Create session factory
    SessionFactory = sessionmaker(bind=engine)
    Session = scoped_session(SessionFactory) # Flask request-safe session
    return engine

def create_tables():
    """Create all tables in the database if they do not exist."""
    global engine
    if engine is None:
        create_db_engine()
    Base.metadata.create_all(engine)

def get_db_session():
    """
    Get a SQLAlchemy session tied to Flask's g context.
    - Uses Flask's g context if in request.
    - Otherwise returns a normal session for CLI scripts.
    """
    global Session

    # Initialize database if not already done
    if Session is None:
        create_db_engine()

    if has_request_context():
        if 'db_session' not in g:
            g.db_session = Session()
        return g.db_session
    else:
        # No Flask request context; return a regular session
        return Session()

def close_db_session(e=None):
    """
    Close the SQLAlchemy session.
    - In Flask request: pop from g.
    - In scripts: must be closed manually.
    """

    if has_request_context():
        db_session = g.pop('db_session', None)
        if db_session:
            db_session.close()

def has_full_data():
    """Check if the database has data in patients, variants, and patient_variant tables."""
    session = get_db_session()

    try:
        tables = ['patients', 'variants', 'patient_variant', 'genes']
        for table_name in tables:
            count = session.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
            if count == 0:
                return False
        return True
    finally:
        if not has_request_context():
            session.close()
