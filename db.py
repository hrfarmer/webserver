import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS image_links (
                                file_path text,
                                shortlink text
                            ); """)
        print("done")
    
    def add_link(self, path, shortlink):
        self.cursor.execute(f"INSERT INTO image_links (file_path, shortlink) VALUES('{file_path}', '{shortlink}')")
        self.conn.commit()
        
d = Database()

