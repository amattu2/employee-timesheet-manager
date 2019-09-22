'''
Database Design:
	Employees:
		- ID
		- Name
		- Created
		- Deleted

	Timesheets:
		- ID
		- Month [Ex. 09]
		- Year [Ex. 2019]
		- Created
		- Deleted

	TimesheetDays
		- ID
		- EmployeeID
		- TimesheetID
		- Start [Ex. 07]
		- End [Ex. 22]
		- Comments [Ex. "Tester to Michigan"]
		- Date [Ex. 09/15/2019]
		- Deleted
'''

# Imports
from assets.queries import Query, where
from assets.database import TinyDB
from assets.fpdf import FPDF
from assets.scroll import ScrollFrame
from tkinter import Tk, Frame, Menu, PhotoImage, Toplevel, Label, Button, Text, LEFT, TOP, X, FLAT, RAISED, messagebox
from tkinter.ttk import Combobox, Style
from datetime import datetime
import calendar as Calendar
import os

# Variables
window = Tk()
calendar = Calendar.Calendar()
currentMonth = datetime.now().month
AccountConfig = {
	'Name': 'Employee Timesheet',
	'AccountName': 'Test Account',
	'SkipDays': [6]
}
UIConfig = {
	'PageWidthPX': 56,
	'PopupWidthPX': 44,
	'Color_Red': '#d32f2f',
	'Color_Blue': '#42a5f5',
	'Color_Orange': '#e67e22'
}
DataConfig = {
	'Database': 'data/database.json',
	'Tables': {
		'employees': 'Employee',
		'timesheets': 'Timesheet',
		'timesheetdays': 'TimesheetDay'
	},
	'Columns': {
		'employees': {
			'name': 'Name',
			'created': 'Created',
			'deleted': 'Deleted'
		},
		'timesheets': {
			'name': 'Name',
			'month': 'Month',
			'year': 'Year',
			'created': 'Created',
			'deleted': 'Deleted'
		}
	},
	'Formats': {
		'Date': '%Y-%m-%d %H:%M:%S'
	}
}
db = TinyDB(DataConfig['Database'], default_table = DataConfig['Tables']['employees'])
tables = {
	"employees": db.table(DataConfig['Tables']['employees']),
	"timesheets": db.table(DataConfig['Tables']['timesheets']),
	"timesheetdays": db.table(DataConfig['Tables']['timesheetdays'])
}
iconImage = PhotoImage(os.path.join(os.path.join(os.path.join(os.getcwd(), "assets"), "img"), "logo.bmp"))

# Functions
def createEmployee(Name):
	# Checks
	if (not type(Name) == str): return False
	if (not len(Name.strip()) > 0): return False

	# Insert
	tables["employees"].insert({
		DataConfig['Columns']['employees']['name']: str(Name),
		DataConfig['Columns']['employees']['deleted']: 0,
		DataConfig['Columns']['employees']['created']: datetime.today().strftime(DataConfig['Formats']['Date'])
	})

def createTimesheet(Month, Year):
	# Checks
	if (not type(Month) == str): return False
	if (not type(Year) == str): return False

	# Variables
	month = "01"
	year = "2001"
	name = ""

	# Parse Dates
	try:
		# Variables
		month = datetime.strptime(Month.lower(), "%b").strftime("%m")
		year = datetime.strptime(Year, "%Y").strftime("%Y")
		name = str(month +"-"+ year)
	except:
		return False

	# Check Existing
	result = tables["timesheets"].search(Query()[DataConfig['Columns']['timesheets']['name']] == name)
	if (result and len(result) > 0):
		messagebox.showerror(title = "Oops!", message = "It appears that a timesheet for {0} already exists.".format(name))
		return False

	# Insert
	tables["timesheets"].insert({
		DataConfig['Columns']['timesheets']['name']: str(name),
		DataConfig['Columns']['timesheets']['month']: str(month),
		DataConfig['Columns']['timesheets']['year']: str(year),
		DataConfig['Columns']['timesheets']['deleted']: 0,
		DataConfig['Columns']['timesheets']['created']: datetime.today().strftime(DataConfig['Formats']['Date'])
	})

def getTimesheets(default = False):
	# Variables
	months = tables["timesheets"].all()
	monthList = ["Month"] if default == True else []

	# Loops
	for month in months:
		# Checks
		if (not DataConfig['Columns']['timesheets']['deleted'] in month): continue
		if (month[DataConfig['Columns']['timesheets']['deleted']] == 1): continue

		# Push
		monthList.append(month[DataConfig['Columns']['timesheets']['name']])

	# Return
	return monthList

