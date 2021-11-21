import requests
from bs4 import BeautifulSoup



def main():
	NewsURL = 'None'
	URL = "https://www.newworld.com/en-us/news"
	page = requests.get(URL)

	soup = BeautifulSoup(page.content, "html.parser")
	results = soup.find(id="")
	#data = results.find_all("div", class_="ags-SlotModule ags-SlotModule--blog ags-SlotModule--threePerRow")
	dataIWant = str(results.find("a", class_="ags-SlotModule-spacer"))
	URL_extension = dataIWant.split('href="')[1].split('"')[0]
	NewsURL = "https://www.newworld.com" + URL_extension
	return NewsURL


if __name__ == "__main__":
	main()