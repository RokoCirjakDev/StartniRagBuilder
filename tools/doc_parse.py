import os
import docx
from docx import Document
from tools.gemini import call_ai
from tools.local import parse_local
import json
import fitz

def call_ai_docx(heading: str, text: str, LOCAL: bool):
    prompt = f"""
    Vi ste specijalizirani chatbot za korisničku podršku financijskog softvera.

    Na temelju sljedeće sekcije dokumentacije:
    1. Identificirajte jednu funkcionalnost koja je opisana jasno i univerzalno.
    2. Na temelju te funkcionalnosti, formulirajte jedno opće, često postavljano korisničko pitanje (FAQ) i pripadajući univerzalni odgovor koji vrijedi za sve korisnike.

    Vratite isključivo JSON objekt s točno dva polja:
    - "pitanje": jasno, kratko i opće korisničko pitanje koje bi korisnici mogli postaviti kako bi razumjeli tu funkcionalnost (npr. "Kako mogu izvesti izvještaj o plaćanjima?")
    - "odgovor": standardizirani odgovor koji informira korisnika o toj funkcionalnosti, bez korištenja konkretnih primjera, korisničkih imena, organizacija, dokumenata ili procesa koji nisu eksplicitno navedeni

    Stroge upute:
    - Ako sadržaj nije dovoljan za kreiranje općeg FAQ pitanja i odgovora — odmah vrati: {{"error": 0}}
    - Ne izmišljaj funkcionalnosti, imena datoteka, korisničke uloge ili interne procese koji nisu eksplicitno spomenuti.
    - Ako tekst samo objašnjava funkcionalnost bez pitanja, formuliraj prikladno i univerzalno korisničko pitanje koje bi to moglo objasniti, ali samo ako je dovoljno jasno.
    - Ne koristi nikakvo dodatno formatiranje, markdown, bullet points, niti komentare. Vrati isključivo čisti JSON.

    Ulazni sadržaj dokumentacije:
    Heading: {heading}
    Text: {text}
    """

    response = call_ai(prompt, LOCAL)
    try:
        if LOCAL:
            text = parse_local(response)
        else:
            text = response.candidates[0].content.parts[0].text

        data = json.loads(text)

        if "error" in data and data["error"] == 0:
            print("Nema pitanja ili odgovora.")
            return {"pitanje": None, "odgovor": None}

        print("Parsed data:", data)

        return {"pitanje": data["pitanje"], "odgovor": data["odgovor"]}
    
    except Exception as e:
        print(f"Greska sa dict parsingom - {e}")
        exit(1)







def get_sections(docx_path):
    doc = Document(docx_path)
    sections = []
    current_heading = None
    current_text = []

    for para in doc.paragraphs:
        style = para.style.name

        if style == "Heading 2":
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_text)))
                current_text = []

            current_heading = para.text.strip()

        elif current_heading is not None:
            current_text.append(para.text)

    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_text)))

    return sections


def get_doc_data(directory: str, LOCAL: bool, PITAJ_APLIKACIJU_DOC: bool):
    parovi = []

    for file in os.listdir(directory):
        if file.endswith(".docx"):
            sections = get_sections(os.path.join(directory, file))

            if PITAJ_APLIKACIJU_DOC:
                print(f"Na koju APLIKACIJU se odnosi ovaj dokument? {file}:", end="")
                APLIKACIJA = input().strip()
                if not APLIKACIJA:
                    print("Niste unijeli APLIKACIJU. Preskakanje dokumenta...")
                    continue
            else:
                APLIKACIJA = None
            
            for heading, text in sections:
                if text.strip():
                    data = call_ai_docx(heading, text, LOCAL)
                    if data["pitanje"] and data["odgovor"]:
                        parovi.append({
                            'pitanje': data["pitanje"],
                            'odgovor': data["odgovor"],
                            'aplikacija': APLIKACIJA,
                            'kontekst': heading + " " + text
                        })
                    else:
                        print(f"Preskakanje sekcije '{heading}' u dokumentu {file} jer nije pronađeno pitanje ili odgovor.")
                        continue

        elif file.endswith(".pdf"):
            doc = fitz.open(file)
            text = "\n".join([page.get_text() for page in doc])
            
        else:
            print(f"Unsupported file type: {file}")
            continue
    
    return parovi

def get_doc_data_with_app_id(directory: str, LOCAL: bool, app_id: str):
    parovi = []

    for file in os.listdir(directory):
        if file.endswith(".docx"):
            sections = get_sections(os.path.join(directory, file))

            for heading, text in sections:
                if text.strip():
                    data = call_ai_docx(heading, text, LOCAL)
                    if data["pitanje"] and data["odgovor"]:
                        parovi.append({
                            'pitanje': data["pitanje"],
                            'odgovor': data["odgovor"],
                            'aplikacija': app_id,
                            'kontekst': heading + " " + text
                        })
                    else:
                        print(f"Preskakanje sekcije '{heading}' u dokumentu {file} jer nije pronađeno pitanje ili odgovor.")
                        continue

        elif file.endswith(".pdf"):
            doc = fitz.open(file)
            text = "\n".join([page.get_text() for page in doc])
            # PDF handling can be added here if needed

        else:
            print(f"Unsupported file type: {file}")
            continue
    
    return parovi
