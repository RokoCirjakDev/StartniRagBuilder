from tools.gemini import call_ai
from tools.scraper import scrape_email
from tools.local import parse_local
import os
import json



def get_email_data(folder_path: str, LOCAL: bool):
    parovi = []
    
    for filename in sorted(os.listdir(folder_path)):
     if filename.endswith('.eml'):
        file_path = os.path.join(folder_path, filename)
        email_content = scrape_email(file_path)
        if email_content:
            prompt = f"""
            Vi ste stručni chatbot za korisničku podršku.

            Na temelju sljedećeg emaila u običnom tekstu:
            - Izdvojite jedno općenito često postavljano pitanje (FAQ) i pripadajući odgovor naše podrške.
            - Vratite rezultat u JSON formatu s dva polja:
            "question" (pitanje) i "answer" (odgovor).

            Ako email ne sadrži jasno pitanje, predstavlja zahtjev ili ga chatbot ne može riješiti, vratite JSON objekt:
            {{"error": 0}}

            Vratite isključivo običan tekst u JSON formatu, bez ikakvog markdown ili drugog formatiranja.

            Ako email sadrži samo odgovor, formulirajte implicitno FAQ pitanje koje odgovara tom odgovoru, pritom nemojte izostavljati važne informacije.

            Email:
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
                        parovi.append({'question': data["question"], 'answer': data["answer"]})

                    else:
                        print(f"{filename}: Kriva JSON struktura.", data)
                else:
                    print(f"{filename}: Response nije JSON.", data)
            except Exception as e:
                print(f"{filename}: Greska sa dict parsingom - {e}")
    return parovi