import logging
from sqlalchemy import text
from config import engine, Base

logger = logging.getLogger(__name__)

def drop_absence_tables():
    """Drop all absence-related tables from the database"""
    try:
        # List of absence-related tables to drop
        absence_tables = [
            'hours_request',
            'approval_first_hour',
            'approval_second_hour',
            'approval_final_hour',
            'approval_done_hour',
            'approval_process_hour'
        ]
        
        with engine.connect() as conn:
            for table in absence_tables:
                try:
                    # Check if table exists before dropping
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    logger.info(f"Dropped table {table}")
                except Exception as e:
                    logger.warning(f"Error dropping table {table}: {e}")
        
        logger.info("Absence tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping absence tables: {e}")
        raise

def migrate_database():
    """Perform necessary database migrations"""
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(engine)
        logger.info("Database tables created or verified")
    except Exception as e:
        logger.error(f"Error during database migration: {e}")
        raise

def main():
    try:
        logger.info("Starting database migration...")
        
        # First drop absence-related tables
        drop_absence_tables()
        
        # Then create/verify remaining tables
        migrate_database()
        
        logger.info("Database migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    main()
