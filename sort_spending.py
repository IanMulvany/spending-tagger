#from openpyxl import load_workbook, Workbook
from typing import NamedTuple  
from typing import List 
from typing import Tuple
import calendar
import parsedatetime 
import datetime
from collections import defaultdict 
from collections import namedtuple 
from pylab import *

#wbn = Workbook
#wb = load_workbook(filename='HouseholdWealth.xlsx', read_only =True)

#DONE find todays date and use this to shiwncurrent spending 
#DONE wrap all of this in a finction and use this to generate resuts from previous months 
#TODO show top 10 expenses from previous month not including mortgage 
#TODO fill out days of spending and sum per day in preparation for graphing my monthly soend. 
#DONE graph spending  
#TODO add a gui to allow mw to tag my spending. 
#DONE move this script to a local folder to the iphone sonthatbincan shownot on the today screen. 

start_day :int = 16
start_salary :float = 4900

def is_data_row(row) -> bool:
	emptyvals = ["","\n"]
	for datapoint in row:
		if datapoint not in emptyvals:
			return True
	return False
	
def separate_year(date):
	date_parts = date.split("-")#remove(str(year))
	for part in date_parts: 
		if len(part) == 4: 
			year = part
			date_parts.remove(part)
	return year, date_parts
			
def infer_start_end_month(datarows: List[str]) -> Tuple[str,str]:
	dates = [i[0] for i in datarows]
	for row in datarows:
		date = row[0]
		year, date_parts = separate_year(date)
		for part in date_parts: 
			if part == "28": # we know the other part of the date is the lower bound month! 
				date_parts.remove("28")
				month_one = int(date_parts[0])
				if month_one == 12: 
					month_two = '01'
				else:
					month_two = str(month_one +1)
				return(month_one, month_two)

def get_data_rows_from_file(datafile: str) -> List[str]:
	data = open(datafile,'r').readlines()
	datarows = []
	for row in data:
		rowpoints = row.split('\t')
		if is_data_row(rowpoints): datarows.append(rowpoints)
	return datarows

def normalise_date(date: str, month_one: str, month_two: str) -> str:
	year, date_parts = separate_year(date)
	#print(date_parts[-1], month_one)
	if date_parts[-1] == str(month_one):
		if date_parts[0] >= str(start_day):
			date_parts.reverse()
	if date_parts[-1] == month_two:
		date_parts.reverse()
	normalised_date = year + '-' + date_parts[0] + '-' + date_parts[1]
	return normalised_date 

def replace_slash_with_hyphen(row: List[str]) -> List[str]:
	date = row[0]
	date_unslashed = date.replace("/","-")
	row[0] = date_unslashed
	return row

def normalise_data_rows(datarows: List[str]) -> List[str]:	
	"""
	normailse date format and then sort on date 
	"""
	unslashed_data_rows = [replace_slash_with_hyphen(i) for i in datarows[1:]]
	
	month_one, month_two = infer_start_end_month(unslashed_data_rows)
	
	normalised_data_rows = []
	for row in unslashed_data_rows:
		date = row[0]
		normalised_date = normalise_date(date, month_one, month_two)
		row[0] = normalised_date
		normalised_data_rows.append(row)
	normalised_data_rows.sort()
	return normalised_data_rows

def generate_cumulative_data(spend_by_day: List[tuple]) -> List[str]:
	"""
	calculate a running total of spend. over the date range. 
	"""
	cumulative_spend = 0
	cumulative_rows = []
	for row in spend_by_day:
		cumulative_spend = round(cumulative_spend + float(row[1]),2)
		remaining_salary = round(start_salary - cumulative_spend, 2)
		cumulative_rows.append([row[0], cumulative_spend, remaining_salary])
	return cumulative_rows	
	
def spend_summed_by_day(normalised_data_rows: List[str]) -> List[Tuple]:
	"""
	for each day sum the spend. 
	return a sorted list 
	
	with sone code hints on use of zip from 
	https://bugra.github.io/work/notes/2015-01-03/i-wish-i-knew-these-things-when-i-first-learned-python/ 
	
	this function actually returns a list of tuples , but i dont know how to represent that in type hinting. 
	"""
	day_spends_dict = defaultdict(float)
	day_spends = []
	for row in normalised_data_rows:
		date = row[0]
		spend = float(row[2])
		day_spends_dict[date] += spend 
	day_spends = sorted (zip(day_spends_dict.keys(), day_spends_dict.values()))
	return day_spends
	
def spend_summed_by_category(normalised_data_rows: List[str]) -> List[Tuple]:
	"""
	for each category sum the spend. 
	return a sorted list 
	
	with sone code hints on use of zip from 
	https://bugra.github.io/work/notes/2015-01-03/i-wish-i-knew-these-things-when-i-first-learned-python/ 
	
	this function actually returns a list of tuples , but i dont know how to represent that in type hinting. 
	"""
	day_spends_dict = defaultdict(float)
	day_spends = []
	for row in normalised_data_rows:
		date = row[0]
		spend = float(row[2])
		category = row[3]
		print(category)
		day_spends_dict[category] += spend 
	day_spends = sorted (zip(day_spends_dict.keys(), day_spends_dict.values()))
	print(day_spends)
	return day_spends

def today_as_string() -> str:
	today = datetime.date.today().strftime("%Y-%m-%d")
	return today

def generate_today_report(cumulative_data: List[str]) -> bool:
	"""
	show spending within a teonday window of today. 
	"""
	today = today_as_string()
	todays_date = today.split('-')[-1]
	for index, row in enumerate(cumulative_data):
		row_date = row[0].split('-')[-1]
		if abs(int(todays_date) - int(row_date)) < 2:
			print(index, row)
	return True

def generate_top_random_spends(normalised_data_rows):
	"""
	top spends on month not including mortgage or other standing spends. 
	"""
	standard_spends = ['OVO', 'CBS', 'RTB', 'AVIVA']
	
	for row in normalised_data_rows:
		print_flag = False
		if float(row[2]) > 100:
			print_flag = True
			for standard in standard_spends:
				if standard in row[1]:
					print_flag = False
		if print_flag: print(row[0:4])		
	
def plot_spending(data: List[tuple]) -> bool:
	plotting_points = [x[1] for x in data]
	t = range(len(plotting_points))
	s = plotting_points
	plot(t, s)	
	xlabel('days')
	ylabel('spend')
	title('monthly rate of spending')
	grid(True)
	show()
	return True 

def generate_month_report(datafile: str) -> None:
	datarows = get_data_rows_from_file(datafile)
	normalised_data_rows = normalise_data_rows(datarows)
	spend_by_day = spend_summed_by_day(normalised_data_rows)
	spend_by_category = spend_summed_by_category(normalised_data_rows)
	cumulative_data = generate_cumulative_data(spend_by_day)
	plot_spending(cumulative_data)
	generate_today_report(cumulative_data)
	print("")
	generate_top_random_spends(normalised_data_rows)
	print('-'*20)
	
datafiles_long :List[str] = ['data-nov.txt', 'data-dec.txt', 'data-jan-19.txt']
for datafile in datafiles_long:
	generate_month_report(datafile)
