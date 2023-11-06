import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

# Read in list of URLs from CSV file
urls_df = pd.read_csv("!!!PATH TO URL CSV!!!")
urls = urls_df["URL"].tolist()

unscraped = deque(urls)

scraped = set()

emails = set()
email_count = 0  # Counter for number of emails found

while len(unscraped) and email_count < 250:  # Stop program when x emails have been found
    url = unscraped.popleft()
    scraped.add(url)

    parts = urlsplit(url)

    base_url = "{0.scheme}://{0.netloc}".format(parts)
    if '/' in parts.path:
        path = url[:url.rfind('/') + 1]
    else:
        path = url

    print("Crawling URL %s" % url, email_count)
    try:
        response = requests.get(url, timeout=25)  # Set timeout to x seconds
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        continue

    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
    emails.update(new_emails)
    email_count += len(new_emails)  # Increment email count by number of new emails found

    soup = BeautifulSoup(response.text, 'lxml')

    for anchor in soup.find_all("a"):
        if "href" in anchor.attrs:
            link = anchor.attrs["href"]
        else:
            link = ''

        if link.startswith('/'):
            link = base_url + link

        elif not link.startswith('http'):
            link = path + link

        if not link.endswith(".gz") and not link.endswith(".jpg") and not link.endswith(
                ".jpeg") and not link.endswith(".png") and not link.endswith(".gif") and not link.endswith(".pdf"):
            if not link in unscraped and not link in scraped:
                unscraped.append(link)

df = pd.DataFrame(emails, columns=["Email"])
df.to_csv('FoundEmails.csv', index=False)
