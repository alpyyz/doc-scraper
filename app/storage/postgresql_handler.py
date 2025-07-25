import psycopg2

def get_pg_connection():
    return psycopg2.connect(
        dbname="academic_papers",
        user="alp",
        password="Alp1123123*",
        host="localhost",  # or your host/IP
        port="5432"         # default PostgreSQL port
    )

def insert_paper_pg(conn, title, scholar_link, scihub_link, is_downloaded, local_path, raw_text):
    with conn.cursor() as cursor:
        cursor.execute("""
            --sql
            INSERT INTO all_papers (title, scholar_link, scihub_link, is_downloaded, local_path, raw)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (title, scholar_link, scihub_link, is_downloaded, local_path, raw_text))
    conn.commit()
