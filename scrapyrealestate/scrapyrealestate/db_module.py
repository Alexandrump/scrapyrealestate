import sys, datetime
import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def insert_host_mysql(connection, table_name, data_host, logger):
    query = f"""
    INSERT INTO {table_name} (id, chat_id, group_name, time_refresh, min_price, max_price, urls, so, host_name, connections, first_connection, last_connection)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        data_host['id'], data_host['chat_id'], data_host['group_name'], data_host['refresh'], data_host['min_price'],
        data_host['max_price'], data_host['urls'], data_host['so'], data_host['host_name'], data_host['connections'],
        datetime.datetime.now(), datetime.datetime.now()
    )
    execute_query(connection, query, data)

def query_host_mysql(connection, table_name, data_host, logger):
    query = f"SELECT * FROM {table_name} WHERE chat_id = %s AND group_name = %s"
    cursor = connection.cursor()
    cursor.execute(query, (data_host['chat_id'], data_host['group_name']))
    result = cursor.fetchall()
    return result

def update_host_mysql(connection, table_name, data_host, logger):
    query = f"UPDATE {table_name} SET connections = connections + 1, last_connection = %s WHERE chat_id = %s AND group_name = %s"
    execute_query(connection, query, (datetime.datetime.now(), data_host['chat_id'], data_host['group_name']))

def insert_flat_mysql(connection, table_name, data_flat, logger):
    query = f"""
    INSERT INTO {table_name} (id, price, m2, rooms, floor, town, neighbour, street, number, title, href, type, site, online, datetime)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        data_flat['id'], data_flat['price'], data_flat['m2'], data_flat['rooms'], data_flat['floor'], data_flat['town'],
        data_flat['neighbour'], data_flat['street'], data_flat['number'], data_flat['title'], data_flat['href'],
        data_flat['type'], data_flat['site'], data_flat['online'], datetime.datetime.now()
    )
    execute_query(connection, query, data)

def query_flat_mysql(connection, table_name, data_flat, logger):
    query = f"SELECT * FROM {table_name} WHERE site != %s AND price = %s AND m2 = %s AND rooms = %s"
    cursor = connection.cursor()
    cursor.execute(query, (data_flat['site'], data_flat['price'], data_flat['m2'], data_flat['rooms']))
    result = cursor.fetchall()
    return result

def check_bbdd_mysql(config_db_mysql, logger):
    return create_connection(config_db_mysql['db_host'], config_db_mysql['db_user'], config_db_mysql['db_password'], config_db_mysql['db_name'])
