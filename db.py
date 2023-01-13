import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        
    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS image_links (
                                file_path text,
                                shortlink text
                            ); """)
        print("done")
    
    def add_link(self, path, shortlink):
        self.cursor.execute(f"INSERT INTO image_links (file_path, shortlink) VALUES('{path}', '{shortlink}')")
        self.conn.commit()
    
    def return_path(self, shortlink):
        self.cursor.execute(f"SELECT * FROM image_links WHERE shortlink = '{shortlink}'")
        return self.cursor.fetchone()
    
    def check_link_exists(self, shortlink):
        self.cursor.execute(
            f"SELECT * FROM image_links WHERE shortlink = '{shortlink}'")
        if type(self.cursor.fetchone()[1]) == None:
            return False
        else:
            return True

    
