import psycopg2
import ast

with open("url", "r") as file:
    content = file.read()

DATABASE_CONFIG = ast.literal_eval(content)


def get_cursor():
    try:
        connection = psycopg2.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()
        return cursor
    except Exception as e:
        print(f"Error {e}")


def check_validation(cursor):
    with open("key", "r") as f:
        name, key = f.read().split("\n")
    cursor.execute("SELECT CURRENT_DATE;")
    current_time = cursor.fetchone()[0]
    query = """
            SELECT get_validation(
                %s::VARCHAR,
                %s::VARCHAR
            );
        """
    cursor.execute(query, (name, key))
    rows = cursor.fetchall()
    if not rows:
        return False

    return current_time < rows[0][0]
