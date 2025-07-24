from tools.local import get_embedding
from tools.oracle_local import add_to_database
from tools.email_parse import get_email_data
from tools.csv_parse import get_oder_data
from tools.doc_parse import get_doc_data
from tools.sigurnost import provjeri_sigurnost
import os
import json
import pandas as pd

from config import config

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
if input().strip().lower() == 'y':
    add_to_database()
else:
    print("Parovi nisu poslani u bazu podataka.")