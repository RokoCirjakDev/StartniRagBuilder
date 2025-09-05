import pandas as pd
from tools.local import parse_local
from tools.gemini import call_ai
import json
import os

import math

def is_valid_row(row):
    return (
        pd.notna(row['APLIKACIJA']) and 
        pd.notna(row['OPIS']) and isinstance(row['OPIS'], str) and 
        pd.notna(row['PRIMJEDBA']) and isinstance(row['PRIMJEDBA'], str)
    )


def call_ai_ode(opis: str, primjedba: str, LOCAL: bool):
    prompt = f"""
    Vi ste specijalizirani chatbot za korisničku podršku financijskog softvera.

    Vaš zadatak je sljedeći:
    1. Analizirajte opis i primjedbu korisnika.
    2. Ako je moguće, identificirajte ponavljajuće, univerzalno korisničko pitanje koje odražava *namjeru* korisnika, bez specifičnih detalja.
    3. Formulirajte to pitanje i standardizirani odgovor tako da ih mogu razumjeti svi korisnici, neovisno o njihovoj ulozi ili situaciji.

    Vratite rezultat isključivo u JSON formatu s točno dva polja:
    - "pitanje": jasno, sažeto i opće korisničko pitanje koje bi moglo biti često postavljeno (npr. "Kako mogu promijeniti lozinku?")
    - "odgovor": kratak, jasan i univerzalno primjenjiv odgovor (npr. "Lozinku možete promijeniti u postavkama računa pod sekcijom 'Sigurnost'.")

    Pravila:
    - Ako opis/primjedba sadrži osobne podatke, imena korisnika, konkretne dokumente nemojte ih uključivati u odgovor.
    - Ako primjedba ne sadrži dovoljno informacija za formuliranje općeg FAQ pitanja — odmah vratite: {{"error": 0}}
    - Ne izmišljajte module, datoteke, korisničke uloge ili procese koji nisu eksplicitno navedeni.
    - Ako je primjedba zapravo odgovor ili zahtjev bez pitanja, formulirajte implicirano pitanje, ali samo ako je korisnička namjera jasno prepoznatljiva i općenita.
    - Ne koristite nikakvo dodatno formatiranje, markdown, bullet points, niti komentare. Vratite isključivo čisti JSON.
    - Ako podaci nisu dovoljni za formuliranje univerzalnog FAQ-a — vratite: {{"error": 0}}
    - Ne uključujte detalje koji vrijede samo za pojedine korisnike, organizacije ili interne sustave.
    - Ne izmišljajte funkcionalnosti ili procese koji nisu eksplicitno navedeni ili univerzalno primjenjivi.
    - Ako je primjedba zapravo odgovor, pokušajte razumjeti *što je korisnik želio saznati*.

    Ulazni podaci:
    Opis: {opis}
    Primjedba: {primjedba}
    """

    
    response = call_ai(prompt, LOCAL)
    try:
        if LOCAL:
            text = parse_local(response)
            if not text or text.strip() == "":
                print("Empty response from local API")
                return None, None
        else:
            if not response.candidates or not response.candidates[0].content.parts:
                print("No candidates or content parts found in the response.")
                return None, None
            else:
                text = response.candidates[0].content.parts[0].text
                if not text or text.strip() == "":
                    print("Empty text from API response")
                    return None, None

        if not text or text.strip() == "":
            print("Empty response text")
            return None, None
            
        data = json.loads(text)

        if "error" in data and data["error"] == 0:
                print("Nema pitanja ili odgovora.")
                return None, None
        
        print("Parsed data:", data)
        return data["pitanje"], data["odgovor"]
    except Exception as e:
        print(f"Greska sa dict parsingom - {e}")
        return None, None




def get_oder_data(filepath:str, LOCAL:bool):
    print(f"Učitavanje ODE podataka iz {filepath}...")
    if not os.path.exists(filepath):
        print(f"Datoteka {filepath} ne postoji.")
        exit(1)
    
    ode_data = pd.read_csv(filepath, delimiter='á', encoding='utf-8', 
                 engine='python', on_bad_lines='skip', dtype={'OPIS': str, 'PRIMJEDBA': str})


    result = []
    for _, row in ode_data.iterrows():
        if not is_valid_row(row):
            print(f"Neispravan redak: {row}. Preskakanje...")
            continue 
        pitanje, odgovor = call_ai_ode(row['OPIS'], row['PRIMJEDBA'], LOCAL)
        if pitanje is None or odgovor is None:
            print(f"Beskoristan redak. Preskakanje...")
            continue
        result.append({
            "pitanje": pitanje,
            "odgovor": odgovor,
            "aplikacija": row['APLIKACIJA'],
            "kontekst" : str(row['PRIMJEDBA']) + " " + str(row['OPIS'])
        })

    return result



