import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Accessing environment variables
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


def write_emails(emails: list):
    with psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, port=db_port
    ) as conn:
        with conn.cursor() as cur:
            query_create_table = """
            DROP TABLE IF EXISTS emails;
            CREATE TABLE emails (
                id SERIAL PRIMARY KEY,
                email_subject TEXT NOT NULL,
                email_from VARCHAR(255) NOT NULL,
                email_domain VARCHAR(100),
                company_name VARCHAR(255),
                received_at TIMESTAMP NOT NULL
            );
            """
            cur.execute(query_create_table)
            query_insert_emails = """
            INSERT INTO emails (email_subject, email_from, email_domain, company_name, received_at)
            VALUES %s """
            extras.execute_values(cur, query_insert_emails, emails)
            cur.execute("SELECT * FROM emails")
            cur.fetchone()
            for record in cur:
                print(record)
            conn.commit()
