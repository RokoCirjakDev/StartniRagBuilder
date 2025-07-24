from tools.gemini import call_ai
from tools.local import parse_local
import os
import json
import extract_msg
from bs4 import BeautifulSoup

def scrape_email(file_path):
    msg = extract_msg.Message(file_path)
    body = msg.body
    html_body = msg.htmlBody

    if body:
        lines = [line for line in body.splitlines() if line.strip()]
        return '\n'.join(lines)
    elif html_body:
        soup = BeautifulSoup(html_body, 'html.parser')
        text = soup.get_text(separator='\n')
        lines = [line for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
    return ''


def get_email_data(folder_path: str, LOCAL: bool, PITAJ_APLIKACIJU_EMAIL: bool):
    parovi = []
    
    for filename in sorted(os.listdir(folder_path)):
     if filename.endswith('.msg'):
        file_path = os.path.join(folder_path, filename)
        email_content = scrape_email(file_path)
        if email_content:
            prompt = f"""
            Vi ste specijalizirani chatbot za korisničku podršku financijskog softvera.

            Na temelju sadržaja sljedećeg emaila (u običnom tekstu):
            - Izdvojite isključivo jedno opće, često postavljano pitanje (FAQ) i univerzalan odgovor koji je primjenjiv na sve korisnike.
            - Vratite isključivo JSON objekt s dva polja:
            - "question": jasno, opće i univerzalno formulirano pitanje, bez osobnih podataka, korisničkih imena, konkretnih tvrtki ili dokumenata
            - "answer": standardizirani odgovor koji se temelji na pravilima i funkcijama softvera, bez izmišljanja sadržaja ili referenci na specifične korisnike ili slučajeve

            Stroge upute:
            - Ako email sadrži osobne podatke, konkretne slučajeve, interne izraze ili zahtjeve koji nisu općeniti, odmah vratite JSON objekt: {{"error": 0}}
            - Ako sadržaj nije prikladan za formiranje općeg FAQ pitanja koje bi se moglo prikazivati svim korisnicima, vratite: {{"error": 0}}
            - Ne izmišljajte interne dokumente, podatke ili procese koji nisu jasno navedeni u tekstu i univerzalno točni.
            - Ako je sadržaj emaila samo odgovor, možete formulirati implicirano FAQ pitanje, ali samo ako je odgovor smislen i važi za sve korisnike.
            - Ne koristite nikakvo dodatno formatiranje (npr. markdown, bullet points, stilizaciju). Vratite isključivo čisti JSON tekst.

            Email sadržaj:
            {email_content}
            """
            response = call_ai(prompt, LOCAL)
            try:
                
                if LOCAL:
                    text = parse_local(response)
                else:
                    text = response.candidates[0].content.parts[0].text

                data = json.loads(text)
                print(f"{folder_path}/{filename}: ")
                if isinstance(data, dict):
                    if "error" in data and data["error"] == 0:
                        print(f"{filename}: Nema pitanja ili odgovora.")
                    elif "question" in data and "answer" in data:
                        print("Question:", data["question"])
                        print("Answer:", data["answer"])

                        if PITAJ_APLIKACIJU_EMAIL:
                            APLIKACIJA = input(f"Na koju aplikaciju se odnosi ovaj par?")
                        else:
                            APLIKACIJA = None

                        parovi.append({
                            'question': data["question"],
                            'answer': data["answer"],
                            'APLIKACIJA': APLIKACIJA
                        })

                    else:
                        print(f"{filename}: Kriva JSON struktura.", data)
                else:
                    print(f"{filename}: Response nije JSON.", data)
            except Exception as e:
                print(f"{filename}: Greska sa dict parsingom - {e}")
    return parovi