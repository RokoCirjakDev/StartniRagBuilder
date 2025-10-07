import pandas as pd
import oracledb
import array
from tools.local import get_embedding_safe
import ast
import json
import unidecode
import os

user = "skripta"
password = "Infoprojekt1"
dsn = "51.0.0.98/FREEPDB1"


def normaliziraj_hrv(text):
    return unidecode.unidecode(text)

def add_to_database():
    print("Embedding pitanja...")

    p = pd.read_csv('izlaz/kompilirani_csv/baza.csv', index_col=0)
    p['embedding'] = p['pitanje'].apply(normaliziraj_hrv).apply(get_embedding_safe)
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    cursor = connection.cursor()


    for _, row in p.iterrows():
        
        embedding = row['embedding']
        stayembedding = embedding
        print("Embeding passed")
        if not isinstance(embedding, list) or len(embedding) != 768 or not all(isinstance(x, (float)) for x in embedding):
            raise ValueError("Embedding must be a list of 1024 elements.")

        embedding = array.array('d', [float(x) for x in embedding])

        assert isinstance(embedding, array.array), f"embedding is not array.array, got {type(embedding)}"
        assert embedding.typecode == 'd', f"embedding typecode must be 'd', got {embedding.typecode}"
        assert len(embedding) == 768, f"embedding must be length 1024, got {len(embedding)}"
        
       
        try:
            cursor.execute(f"""
            INSERT INTO skripta.RagTest1 (pitanje, odgovor, kontekst, aplikacija, embedding)
            VALUES (:pitanje, :odgovor, :kontekst, :aplikacija, :embedding)
        """, {
            "pitanje": row['pitanje'],
            "odgovor": row['odgovor'],
            "kontekst": row['kontekst'],
            "aplikacija": row['aplikacija'],
            "embedding": embedding
        })
        except oracledb.Error as error:
            print(f"Error inserting into database: {error}")
            print(row)
            with open("embeddings.txt", "w") as f:
                f.write(json.dumps(stayembedding, indent=2))

            os.system("start notepad embeddings.txt")
            stop = input("Press Enter to continue...")
            os.system("del embeddings.txt")
            continue

    connection.commit()
    cursor.close()
    connection.close()
    print(f"Successfully uploaded {len(p)} records to database!")

def send_to_database(df):
    """
    Send a DataFrame to the database with embeddings
    Args:
        df: DataFrame with columns ['pitanje', 'odgovor', 'kontekst']
    """
    print("Embedding pitanja...")
    
    # Create a copy to avoid modifying the original DataFrame
    p = df.copy()
    
    # Add default aplikacija column if not present
    if 'aplikacija' not in p.columns:
        p['aplikacija'] = 0
    
    # Generate embeddings for each question
    p['embedding'] = p['pitanje'].apply(normaliziraj_hrv).apply(get_embedding_safe)
    
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    cursor = connection.cursor()

    for _, row in p.iterrows():
        embedding = row['embedding']
        stayembedding = embedding
        print("Embeding passed")
        
        if not isinstance(embedding, list) or len(embedding) != 768 or not all(isinstance(x, (float)) for x in embedding):
            raise ValueError("Embedding must be a list of 1024 elements.")

        embedding = array.array('d', [float(x) for x in embedding])
        print("Embedding length:", len(embedding))
            
        try:
            cursor.execute(f"""
            INSERT INTO skripta.RagTest1 (pitanje, odgovor, kontekst, aplikacija, embedding)
            VALUES (:pitanje, :odgovor, :kontekst, :aplikacija, :embedding)
        """, {
            "pitanje": row['pitanje'],
            "odgovor": row['odgovor'],
            "kontekst": row['kontekst'],
            "aplikacija": row['aplikacija'],
            "embedding": embedding
        })
        except oracledb.Error as error:
            print(f"Error inserting into database: {error}")
            print(row)
            with open("embeddings.txt", "w") as f:
                f.write(json.dumps(stayembedding, indent=2))

            stop = input("Press Enter to continue...")
            os.system("del embeddings.txt")
            continue
        print("Inserted row:", row['pitanje'])

    connection.commit()
    cursor.close()
    connection.close()
    print(f"Successfully uploaded {len(p)} records to database!")
