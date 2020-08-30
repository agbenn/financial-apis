from bs4 import BeautifulSoup
import requests


class SECURLScraper:

	def __init__(self):
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
	
	def setHeaders(self, headers):
		self.headers = headers

	def getHeaders(self):
		return self.headers

	# get cik code required for get downloads call by ticker
	def getCIK(self, ticker):
		try:

			requestURL = 'https://sec.report/Ticker/' + ticker
			
			html_doc = requests.get(requestURL, headers=self.headers).text

			print('getting CIK code for ' + ticker)

			soup = BeautifulSoup(html_doc, 'html.parser')
			
			cik = soup.find_all("h2")[0]
			
			cik = cik.text
			
			cik = cik.rsplit(' ', 1)[1]

			print('CIK code retrieved: ' + cik)
			
			return cik
			
		except:
			print('no website found for ' + str(ticker))
			return None


	def getDownloadURLs(self, cik):

		baseURL = 'https://www.sec.gov/Archives/edgar/data/'

		baseRequestURL = baseURL + cik

		print('retrieving urls for cik ' + cik + ' from ' + baseRequestURL)

		html_doc = requests.get(baseRequestURL, headers=self.headers).text

		soup = BeautifulSoup(html_doc, 'html.parser')

		soup = soup.find_all('a')

		allDirURLs = []

		for each in soup:
			if each.parent.name == 'td':
				newURL = baseRequestURL + '/' + each.getText()
				allDirURLs.append(newURL)

		dataFileURLs = []

		for url in allDirURLs:
			html_doc = requests.get(url, headers=self.headers).text

			soup = BeautifulSoup(html_doc, 'html.parser')

			soup = soup.find_all('a')

			for each in soup:
				text = each.getText()
				if 'Financial_Report' in text:
					print('Financial Report Found')
					dataFileURLs.append((url + '/' + text))

		print('retrieved ' + str(len(dataFileURLs)) + ' urls')

		return dataFileURLs

	









