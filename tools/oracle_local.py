
import pandas as pd
from tools.local import get_embedding
import oracledb

def add_to_database():
    print("Embeding pitanja...")
    p = pd.read_csv('izlaz/kompilirani_csv/baza.csv', index_col=0)
    p['question_embedding'] = p['question'].apply(get_embedding)

    exit(0)  # Zavrsi ranije
    print("Spremanje u bazu podataka...")

    conn = oracledb.connect(
        user="your_username",
        password="your_password",
        host="51.0.0.98",
        port=1521,
        service_name="your_service_name"
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO test (id, question, answer, APLIKACIJA, question_embedding)
        VALUES (:1, :2, :3, :4, :5)
        """,
        (row['id'], row['question'], row['answer'], row['APLIKACIJA'], row['question_embedding'])
    )

    conn.commit()
    cursor.close()
    conn.close()
   