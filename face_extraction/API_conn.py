from flask import jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

def create_connection():
    conn = psycopg2.connect(host='localhost', port='5432', dbname='ekyc_video', user='kith', password='test123')
    return conn

def create_api_key_table():
    conn = create_connection()
    cursor = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS api_key (
        id SERIAL PRIMARY KEY,
        application TEXT NOT NULL,
        client TEXT NOT NULL,
        key TEXT NOT NULL
    );
    '''
    cursor.execute(create_table_query)
    print("table created succefully")
    conn.commit()
    cursor.close()
    conn.close()

def insert_api_key(application, client, key):
    conn = create_connection()
    cursor = conn.cursor()
    insert_query = '''
    INSERT INTO api_key (application, client, key)
    VALUES (%s, %s, %s);
    '''
    cursor.execute(insert_query, (application, client, key))
    conn.commit()
    cursor.close()
    conn.close()

# Function to get the API key from the database
def get_apikey(client, app):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM api_key WHERE application = %s AND client = %s;", (app, client))
    row = cursor.fetchone()
    api_key = row[0] if row else None
    cursor.close()
    conn.close()
    return api_key
