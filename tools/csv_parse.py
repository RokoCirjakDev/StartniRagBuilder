import pandas as pd
from tools.local import parse_local
from tools.gemini import call_ai
import json
import os

def call_ai_ode(opis: str, primjedba: str, LOCAL: bool):
   prompt = f"""
    Vi ste stručni chatbot za korisničku podršku.

    Na temelju donesenog opisa i primjedbe:
    1. Izdvojite općenito često postavljano pitanje (FAQ) i pripadajući odgovor naše podrške.
    2. Vratite rezultat isključivo u JSON formatu s dva polja:
    - "question": tekst pitanja
    - "answer": tekst odgovora

    Upute:
    - Ako opis ne sadrži jasno pitanje ili primjedba ne sadrži valjani odgovor, vratite JSON objekt: {{"error": 0}}
    - Nemojte koristiti nikakvo markdown ili drugo formatiranje, vratite samo čist JSON tekst.
    - Ako opis sadrži samo odgovor, formulirajte implicitno pitanje koje odgovara tom odgovoru, pod uvjetom da je odgovor smislen i općenit.
    - Ne preskačite važne informacije u odgovoru.

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




def get_ode_data(filepath:str, LOCAL:bool):
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
            'APLIKACIJA': row['APLIKACIJA'],
            'question': question,
            'answer': answer
        })

    return result



