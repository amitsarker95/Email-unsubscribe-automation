from dotenv import load_dotenv
import imaplib
import email
from bs4 import BeautifulSoup
import requests
import os


load_dotenv()


username = os.getenv('Email')
password = os.getenv('PASSWORD')

def connect_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select('inbox')

    return mail


def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.perser")
    links = [link["href"] for link in soup.findall("a", href=True) if "unsubscribe" in link["href"].lower()]

    return links


def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print("Successfully clicked", link)
        else:
            print("Failed to click", link, response.status_code)
    except Exception as e:
        print("Error", link, str(e), response.status_code)




def search_email():
    mail = connect_email()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()

    links = []

    for num in data:
        _, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    links.extend(extract_links_from_html(html_content))

        else:
            content_type = msg.get_content_type()
            content = msg.get_payload(decode=True).decode()

            if content_type == "text/html":
                links.extend(extract_links_from_html(content))


    mail.logout()
    return links

def save_links(links):
    with open("links.txt", "w") as f:
        f.write('\n'.join(links))

links = search_email()

for link in links:
    click_link(link)

save_links(links)