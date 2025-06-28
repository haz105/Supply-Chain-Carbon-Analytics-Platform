from database.connection import get_db_session
from sqlalchemy import text

def clear_tables():
    session = get_db_session()
    try:
        session.execute(text('TRUNCATE TABLE carbon_emissions RESTART IDENTITY CASCADE;'))
        session.execute(text('TRUNCATE TABLE shipments RESTART IDENTITY CASCADE;'))
        session.commit()
        print("✅ Tables cleared successfully.")
    except Exception as e:
        print(f"❌ Error clearing tables: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    clear_tables() 