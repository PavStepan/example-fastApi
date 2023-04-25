import psycopg2
from config import db_config


def get_status_payment(user_id, payment_id):
    sql_status_payment = f"SELECT status from SomeTable.Payments " \
                         f"WHERE userId = {user_id} AND paymentId = '{payment_id}'"
    result = execute_query(sql_status_payment)
    return result


def add_refund(entry):
    sql_query = (f"UPDATE SomeTable.Payments SET status = 'refund', descRefund = '{entry['description']}', "
                 f"refundAmount = {entry['refundAmount']}"
                 f"where paymentId = '{entry['payment_id']}' AND userId = {entry['user_id']}")
    _ = execute_query(sql_query)


def get_price():
    sql_query = "SELECT tariff, price FROM SomeTable.Prices"
    result = execute_query(sql_query)
    return result


def execute_query(sql_query):
    conn = None
    response = None
    try:
        # read connection parameters
        params = db_config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.autocommit = True

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute(sql_query)

        response = cur.fetchall()
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ""
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')
            if response is not None:
                return response
            else:
                return ""
