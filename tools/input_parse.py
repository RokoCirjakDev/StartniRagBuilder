
from tools.local import call_local, parse_local
import json

def PoboljsajUnos(pitanje: str, odgovor: str, Kontekst: str = "", kritika: str = "") -> str:
    prompt = (
        f"Poboljšaj sljedeće pitanje i odgovor na hrvatskom jeziku ISKLJUČIVO u smislu profesionalnosti i profesionalnog tona i opcoj namjnenjivosti za rag sustav. "
        f"ali NIKAKO ne mijenjaj značenje pitanja ili odgovora. Svako pitanje mora imati '?' i svaki odgovor mora imati '.' na kraju. "
        f"Pitanje i odgovor moraju biti više opći i razumljivi, ne smiju uključivati imena, poštapalice ili bilo što nepotrebno značenju pitanja. "
        f"Vrati rezultat isključivo kao validan JSON s poljima 'pitanje' i 'odgovor' LOWERCASE!!!. "
        f"Ne dodavaj nikakav dodatni tekst, komentare ili objašnjenja. "
        f"Uzmite u obzir sljedeću kritiku i poboljšajte unos: {kritika}\n"
        f"Kontekst na kojoj bazi je pitanje i odgovor: {Kontekst}\n"
        f"pitanje: {pitanje}\n"
        f"odgovor: {odgovor}\n"
        f"JSON rezultat:"
    )

    response = call_local(prompt)
    result_json = parse_local(response)
    print(f"AI Poboljšanje: {result_json}")
    try:
        result = json.loads(result_json)
        print(result)
        return result
    except json.JSONDecodeError:
        print("Rezultat nije validan JSON i ne može se spremiti.")
        print(f"Originalni odgovor: {result_json}")
        return {"pitanje": None, "odgovor": None}

def TestirajUnos(pitanje: str, odgovor: str, Kontekst: str = "") -> str:
    prompt = (
        f"Testiraj sljedeće pitanje i odgovor na hrvatskom jeziku ISKLJUČIVO u smislu profesionalnosti i profesionalnog tona i opcoj namjnenjivosti za rag sustav. "
        f"Pitanje i odgovor moraju biti više opći i razumljivi, ne smiju uključivati imena, poštapalice ili bilo što nepotrebno značenju pitanja. "
        f"Vrati rezultat isključivo kao validan JSON s poljimem 'kritika' kao preporuka kako poboljsati unos"
        f"NI SLUCAJNO NEMOJ DODAVATI IKAKAV MARKDOWN FORMATING, VRATI SAMO CISTI JSON"
        f"pitanje: {pitanje}\n"
        f"odgovor: {odgovor}\n"
        f"Kontekst na kojoj bazi je pitanje i odgovor, njega nemoj kritizirati jer sluzi samo kao izvor: {Kontekst}\n"
        f"JSON rezultat:"
    )

    response = call_local(prompt)
    result_json = parse_local(response)
    print(f"AI Testiranje: {result_json}")
    try:
        result = json.loads(result_json)
        print(result)
        if "kritika" not in result:
            result["kritika"] = "Prazna kritika."
        else:
            return result["kritika"]
    except json.JSONDecodeError:
        print("Rezultat nije validan JSON i ne može se spremiti.")
        print(f"Originalni odgovor: {result_json}")
        return {"kritika": "Prazna kritika."}


