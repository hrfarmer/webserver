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
        print("image links created")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS db_user (
                                twitch_username text,
                                email text,
                                access_token text,
                                refresh_token text,
                                user_type text
                            );""")

    def new_user(self, username, email, a_token, r_token, u_type):
        self.cursor.execute(
            f"INSERT INTO db_user (twitch_username, email, access_token, refresh_token, user_type) VALUES('{username}', '{email}', '{a_token}', '{r_token}', '{u_type}')")
        self.conn.commit()

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

