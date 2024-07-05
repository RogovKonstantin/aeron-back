import psycopg2

DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host="127.0.0.1", port="5432")

cursor = conn.cursor()

create_table_query1 = '''CREATE TABLE IF NOT EXISTS folders (
                            folder_id SERIAL PRIMARY KEY,
                            folder_name VARCHAR(255) NOT NULL,
                            parent_id INTEGER,
                            FOREIGN KEY (parent_id) REFERENCES folders(folder_id)
                        )'''
cursor.execute(create_table_query1)

create_table_query2 = '''CREATE TABLE IF NOT EXISTS message (
                            message_id SERIAL PRIMARY KEY,
                            message VARCHAR(255) NOT NULL,
                            result VARCHAR(255)
                        )'''
cursor.execute(create_table_query2)

create_table_query3 = '''CREATE TABLE IF NOT EXISTS templates (
                            template_id SERIAL PRIMARY KEY,
                            template_name VARCHAR(255) NOT NULL,
                            picking_template VARCHAR(255),
                            template VARCHAR(255),
                            model VARCHAR(255),
                            message VARCHAR(255),
                            folder_id INTEGER,
                            FOREIGN KEY (folder_id) REFERENCES folders(folder_id)
                        )'''
cursor.execute(create_table_query3)

populate_table_query1 = '''INSERT INTO folders (folder_name, parent_id)
                            VALUES ('Folder A', NULL),
                                   ('Folder B', NULL),
                                   ('Subfolder 1', 1),
                                   ('Subfolder 2', 1)'''
cursor.execute(populate_table_query1)

populate_table_query2 = '''INSERT INTO message (message, result)
                            VALUES ('Message 1', 'Result A'),
                                   ('Message 2', 'Result B')'''
cursor.execute(populate_table_query2)

populate_table_query3 = '''INSERT INTO templates (template_name, picking_template, template, model, message, folder_id)
                            VALUES ('Template 1', 'Picking A', 'Template A', 'Model A', 'Message 1', 1),
                                   ('Template 2', 'Picking B', 'Template B', 'Model B', 'Message 2', 2)'''
cursor.execute(populate_table_query3)

conn.commit()

conn.close()
