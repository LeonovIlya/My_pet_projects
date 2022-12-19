# запросы к таблице files
shop_list = "SELECT DISTINCT chain_name FROM files"
magnit_list = "SELECT DISTINCT shop_name FROM files"
name_query = "SELECT DISTINCT name FROM files"
file_query = "SELECT file_link FROM files"

# запросы к таблице users
check_query = "SELECT * FROM users"
access_query = "SELECT access_level FROM users"
get_query = "SELECT name FROM users"
set_tg_id = "UPDATE users SET tg_id = ? WHERE password = ?"
insert_user = "INSERT INTO users (name, password, access_level, supervisor_name) VALUES (?, ?, 1, ?)"
logout = "UPDATE users SET tg_id = NULL WHERE tg_id = ?"
delete_user = "DELETE FROM users WHERE name = ?"
edit_user_name = "UPDATE users SET name = ? WHERE name = ?"
edit_user_password = "UPDATE users SET password = ? WHERE name = ?"

