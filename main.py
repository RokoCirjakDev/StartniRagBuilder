from tools.gemini import call_ai
from tools.scraper import scrape_email
import os
import json

# emailove s .eml ekstenzijom treba staviti u folder emails
# .env datoteka sa GEMINI_API_KEY mora bit u project rootu. U buducnosti zamjeniti gemini s lokalnim api-jem kada se osposobi server.

if not os.path.exists('.env') or 'GEMINI_API_KEY' not in os.environ:
    print("GEMINI_API_KEY environment variable is not set.")
    exit(1)

folder_path = 'emails' 

for filename in sorted(os.listdir(folder_path)):
    if filename.endswith('.eml'):
        file_path = os.path.join(folder_path, filename)
        email_content = scrape_email(file_path)
        if email_content:
            response = call_ai(
                f"""Vi ste stručni chatbot za korisničku podršku.
                Na temelju sljedećeg emaila u običnom tekstu, izdvojite potpuno pitanje i odgovor naše podrške.
                Vratite odgovor u JSON formatu s dva polja: "question" (pitanje) i "answer" (odgovor).
                Ako email ne sadrži pitanje, predstavlja zahtjev ili ga chatbot ne može riješiti, vratite JSON objekt s poljem "error" i vrijednošću 0.
                BEZ markdown formatiranja, samo običan tekst.
                AKO email sadrži samo odgovor, dodajte pitanje koje je implicirano punim odgovorom, nemojte preskakati informacije.
                Email:
                {email_content}
                """
            )
            try:
                text = response.candidates[0].content.parts[0].text
                data = json.loads(text)
                if isinstance(data, dict):
                    if "error" in data and data["error"] == 0:
                        print(f"{filename}: Nema pitanja ili odgovora.")
                    elif "question" in data and "answer" in data:
                        # Daljnja logika za slanje para pitanja i odgovora u oracle db ide ovdje.
                        print(f"{folder_path}/{filename}:")
                        print("Question:", data["question"])
                        print("Answer:", data["answer"])
                    else:
                        print(f"{filename}: Kriva JSON struktura.", data)
                else:
                    print(f"{filename}: Response nije JSON.", data)
            except Exception as e:
                print(f"{filename}: Greska sa dict parsingom: {response}")