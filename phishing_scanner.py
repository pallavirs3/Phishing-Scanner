import re
import requests
from bs4 import BeautifulSoup

def is_suspicious_url(url):
    # Check for IP address in the URL
    ip_pattern = re.compile(r'^(http[s]?://)?(\d{1,3}\.){3}\d{1,3}(:\d+)?(/|$)')
    if ip_pattern.search(url):
        return True

    # Check for long URLs
    if len(url) > 75:
        return True

    # Check for suspicious keywords in the URL
    suspicious_keywords = ["login", "verify", "update", "security", "ebayisapi", "banking", "secure"]
    if any(keyword.lower() in url.lower() for keyword in suspicious_keywords):
        return True

    return False

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def is_suspicious_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check forms specifically for sensitive input fields or action URLs
    forms = soup.find_all('form')
    for form in forms:
        form_text = form.text.lower()
        form_action = form.get('action', '').lower()
        # Check if the form action URL or form text contains suspicious elements
        if any(keyword in form_text for keyword in ["password", "ssn", "credit card", "bank account"]) or \
           any(keyword in form_action for keyword in ["login", "secure", "verify"]):
            return True
    
    # General page content keyword check
    suspicious_keywords = ["login", "verify", "update", "secure", "confirm", "account"]
    keyword_count = sum(content.lower().count(keyword) for keyword in suspicious_keywords)
    
    # Consider content suspicious if too many occurrences of suspicious keywords
    if keyword_count > 10:  # Threshold set to 10 occurrences, can be adjusted
        return True

    return False

def scan_url(url):
    print(f"Scanning URL: {url}")

    # Check URL characteristics
    if is_suspicious_url(url):
        print("Warning: URL is suspicious based on its characteristics.")
        return True

    # Fetch and analyze page content
    content = fetch_page_content(url)
    if content and is_suspicious_content(content):
        print("Warning: Page content is suspicious.")
        return True

    print("URL seems to be safe.")
    return False

# Prompt the user to input a URL
user_url = input("Please enter a URL to scan: ").strip()
scan_url(user_url)