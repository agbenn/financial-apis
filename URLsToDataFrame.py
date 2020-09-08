from optimizer import optimize
import pandas as pd
import numpy as np
import dateutil.parser
import os
import urllib.request



# quickie func to format .xls dfs
def formatDF(df, document):
	if document == 0:
		df = df.bfill(axis=1)
	if df.iloc[0, 0].isna():
		df.iloc[0, 0] = (df.columns)[0]
		df.columns = df.iloc[0, :]
	if df.iloc[0, 1].isna():
		df = df.iloc[1:]
	else:
		df = df.iloc[2:]
	return df

# returns list of worksheets if given a url for a xls or xlsx filing download url
def getWorksheetsListFromExcelURL(downloadURL, isXLSX):
	print('downloading file : ' + downloadURL)

	# handles well formatted .xlsx files with dat reader bitch
	if isXLSX:
		urllib.request.urlretrieve(downloadURL, "temp.xlsx")

		xlsxFile = pd.ExcelFile("temp.xlsx")

		worksheets = []

		print('file downloaded, tranforming into sheets')

		for xlsxSheet in xlsxFile.sheet_names:
			worksheets.append(pd.read_excel(xlsxFile, xlsxSheet))

		print('file transformed, cleaning up')
		os.remove("temp.xlsx")

	# handles .xls schema which is stored string like - parses that bitch
	else:
		urllib.request.urlretrieve(downloadURL, "temp.xls")

		file1 = open('temp.xls', 'r')
		lines = file1.readlines()

		worksheets = []
		worksheet = []
		isWorksheet = False
		isFirstWorkSheet = True
		count = 0

		print('file downloaded, tranforming into sheets')

		for line in lines:
			if '<html' in line:
				isWorksheet = True
			if '</html' in line:
				isWorksheet = False

			if isWorksheet:
				worksheet.append(line)
			else:
				if len(worksheet) > 0:
					worksheet.append(line)
					if not isFirstWorkSheet:
						temp = '\n'.join(worksheet)
						temp = temp.replace('3D1', '1')
						temp = temp.replace('3D2', '2')
						temp = temp.replace('3D3', '3')
						temp = temp.replace('3D4', '4')
						temp = temp.replace('3D5', '5')
						temp = temp.replace('3D6', '6')
						temp = temp.replace('3D7', '7')
						temp = temp.replace('3D8', '8')
						temp = temp.replace('3D9', '9')
						temp = temp.replace('3D10', '10')
						temp = pd.read_html(temp)
						temp = formatDF(temp, count)
						count += 1
						worksheets.append(temp)
						worksheet = []
					else:
						worksheet = []
						isFirstWorkSheet = False
				else:
					worksheet = []

		print('file transformed, cleaning up')

		os.remove("temp.xls")

	return worksheets

# retrieve current column when multi-indexed column exists

def getCurrentMultiIndexColumn(worksheetColumns):

	currentMaxMonth = 0
	currentMaxDate = dateutil.parser.parse('1/1/1901')

	# financial form column
	firstIndex = worksheetColumns[0]
	# date column index
	secondIndex = None
	# some multi-index columns are 'unnamed' so take most recent x-months
	lastNewMonth = None

	for colIndex in range(1, len(worksheetColumns)):
		# if column is 'unnamed' catch the exception and set the index to last correct unnamed version
		try:
			newMonth = int(worksheetColumns[colIndex][0][0])
			lastNewMonth = worksheetColumns[colIndex][0]
		except:
			newMonth = int(lastNewMonth[0])
			worksheetColumns.values[colIndex] = (lastNewMonth, worksheetColumns.values[colIndex][1])
			print('column was unnamed, previous value was : ' +
					worksheetColumns.values[colIndex])

		# find max 'x months trailing' date
		if newMonth > currentMaxMonth:
			currentMaxMonth = newMonth
			secondIndex = worksheetColumns[colIndex]

		# if column is malformed with a bunch of extraneous characters then substring date from column head
		if len(worksheetColumns.values[colIndex][1]) > 13:
			worksheetColumns.values[colIndex] = (
				worksheetColumns[colIndex][0], worksheetColumns[colIndex][1][:13])

		# find max date column for the sheet
		newDate = dateutil.parser.parse(worksheetColumns.values[colIndex][1])
		if newDate > currentMaxDate:
			currentMaxDate = newDate
			secondIndex = worksheetColumns[colIndex]
	return firstIndex, secondIndex, worksheetColumns

# retrieve current column date for the worksheet
def getCurrentColumn(worksheetColumns, periodEndDate):
	currentMaxDate = dateutil.parser.parse('1/1/1901')
	index = None
	isEntitySheet = False
	newDate = None

	if 'Entity Information' in worksheetColumns[0]:
		isEntitySheet = True

	for colIndex in range(1, len(worksheetColumns)):
		if len(worksheetColumns.values[colIndex]) > 13:
			worksheetColumns.values[colIndex] = worksheetColumns.values[colIndex][:13]
		try:	
			newDate = dateutil.parser.parse(worksheetColumns.values[colIndex])
		except:
			newDate = periodEndDate
		if newDate > currentMaxDate:
			currentMaxDate = newDate
			index = worksheetColumns.values[colIndex]
	return index, worksheetColumns

