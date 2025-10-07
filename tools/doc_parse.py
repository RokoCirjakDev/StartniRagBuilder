import os
import docx
from docx import Document
from tools.gemini import call_ai
from tools.local import parse_local
import json
import fitz

def call_ai_docx(heading: str, text: str, LOCAL: bool):
    prompt = f"""
    Vi ste specijalizirani ai agent za citanje dokumentacije firme i prilagodaj tih dokumentacija u informacija u formatu za rag sustav.

    Na temelju sljedeće sekcije dokumentacije:
    1. Identificirajte više činjenica o financijskom software firme i generirajte ih u obliku pitanja i odgovora.
    2. Na temelju svake te cinjenice, formulirajte opće, često postavljano korisničko pitanje (FAQ) i pripadajući univerzalni odgovor koji vrijedi za sve korisnike.

    Vratite isključivo JSON objekt listu s više parova po točno dva polja:
    - "pitanje": jasno, kratko i opće korisničko pitanje koje bi korisnici mogli postaviti kako bi razumjeli tu funkcionalnost (npr. "Kako mogu izvesti izvještaj o plaćanjima?")
    - "odgovor": standardizirani odgovor koji informira korisnika o toj funkcionalnosti ili nekoj potrebi korisnika

    Važne upute:
    - Ne izmišljaj funkcionalnosti, imena datoteka, korisničke uloge ili interne procese koji nisu eksplicitno spomenuti.
    - Ako tekst samo objašnjava funkcionalnost bez pitanja, formuliraj prikladno i univerzalno korisničko pitanje koje bi to moglo objasniti, ali samo ako je dovoljno jasno.
    - Ne koristi nikakvo dodatno formatiranje, markdown, bullet points, niti komentare. Vrati isključivo čisti JSON.

    Ne ukljuciti: Imena, primjere, poštapalice, interne procese, imena datoteka, korisničke uloge ili bilo što što nije univerzalno.

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

        print("Parsed data:", data)

        return data
    
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




def get_doc_data_with_app_id(directory: str, LOCAL: bool, app_id: str):
    parovi = []

    for file in os.listdir(directory):
        if file.endswith(".docx"):
            sections = get_sections(os.path.join(directory, file))

            for heading, text in sections:
                if text.strip():
                    data = call_ai_docx(heading, text, LOCAL)
                    for pair in data:
                        if 'pitanje' in pair and 'odgovor' in pair:
                            parovi.append({
                                'pitanje': pair['pitanje'],
                                'odgovor': pair['odgovor'],
                                'aplikacija': app_id,
                                'kontekst': heading + " " + text
                            })
                        else:
                            print(f"Preskakanje para u sekciji '{heading}' u dokumentu {file} jer nije pronađeno pitanje ili odgovor.")

                    else:
                        print(f"Preskakanje sekcije '{heading}' u dokumentu {file} jer nije pronađeno pitanje ili odgovor.")
                        continue

        else:
            print(f"Unsupported file type: {file}")
            continue
    
    return parovi
