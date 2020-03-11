
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

url = "http://www.cmfchile.cl/institucional/mercados/"
ua = UserAgent(fallback="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0")

url_fondos = "consulta.php?mercado=V&Estado=VI&entidad=FINRE&_=1583866428197"
url_temp_value = "entidad.php?mercado=V&rut={}&tipoentidad=FINRE&row=AAAw%20cAAhAABP4PAAP&vig=VI&control=svs&pestania=7"
post_temp_value = "dia1={:02d}&mes1={:02d}&anio1={}&dia2={:02d}&mes2={:02d}&anio2={}&sub_consulta_fi=Consultar&enviado=1"

def get_soup(path, m="get", data=None):
	method = requests.get if m == "get" else requests.post
	try:
		header = {"User-Agent": ua.random, "Content-Type": "application/x-www-form-urlencoded"}
		rs = method(url+path, data=data, headers=header, timeout=30)
		rs.raise_for_status()
	except Exception as e:
		print(f"Request failed ({e})")
		return None
	return BeautifulSoup(rs.content, 'html.parser')

def get_fondos():
	soup = get_soup(url_fondos)
	if not soup:
		return None, None
	ruts = []
	names = []
	for e in soup.find_all("tr"):
		td = e.contents[1]
		if td.name == "td":
			ruts.append(td.contents[1].get_text())
		td = e.contents[3]
		if td.name == "td":
			names.append(td.contents[1].get_text())
	return ruts, names

def get_value(rut, day1, month1, year1, day2, month2, year2):
	data = post_temp_value.format(day1, month1, year1, day2, month2, year2)
	soup = get_soup(url_temp_value.format(rut), "post", data)
	if not soup:
		return None
	info = []
	for e in soup.find_all("tr"):
		info.append([x.get_text() for x in e.contents if x.__class__.__name__ != "NavigableString"])
	return info

def get_value_url(rut):
	return url + url_temp_value.format(rut)

if __name__ == "__main__":
	from datetime import datetime

	ruts, names = get_fondos()

	if not ruts:
		raise Exception("Error, could not get company ruts")

	now = datetime.now()
	d = now.day
	m = now.month
	y = now.year

	data = get_value(ruts[0].split("-")[0], d-2, m, y, d-1, m, y)
	if not data:
		raise Exception("Error, could not get company data")

	print(data)

