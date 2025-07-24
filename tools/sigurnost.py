import os


def provjeri_sigurnost(config):
    if not (config.get('UKLJUCI_CSV') or config.get('UKLJUCI_EMAIL') or config.get('UKLJUCI_DOC')):
        print("Nije odabrano parsanje emailova ili CSV datoteke. Odaberite barem jednu opciju.")
        exit(1)

    if not config.get('LOCAL'):
        print("Koristi se VANJSKI Gemini API. Nastaviti? (y/n): ", end="")
        if input().strip().lower() != 'y':
            print("Prekid programa.")
            exit(1)
    else:
        print("Lokalni model.")

    if not config.get('LOCAL') and (not os.path.exists('.env') or 'GEMINI_API_KEY' not in os.environ):
        print("GEMINI_API_KEY fali u .env datoteci ili .env datoteka ne postoji.")
        exit(1)
