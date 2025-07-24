import pandas as pd
from tools.local import parse_local
from tools.gemini import call_ai
import json
import os

def call_ai_ode(opis: str, primjedba: str, LOCAL: bool):
    prompt = f"""
    Vi ste specijalizirani chatbot za korisničku podršku financijskog softvera.

    Na temelju donesenog opisa i primjedbe:
    1. Izdvojite isključivo opće, ponavljajuće korisničko pitanje (FAQ) i odgovarajući odgovor koji vrijedi za sve korisnike sustava.
    2. Vratite rezultat isključivo u JSON formatu s točno dva polja:
    - "question": općenito, jasno i univerzalno formulirano pitanje bez osobnih imena, specifičnih korisnika ili dokumenata
    - "answer": standardizirani odgovor bez referenci na korisnike, osobne primjere, interne dokumente ili nestandardne procese

    Stroge upute:
    - Ako opis i/ili primjedba sadrže osobne podatke, imena korisnika, konkretne interne slučajeve ili nestandardne probleme — odmah vratite: {{"error": 0}}
    - Ako opis ili primjedba ne sadrže dovoljno informacija za formiranje općeg FAQ-a, također vratite: {{"error": 0}}
    - Ne izmišljajte dokumente, procese, imena, ni bilo kakve informacije koje nisu univerzalno točne.
    - Ako je primjedba samo odgovor, pokušajte formirati implicirano, opće pitanje, ali samo ako je jasno i primjenjivo na sve korisnike.
    - Ne koristite nikakav markdown, formatiranje ili dodatni tekst. Vratite isključivo čisti JSON.

    Ulazni podaci:
    Opis: {opis}
    Primjedba: {primjedba}
    """
    
    response = call_ai(prompt, LOCAL)
    try:
        if LOCAL:
            text = parse_local(response)
        else:
            if not response.candidates or not response.candidates[0].content.parts:
                print("No candidates or content parts found in the response.")
                exit(1)
            else:
                text = response.candidates[0].content.parts[0].text

        data = json.loads(text)

        if "error" in data and data["error"] == 0:
                print("Nema pitanja ili odgovora.")
                return None, None
        
        print("Parsed data:", data)
        return data["question"], data["answer"]
    except Exception as e:
        print(f"Greska sa dict parsingom - {e}")
        exit(1)




def get_oder_data(filepath:str, LOCAL:bool):
    print(f"Učitavanje ODE podataka iz {filepath}...")
    if not os.path.exists(filepath):
        print(f"Datoteka {filepath} ne postoji.")
        exit(1)
    
    ode_data = pd.read_csv(filepath, delimiter='|', encoding='utf-8', on_bad_lines='skip')

    result = []
    for _, row in ode_data.iterrows():
        question, answer = call_ai_ode(row['OPIS'], row['PRIMJEDBA'], LOCAL)
        if question is None or answer is None:
            print(f"Beskoristan redak. Preskakanje...")
            continue
        result.append({
            'question': question,
            'answer': answer,
            'APLIKACIJA': row['APLIKACIJA']
        })

    return result