def getEmployees(default = False):
	# Variables
	employees = tables["employees"].all()
	employeeList = ["Select a employee"] if default == True else []

	# Loops
	for employee in employees:
		# Checks
		if (not DataConfig['Columns']['employees']['name'] in employee): continue
		if (not DataConfig['Columns']['employees']['deleted'] in employee): continue
		if (employee[DataConfig['Columns']['employees']['deleted']] == 1): continue

		# Push
		employeeList.append(employee["Name"])

	# Return
	return employeeList

def getTimeSheetDays(employee):
	pass
	# I need to figure out how to associate a unique ID with the employee
	# Then select all days for the employee

def getHeaderText():
	# Variables
	aname = AccountConfig['AccountName']
	date = datetime.now().strftime("%B, %Y")

	# Return
	return "Company: {0} | Date: {1}".format(aname, date)

def getMonths(default = False):
	# Variables
	monthList = ["Month"] if default == True else []
	index = datetime.now().month if default == True else datetime.now().month - 1

	# Loops
	for m in Calendar.month_abbr:
		if (len(m) <= 0): continue
		monthList.append(m)

	# Return
	return (monthList, index)

def getYears(default = False):
	# Variables
	currentYear = datetime.now().year
	nextYear = currentYear + 1
	yearList = ["Year"] if default == True else []
	index = 2 if default == True else 1

	# Loops
	for year in range(nextYear, nextYear - 5, -1):
		yearList.append(year)

	# Return
	return (yearList, index)

