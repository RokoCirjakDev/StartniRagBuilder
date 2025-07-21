import mailparser
from bs4 import BeautifulSoup 

def scrape_email(file_path):
    mail = mailparser.parse_from_file(file_path)
    if mail.text_plain:
        lines = [line for line in mail.text_plain if line.strip()]
        return '\n'.join(lines)
    elif mail.text_html:
        soup = BeautifulSoup('\n'.join(mail.text_html), 'html.parser')
        text = soup.get_text(separator='\n')
        lines = [line for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
    return ''