# accepts the excel filing as a list of data frames
# parses out the current column
# appends all reports to one series
# returns the DF if it is the base DF
# returns a dictionary and the new column name if not base DF
def getCurrentDataFromFilings(worksheets, isXLSX=True):
	allWorksheets = []
	periodEndDate = None

	print('beginning worksheets to single column transformation')
	for worksheetIndex in range(0, len(worksheets)):
		worksheet = None
		if isXLSX:
			worksheet = worksheets[worksheetIndex]
		else:
			worksheet = worksheets[worksheetIndex][0]

		# set period end date global
		if worksheetIndex == 0:
			periodEndDate = dateutil.parser.parse(worksheet.loc[worksheet[(worksheet.columns)[0]].isin(['Period End Date', 'Document Period End Date', 'End Date'])].values[0][1])

		worksheet = worksheet.dropna(thresh=int(len(worksheet)*.5), axis=1)

		if worksheet.shape[1] > 1:
			if isinstance(worksheet.columns, pd.MultiIndex):
				col1, col2, fullCols = getCurrentMultiIndexColumn(
					worksheet.columns)
				worksheet.columns = fullCols
				columns = [col1[1], col2[1]]
				tempDF = pd.concat([worksheet[col1], worksheet[col2]], axis=1)
				tempDF.columns = columns
			else:
				col1 = list(worksheet.columns)[0]
				col2, fullCols = getCurrentColumn(worksheet.columns, periodEndDate)
				worksheet.columns = fullCols
				tempDF = pd.concat([worksheet[col1], worksheet[col2]], axis=1)
				tempDF.columns = [col1, col2]

			multiplier = 0
			if 'In Thousands' in tempDF.columns[0]:
				multiplier = 1000
			if 'In Millions' in tempDF.columns[0]:
				multiplier = 1000000
			if 'In Billions' in tempDF.columns[0]:
				multiplier = 1000000000
			tempDF = tempDF.fillna(0)
			if multiplier > 0:
				tempDF[tempDF.columns[1]].loc[tempDF[tempDF.columns[1]].astype(str).str.isnumeric(
				)] = tempDF[tempDF.columns[1]].loc[tempDF[tempDF.columns[1]].astype(str).str.isnumeric()].astype(float) * multiplier

			tempDF = optimize(tempDF.transpose()).transpose()

		print('completed report transformation: ' + col1)
		allWorksheets.append(tempDF.values)

	x = pd.DataFrame(np.concatenate(allWorksheets))
	col2 = x.loc[x[0] == 'Document Type'].values[0] + ' on ' + \
		x.loc[x[0] == 'Document Period End Date'].values[0]
	x.columns = ['Metric', col2[1]]

	print('completed worksheets to single column transform for filing: ' + col2[1])
	colStr = str(col2[1]).upper()

	if 'Q' in colStr and '10' in colStr:
		return x, col2[1], '10Q'
	elif 'K' in colStr and '10' in colStr:
		return x, col2[1], '10K'
	else:
		return None, None, None

def getFinancialFilingsFromURLs(urls):
	print('initiating extraction to dataframe for all filings for the company')

	# set variable so first iteration builds dataframe, consecutive iterations will build dictionaries
	AnnualDataFrame = None
	QuarterlyDataFrame = None

	for url in urls:
		print('getting worksheets from url : ' + url)
		
		isXLSX = False
		if '.xlsx' in url:
			isXLSX = True

		worksheets = getWorksheetsListFromExcelURL(url, isXLSX)
		print('retrieved ' + str(len(worksheets)) + ' worksheets')
		
		print('initialize multi worksheet transform from: ' + url)

		# need a separate df for quarterly vs annual reports
		# 10-q + 10-q/a vs 10-k

		df, col, reportType = getCurrentDataFromFilings(worksheets, isXLSX)
		if reportType == '10K':
			if AnnualDataFrame is not None:
				print('transforming 10K report into dictionary')
				newColDictionary =  dict(zip(df['Metric'], df[col]))
				print('retrieved dictionary of size, ' + str(len(newColDictionary)) + ' appending new data to data frame of size: ' + str(AnnualDataFrame.shape))
				AnnualDataFrame[col] = AnnualDataFrame['Metric'].map(newColDictionary)
				print('data successfully appended to data frame, new DF size: ' + str(AnnualDataFrame.shape))
			else:
				AnnualDataFrame = df
				print('retrieved base 10K data frame of size: ' + str(AnnualDataFrame.shape))

		elif reportType == '10Q':
			if QuarterlyDataFrame is not None:
				print('transforming 10Q report into dictionary')
				newColDictionary =  dict(zip(df['Metric'], df[col]))
				print('retrieved dictionary of size, ' + str(len(newColDictionary)) + ' appending new data to data frame of size: ' + str(QuarterlyDataFrame.shape))
				QuarterlyDataFrame[col] = QuarterlyDataFrame['Metric'].map(newColDictionary)
				print('data successfully appended to data frame, new DF size: ' + str(QuarterlyDataFrame.shape))
			else:
				QuarterlyDataFrame = df
				print('retrieved base 10Q data frame of size: ' + str(QuarterlyDataFrame.shape))

	print('all urls extracted, annual report size: ' + str(AnnualDataFrame.shape))
	print('all urls extracted, quarterly report size: ' + str(QuarterlyDataFrame.shape))

	#TODO make more robust for selection of only quarterly or only annual
	# would need a 'peek' method to look at report type on first field
	# use thread pooler to spin thread off for each worksheet - initial dataframe for each needs to be created
	return [AnnualDataFrame, QuarterlyDataFrame]





