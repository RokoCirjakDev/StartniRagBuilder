import os
os.environ["FLET_SECRET_KEY"] = "your-simple-key-123"
from tools.local import get_embedding
from tools.oracle_local import add_to_database
from tools.email_parse import get_email_data
from tools.csv_parse import get_oder_data
from tools.doc_parse import get_doc_data
from tools.sigurnost import provjeri_sigurnost
import json
import pandas as pd
import flet as ft

from config import config
from frontend.document import create_docs_content

provjeri_sigurnost(config)

parovi = []

if config["UKLJUCI_EMAIL"]:
    print("Parsanje emailova...")  
    parovi.extend(get_email_data('unos/emails', config["LOCAL"], config["PITAJ_APLIKACIJU_EMAIL"]))
    
if config["UKLJUCI_DOC"]:
    print("Parsanje dokumenata...")
    parovi.extend(get_doc_data('unos/dokumentacija', config["LOCAL"], config["PITAJ_APLIKACIJU_DOC"]))

if config["UKLJUCI_CSV"]:
    print("Parsanje ODER podataka iz CSV datoteke...")
    parovi.extend(get_oder_data('unos/cvs-ode/ode.txt', config["LOCAL"])) 

p = pd.DataFrame(parovi)

p.index.name = "id"
p.to_csv('izlaz/kompilirani_csv/baza.csv', index=True)

print("Parovi su spremljeni u izlaz/kompilirani_cvs/parovi.csv, moguca je rucna promjena rezultata. poslati u bazu? (y/n): ", end="")
os.system('start izlaz/kompilirani_csv/baza.csv')
if input().strip().lower() == 'y':
    add_to_database()
else:
    print("Parovi nisu poslani u bazu podataka.")

def main(page: ft.Page):
    page.title = "Email Scrape LLM"
    page.add(create_docs_content(page))

if __name__ == "__main__":
    ft.app(target=main, upload_dir="uploads", secret_key="your-simple-key-123")

