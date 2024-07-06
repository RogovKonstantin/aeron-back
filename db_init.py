import psycopg2

DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host="127.0.0.1", port="5432")

cursor = conn.cursor()


truncate_table_query1 = '''TRUNCATE TABLE templates, message, folders RESTART IDENTITY CASCADE'''
cursor.execute(truncate_table_query1)


create_table_query1 = '''CREATE TABLE IF NOT EXISTS folders (
    folder_id SERIAL PRIMARY KEY,
    folder_name VARCHAR(255) NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES folders(folder_id),
    CONSTRAINT unique_folder_name UNIQUE (folder_name)
)'''
cursor.execute(create_table_query1)

create_table_query2 = '''CREATE TABLE IF NOT EXISTS message (
                            message_id SERIAL PRIMARY KEY,
                            message VARCHAR(255) NOT NULL,
                            result VARCHAR(255) NOT NULL
                        )'''
cursor.execute(create_table_query2)

create_table_query3 = '''CREATE TABLE IF NOT EXISTS templates (
                            template_id SERIAL PRIMARY KEY,
                            template_name VARCHAR(255) NOT NULL,
                            picking_template VARCHAR(255),
                            template VARCHAR(255) NOT NULL,
                            model VARCHAR(255),
                            message VARCHAR(255),
                            folder_id INTEGER NOT NULL,
                            FOREIGN KEY (folder_id) REFERENCES folders(folder_id)
                        )'''
cursor.execute(create_table_query3)


populate_table_query1 = '''INSERT INTO folders (folder_name, parent_id)
                            VALUES 
                            ('Downlink templates', NULL),
                            ('Uplink templates', NULL),
                            ('A-320 templates', 1),
                            ('A-300 template', 1),
                            ('A-350 templates', 1),
                            ('A-320 template 1', 2),
                            ('A-320 template 2', 2),
                            ('A-300 template 1', 3)
                            '''
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
                            ('Template 1', 'Picking A', 'Template A', 'Model A', 'Message 1', 3),
                            ('Template 2', 'Picking B', 'Template B', 'Model B', 'Message 2', 4),
                            ('Template 3', NULL, 'Template C', 'Model C', 'Message 3', 5),
                            ('Template 4', NULL, 'Template D', 'Model D', 'Message 4', 6),
                            ('Template 5', 'Picking C', 'Template E', 'Model E', 'Message 5', 7)
                        '''
cursor.execute(populate_table_query3)

conn.commit()

cursor.close()
conn.close()
