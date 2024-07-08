import psycopg2

DB_NAME = 'acars'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = "127.0.0.1"
DB_PORT = "5432"


class DatabaseSetup:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        self.cursor = self.conn.cursor()

    def drop_all_tables(self):

        self.cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = self.cursor.fetchall()

        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE")

    def create_tables(self):
        queries = [
            '''CREATE TABLE IF NOT EXISTS folders (
                folder_id SERIAL PRIMARY KEY,
                folder_name VARCHAR(255) NOT NULL,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES folders(folder_id),
                CONSTRAINT unique_folder_name UNIQUE (folder_name)
            )''',
            '''CREATE TABLE IF NOT EXISTS messages (
                message_id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                result TEXT NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS templates (
                template_id SERIAL PRIMARY KEY,
                template_name VARCHAR(255) NOT NULL,
                picking_template VARCHAR(255),
                template TEXT,
                model VARCHAR(255),
                message TEXT,
                folder_id INTEGER NOT NULL,
                FOREIGN KEY (folder_id) REFERENCES folders(folder_id)
            )'''
        ]
        for query in queries:
            self.cursor.execute(query)

    def populate_tables(self):
        queries = [
            '''INSERT INTO folders (folder_name, parent_id) VALUES 
                ('Downlink templates', NULL),
                ('Uplink templates', NULL),
                ('A-320 templates', 1),
                ('A-300 template', 1),
                ('A-350 templates', 1)
                ''',
            '''INSERT INTO messages (message, result) VALUES 
                ('Message 1', 'Result A'),
                ('Message 2', 'Result B'),
                ('Message 3', 'Result C'),
                ('Message 4', 'Result D'),
                ('Message 5', 'Result E'),
                ('Message 6', 'Result F')''',
            '''INSERT INTO templates (template_name, picking_template, template, model, message, folder_id) VALUES 
                ('Template 1', 'Picking A', 'Template A', 'Model A', 'message1', 3),
                ('Template 2', 'Picking B', 'Template B', 'Model B', 'message2', 4),
                ('Template 3', NULL, 'Template C', 'Model C',NULL, 5),
                ('Template 4', NULL, 'Template D', 'Model D',NULL, 3),
                ('Template 5', 'Picking C', 'Template E', 'Model E',NULL, 5)'''
        ]
        for query in queries:
            self.cursor.execute(query)

    def setup(self):
        try:
            self.drop_all_tables()
            self.create_tables()
            self.populate_tables()
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
        finally:
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    db_setup = DatabaseSetup()
    db_setup.setup()
