import psycopg2

DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host="127.0.0.1", port="5432")

cursor = conn.cursor()

# Create tables
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

# Populate tables
populate_table_query1 = '''INSERT INTO folders (folder_name, parent_id)
                            VALUES 
                            ('Folder A', NULL),
                            ('Folder B', NULL),
                            ('Subfolder 1', 1),
                            ('Subfolder 2', 1),
                            ('Subfolder 3', 2),
                            ('Subfolder 4', 2),
                            ('Nested Subfolder 1', 3),
                            ('Nested Subfolder 2', 4)'''
cursor.execute(populate_table_query1)

populate_table_query2 = '''INSERT INTO message (message, result)
                            VALUES 
                            ('Message 1', 'Result A'),
                            ('Message 2', 'Result B'),
                            ('Message 3', 'Result C'),
                            ('Message 4', 'Result D'),
                            ('Message 5', 'Result E'),
                            ('Message 6', 'Result F')'''
cursor.execute(populate_table_query2)

populate_table_query3 = '''INSERT INTO templates (template_name, picking_template, template, model, message, folder_id)
                            VALUES 
                            ('Template 1', 'Picking A', 'Template A', 'Model A', 'Message 1', 1),
                            ('Template 2', 'Picking B', 'Template B', 'Model B', 'Message 2', 2),
                            ('Template 3', NULL, 'Template C', 'Model C', 'Message 3', 3),
                            ('Template 4', NULL, 'Template D', 'Model D', 'Message 4', 4),
                            ('Template 5', 'Picking C', 'Template E', 'Model E', 'Message 5', 5),
                            ('Template 6', 'Picking D', 'Template F', 'Model F', 'Message 6', 6),
                            ('Template 7', NULL, 'Template G', 'Model G', 'Message 1', 7),
                            ('Template 8', NULL, 'Template H', 'Model H', 'Message 2', 8)'''
cursor.execute(populate_table_query3)

conn.commit()

cursor.close()
conn.close()