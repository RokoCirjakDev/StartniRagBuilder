from tools.local import get_embedding
from tools.oracle_local import add_to_database
from tools.email_parse import get_email_data
from tools.csv_parse import get_ode_data
import os
import json
import pandas as pd

# emailove s .eml ekstenzijom treba staviti u folder emails
# .env datoteka sa GEMINI_API_KEY mora bit u project rootu. U buducnosti zamjeniti gemini s lokalnim api-jem kada se osposobi server.


LOCAL = True # LOCAL -> varijabla koja određuje hoće li se koristiti lokalni model ili Gemini API
UKLJUCI_CSV = True  # Ako je True, koristi se CSV datoteka za ODE podatke
UKLJUCI_EMAIL =  True # Ako je True, koristi se email folder za parsanje emailova

if not (UKLJUCI_CSV or UKLJUCI_EMAIL):
    print("Nije odabrano parsanje emailova ili CSV datoteke. Odaberite barem jednu opciju.")
    exit(1)


if not LOCAL and (not os.path.exists('.env') or 'GEMINI_API_KEY' not in os.environ):
    print("GEMINI_API_KEY environment variable is not set.")
    exit(1)
else :
    print("Lokalni model.")

folder_path_email = 'emails' 
parovi = []

if UKLJUCI_EMAIL:
    parovi.append(get_email_data(folder_path_email , LOCAL))
    for par in parovi:
        par['APLIKACIJA'] = None
if UKLJUCI_CSV:
    parovi.append(get_ode_data('cvs-ode/ode.txt', LOCAL)) 

p = pd.DataFrame(parovi)
p['question_embedding'] = p['question'].apply(get_embedding)
p.to_csv('kompilirani_csv/parovi.csv', index=False)

print("Parovi su spremljeni u cvs/parovi.csv, poslati u bazu? (y/n): ", end="")
if input().strip().lower() == 'y':
    add_to_database(p)
else:
    print("Parovi nisu poslani u bazu podataka.")