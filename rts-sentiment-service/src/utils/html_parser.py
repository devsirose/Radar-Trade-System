from bs4 import BeautifulSoup

def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')
    return ' '.join(p.get_text() for p in paragraphs)
