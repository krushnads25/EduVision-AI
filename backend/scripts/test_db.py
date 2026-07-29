from app.database import session
from sqlalchemy import text
import traceback

def main():
    try:
        with session.engine.connect() as conn:
            r = conn.execute(text('SELECT 1'))
            print('DB_OK', list(r))
    except Exception as e:
        traceback.print_exc()
        print('DB_ERR', str(e))

if __name__ == '__main__':
    main()
