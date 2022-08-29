# import psycopg
# from vars import DB_URI, DB_NAME, DB_USER


# class DBManager:
#     def __init__(self):
#         self.connection = psycopg.connect(DB_URI)
#         self.cursor = self.connection.cursor()
#
#     def restart(self):
#         if self.connection.closed:
#             self.connection = psycopg.connect(DB_URI)
#             self.cursor = self.connection.cursor()
#
#     def get_user(self, user_id) -> str:
#         existing_user = self.cursor.execute(f"SELECT id from users where id = {user_id}").fetchone()
#
#         return existing_user
#
#     def add_user(self, user_id, username):
#         existing_user = self.get_user(user_id)
#
#         if not existing_user:
#             self.cursor.execute("INSERT INTO users(id, username) VALUES (%s, %s)", (user_id, username))
#             self.connection.commit()
#
#     def update_gender(self, user_id, gender_value):
#         self.cursor.execute(f"UPDATE users SET gender = {gender_value} WHERE id = {user_id}")
#         self.connection.commit()
#
#     def stop(self):
#         self.connection.close()
