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
    - Izdvojite isključivo jedno opće, često postavljano pitanje (FAQ) i univerzalno primjenjiv odgovor koji odgovara funkcionalnostima opisanima u tekstu.
    - Vratite isključivo JSON objekt s točno dva polja:
    - "question": jasno, općenito i korisnicima razumljivo pitanje koje bi mogli postaviti o toj funkcionalnosti
    - "answer": standardizirani, informativan odgovor bez referenci na korisnike, konkretne firme, primjere iz stvarne prakse, osobna imena ili dokumente koji nisu eksplicitno navedeni

    Stroge upute:
    - Ako tekst ne sadrži dovoljno informacija za jasno i univerzalno pitanje/odgovor, odmah vratite: {{"error": 0}}
    - Ne izmišljajte funkcionalnosti, module, interne procese, datoteke, imena ili korisničke uloge koje nisu eksplicitno spomenute u tekstu.
    - Ako tekst sadrži samo informaciju (bez pitanja), formulirajte prikladno i opće FAQ pitanje koje odgovara toj informaciji, ali samo ako je jasno i primjenjivo na sve korisnike.
    - Ne koristite nikakvo dodatno formatiranje, markdown, bullet points ni stilizaciju. Vratite isključivo čisti JSON bez ikakvih dodataka.

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
            return {"question": None, "answer": None}

        print("Parsed data:", data)

        return {"question": data["question"], "answer": data["answer"]}
    
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
                    if data["question"] and data["answer"]:
                        parovi.append({
                            'question': data["question"],
                            'answer': data["answer"],
                            'APLIKACIJA': APLIKACIJA
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
    