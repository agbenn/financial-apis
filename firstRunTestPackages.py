import pandas as pd
import numpy as np
import SECURLScraper
import URLsToDataFrame


allTickers = ['BE','CRM','ZM']

for ticker in allTickers:
	SECURLScraper = SECURLScraper.SECURLScraper()

	#CIK = SECURLScraper.getCIK(ticker)
	#allFileURLs = SECURLScraper.getDownloadURLs(CIK)
	#pd.DataFrame(allFileURLs).to_csv('fileURLs.csv')
	allFileURLs = list((pd.read_csv('fileURLs.csv')).iloc[:,-1])
	fullDF = URLsToDataFrame.getFinancialFilingsFromURLs(allFileURLs)
	print(fullDF.head(5))

'''
need to first construct the get columns method such that when parsing the first sheet 
global variable 'periodEndDate' will be filled from 'period end date' in sheet itself (fuzzy match)
columns need to be recognized and try catch will need to be entered for non-multiIndex
in exception column value replaced by periodEndDate
clear periodEndDate at end of worksheet parse

'''



















