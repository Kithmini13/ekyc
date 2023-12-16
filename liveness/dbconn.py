import psycopg2
import os
from datetime import datetime

class dbquery:
    def __init__(self):
        self.conn = psycopg2.connect(dbname="ekyc_video", user="gagani", password="gagani", host="localhost", port="5432")
        print('Database connected successfully!')


    def insert_data(self, user_id, path, date_time):
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO video_info(user_id, path, date_time) VALUES (%s, %s, %s)", (user_id, path, date_time))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting data in dbconn.py: {str(e)}")
        finally:
            cur.close()


    def retrieve_data(self, pid):
        rows_string = ''
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT path FROM video_info WHERE user_id = %s;", (str(pid),))
            rows = cur.fetchone()
            if rows is not None:
                rows_string = ', '.join(str(value) for value in rows)
        except psycopg2.Error as e:
            # Handle specific database errors using psycopg2.Error
            print(f"PostgreSQL Error: {e}")
        except Exception as e:
            # Handle other general exceptions
            print(f"An error occurred in dbconn.py: {str(e)}")
        finally:
            if cur:
                cur.close()
        return rows_string


    def insert_folder_data(self, file_path, user_id):
        for filename in os.listdir(file_path):
            if filename.endswith('.mp4'):
                full_path = os.path.join(file_path, filename)
                video_id = int(os.path.splitext(filename)[0])
                date_time = datetime.now()
                webcam_ekycvideo = self(user_id=user_id, path=full_path, date_time=date_time)
                webcam_ekycvideo.save()


