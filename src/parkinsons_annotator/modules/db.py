from flask import g, current_app
from sqlalchemy import create_engine, event, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from .modules.models import Base

# Global placeholders
engine = None
Session = None

def create_db_engine():
    """Create a SQLAlchemy engine connected to the SQLite database with foreign keys enabled."""
    global engine, Session
    db_name = current_app.config.get("DB_NAME", "parkinsons_data.db")
    engine = create_engine(f"sqlite:///{db_name}", echo=True)

    # Enable SQLite foreign keys
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    # Create session factory
    SessionFactory = sessionmaker(bind=engine)
    Session = scoped_session(SessionFactory)
    return engine

def create_tables():
    """Create all tables in the database if they do not exist."""
    global engine
    if engine is None:
        create_db_engine()
    Base.metadata.create_all(engine)

def get_db_session():
    """Get a SQLAlchemy session tied to Flask's g context."""
    if 'db_session' not in g:
        g.db_session = Session()
    return g.db_session

def close_db_session(e=None):
    """Close the SQLAlchemy session."""
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.close()

def has_full_data():
    """Check if the database has data in patients, variants, and patient_variant tables."""
    session = get_db_session()
    tables = ['patients', 'variants', 'patient_variant']
    for table_name in tables:
        count = session.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
        if count == 0:
            return False
    return True
