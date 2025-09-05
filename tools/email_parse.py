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

            Na temelju sadržaja sljedećeg korisničkog e-maila:
            1. Identificirajte jednu jasno izraženu namjeru korisnika koja se može pretvoriti u opće, često postavljano pitanje (FAQ).
            2. Formulirajte to pitanje i univerzalan odgovor koji je primjenjiv na sve korisnike sustava.

            Vratite isključivo JSON objekt sa sljedećim poljima:
            - "pitanje": opće, jasno i univerzalno formulirano korisničko pitanje (bez osobnih podataka, imena korisnika, tvrtki, dokumenata ili konteksta specifičnih slučajeva)
            - "odgovor": kratak, standardiziran odgovor temeljen na funkcionalnostima i pravilima softvera, bez spominjanja specifičnih korisnika, organizacija ili procesa koji nisu univerzalni

            Stroge upute:
            - Ako e-mail sadrži osobne podatke, konkretne poslovne slučajeve, interne nazive procesa ili zahtjeve koji nisu primjenjivi svim korisnicima — odmah vrati: {{"error": 0}}
            - Ako e-mail ne sadrži dovoljno informacija za kreiranje smislenog i općenitog FAQ pitanja — vrati: {{"error": 0}}
            - Ne izmišljaj module, datoteke, korisničke uloge ili procese koji nisu eksplicitno navedeni i univerzalni.
            - Ako je e-mail zapravo odgovor ili zahtjev bez pitanja, možeš formulirati implicirano pitanje, ali samo ako je korisnička namjera jasno prepoznatljiva i općenita.
            - Ne koristi nikakvo dodatno formatiranje, markdown, stilizaciju ni komentare. Vrati isključivo čisti JSON.

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
                    elif "pitanje" in data and "odgovor" in data:
                        print("pitanje:", data["pitanje"])
                        print("odgovor:", data["odgovor"])

                        if PITAJ_APLIKACIJU_EMAIL:
                            APLIKACIJA = input(f"Na koju aplikaciju se odnosi ovaj par?")
                        else:
                            APLIKACIJA = None

                        parovi.append({
                            "pitanje": data["pitanje"],
                            "odgovor": data["odgovor"],
                            "aplikacija": APLIKACIJA,
                            "kontekst": email_content

                        })

                    else:
                        print(f"{filename}: Kriva JSON struktura.", data)
                else:
                    print(f"{filename}: Response nije JSON.", data)
            except Exception as e:
                print(f"{filename}: Greska sa dict parsingom - {e}")
    return parovi

def get_email_data_with_app(folder_path: str, LOCAL: bool, aplikacija: str):
    parovi = []
    
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.msg'):
            file_path = os.path.join(folder_path, filename)
            email_content = scrape_email(file_path)
            if email_content:
                prompt = f"""
                Vi ste specijalizirani chatbot za korisničku podršku financijskog softvera.

                Na temelju sadržaja sljedećeg korisničkog e-maila:
                1. Identificirajte jednu jasno izraženu namjeru korisnika koja se može pretvoriti u opće, često postavljano pitanje (FAQ).
                2. Formulirajte to pitanje i univerzalan odgovor koji je primjenjiv na sve korisnike sustava.

                Vratite isključivo JSON objekt sa sljedećim poljima:
                - "pitanje": opće, jasno i univerzalno formulirano korisničko pitanje (bez osobnih podataka, imena korisnika, tvrtki, dokumenata ili konteksta specifičnih slučajeva)
                - "odgovor": kratak, standardiziran odgovor temeljen na funkcionalnostima i pravilima softvera, bez spominjanja specifičnih korisnika, organizacija ili procesa koji nisu univerzalni

                Stroge upute:
                - Ako e-mail sadrži osobne podatke, konkretne poslovne slučajeve, interne nazive procesa ili zahtjeve koji nisu primjenjivi svim korisnicima — odmah vrati: {{"error": 0}}
                - Ako e-mail ne sadrži dovoljno informacija za kreiranje smislenog i općenitog FAQ pitanja — vrati: {{"error": 0}}
                - Ne izmišljaj module, datoteke, korisničke uloge ili procese koji nisu eksplicitno navedeni i univerzalni.
                - Ako je e-mail zapravo odgovor ili zahtjev bez pitanja, možeš formulirati implicirano pitanje, ali samo ako je korisnička namjera jasno prepoznatljiva i općenita.
                - Ne koristi nikakvo dodatno formatiranje, markdown, stilizaciju ni komentare. Vrati isključivo čisti JSON.

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
                        elif "pitanje" in data and "odgovor" in data:
                            print("pitanje:", data["pitanje"])
                            print("odgovor:", data["odgovor"])

                            parovi.append({
                                "pitanje": data["pitanje"],
                                "odgovor": data["odgovor"],
                                "aplikacija": aplikacija,
                                "kontekst": email_content
                            })

                        else:
                            print(f"{filename}: Kriva JSON struktura.", data)
                    else:
                        print(f"{filename}: Response nije JSON.", data)
                except Exception as e:
                    print(f"{filename}: Greska sa dict parsingom - {e}")
    return parovi