# Classes
class UI(Frame):
	def __init__(self):
		super().__init__()

		# Variables
		self.currentTimeSheet = ""
		self.currentEmployee = ""

		# Config
		self.master.title(AccountConfig['Name'])
		self.master.geometry("450x500")
		self.master.resizable(width = False, height = False)
		self.master.configure(background = '#f2f2f2')
		self.master.tk.call('wm', 'iconphoto', window._w, iconImage)
		self.master.option_add('*tearOff', False)
		self.combostyle = Style()
		self.combostyle.theme_create('combostyle', parent='alt', settings = {'TCombobox': {'configure': {'selectforeground': '#3b3b3b', 'selectbackground': '#ffffff', 'fieldbackground': '#ffffff', 'background': '#ffffff'}}})
		self.combostyle.theme_use('combostyle')
		self.build()

	def build(self):
		# Variables
		menu = Menu(self.master)
		dataMenu = Menu(menu)
		removeMenu = Menu(dataMenu)
		newSubMenu = Menu(dataMenu)
		removeSubMenu = Menu(removeMenu)
		exportSubMenu = Menu(menu)

		# Attributes
		exportSubMenu.add_command(label = "Timesheet", command = self.exportPopup)
		newSubMenu.add_command(label = "Employee", command = self.createEmployeePopup)
		newSubMenu.add_command(label = "Month", command = self.createTimesheetPopup)
		removeSubMenu.add_command(label = "Employee", command = self.removeEmployeePopup)
		dataMenu.add_cascade(label = 'New', menu = newSubMenu, underline = 0)
		dataMenu.add_cascade(label = 'Remove', menu = removeSubMenu, underline = 0)
		menu.add_cascade(label = "Data", underline = 0, menu = dataMenu)
		menu.add_cascade(label = "Export", underline = 0, menu = exportSubMenu)

		# UI
		self.master.config(menu = menu)
		self.buildUI()

	def buildUI(self):
		# Variables
		employeeSelectFrame = Frame(window, bg = UIConfig['Color_Blue'])
		status = Label(window, text = getHeaderText(), width = UIConfig['PageWidthPX'], height = "2", background = "#3b3b3b", fg = "#ffffff", anchor = "w", padx = 8)
		self.TSSelect = Combobox(employeeSelectFrame, values = getTimesheets(True), state = "readonly", height = "4", width = 10)
		self.employeeSelect = Combobox(employeeSelectFrame, values = getEmployees(True), state = "readonly", height = "4", width = str(UIConfig['PageWidthPX'] - 4 - 14))
		self.scrollFrame = ScrollFrame(window, "#f2f2f2")
		#self.timesheetFrame = Frame(self.scrollFrame.viewPort, bg = "#f2f2f2")

		# Attributes
		status.configure(font=("Sans-serif", 11, "normal"))
		status.grid(column = 0, row = 0)
		self.TSSelect.grid(column = 0, row = 1, pady = 16, padx = 8, sticky = "w")
		self.TSSelect.current(0)
		self.employeeSelect.grid(column = 1, row = 1, pady = 16, padx = 8, sticky = "w")
		self.employeeSelect.current(0)
		employeeSelectFrame.grid(column = 0, row = 1, pady = 0, padx = 0, sticky = "w")
		#self.scrollFrame.grid(column = 0, row = 2, sticky = "w")
		#self.timesheetFrame.grid(column = 0, row = 2, pady = 8, padx = 8, sticky = "w")

		# Events
		self.TSSelect.bind("<<ComboboxSelected>>", self.selectTimeSheet)
		self.employeeSelect.bind("<<ComboboxSelected>>", self.selectEmployee)

	def selectTimeSheet(self, event):
		# Checks
		if (not self.TSSelect.get()): return False
		if (self.TSSelect.get().lower() == "month"): return False

		self.currentTimeSheet = self.TSSelect.get()

	def selectEmployee(self, event):
		# Checks
		if (not self.employeeSelect.get()): return False
		if (self.employeeSelect.get().lower() == ""): return False
		if (self.employeeSelect.get().lower() == "select a employee"): return False

		# Variables
		row = 0
		self.currentEmployee = self.employeeSelect.get()

		# Loops
		for date in calendar.itermonthdates(2019, currentMonth):
			# Checks
			if (not date.month == currentMonth): continue
			if (date.weekday() in AccountConfig['SkipDays']): continue

			# Variables
			frame = Frame(self.scrollFrame.viewPort, width = UIConfig['PageWidthPX'], height = "10")
			status = Label(frame, text = date.strftime("%a, %B %d %Y"), width = "25", height = "2", anchor = "w", bg = "#f2f2f2", fg = "#3b3b3b", font=("Sans-serif", 10, "normal"))

			# Attributes
			status.grid(row = row, column = 0)
			frame.grid(column = 0, row = row, pady = 8, padx = 8, sticky = "w")

			# Increment
			row = row+1
		self.scrollFrame.grid(column = 0, row = 2, sticky = "w")

	def exportPopup(self):
		print("Present month & employee selection, then build pdf")

	def createEmployeePopup(self):
		# Functions
		def create():
			if (not textbox.get(1.0, 25.0)): return False
			if (not len(textbox.get(1.0, 25.0).strip()) > 0): return False
			createEmployee(textbox.get(1.0, 25.0).strip())
			popup.destroy()
			self.buildUI()

		# Variables
		popup = self.createPopup("Create Employee")
		status = Label(popup, text = "Create new employee", width = UIConfig['PopupWidthPX'], height = "2", background = "#3b3b3b", fg = "#ffffff", anchor = "w")
		textbox = Text(popup, width = str(UIConfig['PopupWidthPX'] - 3), height = 2)
		btn = Button(popup, text = "Create", width = str(UIConfig['PopupWidthPX'] - 6), command = create)

		# Attributes
		status.grid(column = 0, row = 0)
		textbox.grid(column = 0, row = 1, pady = 8, padx = 8, sticky = "w")
		btn.grid(column = 0, row = 2, pady = 8, padx = 8, sticky = "w")

	def removeEmployeePopup(self):
		pass

	def createTimesheetPopup(self):
		# Functions
		def create():
			if (not monthSelect.get()): return False
			if (not yearSelect.get()): return False
			if (monthSelect.get().lower() == "month"): return False
			if (yearSelect.get().lower() == "year"): return False

			createTimesheet(monthSelect.get(), yearSelect.get())
			popup.destroy()
			self.buildUI()

		# Variables
		months = getMonths()
		years = getYears()
		popup = self.createPopup("Create Timesheet")
		status = Label(popup, text = "Create new timesheet", width = UIConfig['PopupWidthPX'], height = "2", background = "#3b3b3b", fg = "#ffffff", anchor = "w")
		employeeSelectFrame = Frame(popup, bg = "#f2f2f2")
		monthSelect = Combobox(employeeSelectFrame, values = months[0], state = "readonly", height = "4", width = UIConfig['PopupWidthPX'] - 19)
		yearSelect = Combobox(employeeSelectFrame, values = years[0], state = "readonly", height = "4", width = 10)
		btn = Button(popup, text = "Create", width = str(UIConfig['PopupWidthPX'] - 6), command = create)

		# Attributes
		status.grid(column = 0, row = 0)
		monthSelect.grid(column = 0, row = 1, pady = 16, padx = 8, sticky = "w")
		monthSelect.current(months[1])
		yearSelect.grid(column = 1, row = 1, pady = 16, padx = 8, sticky = "w")
		yearSelect.current(years[1])
		employeeSelectFrame.grid(column = 0, row = 1, pady = 0, padx = 0, sticky = "w")
		btn.grid(column = 0, row = 2, pady = 8, padx = 8, sticky = "w")

	def createPopup(self, title):
		# Variables
		popup = Toplevel()

		# Attributes
		popup.title(title)
		popup.geometry("350x150")
		popup.resizable(width = False, height = False)
		popup.configure(background = '#f2f2f2')
		popup.lift()
		popup.focus_force()
		popup.attributes('-topmost', True)

		return popup

win = UI()
window.mainloop()
