from bs4 import BeautifulSoup
import requests
import ipaddress

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

BASE_URL = "https://ipapi.co"

def get_location(ip):
    if ipaddress.ip_address(ip).is_private:
        return "   Localhost"
    r = requests.get(f"{BASE_URL}/ip", headers=HEADERS, timeout=5)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find_all("td", {"class":"ipval"})
    location = content[1].text + " , " + content[3].text.replace("\n","")
    return location