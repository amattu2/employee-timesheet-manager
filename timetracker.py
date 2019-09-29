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
from tkinter import Tk, Frame, Menu, Toplevel, Label, Button, Text, Entry, LEFT, TOP, X, FLAT, RAISED, END, messagebox
from tkinter.ttk import Combobox, Style
from datetime import datetime
import calendar as Calendar
import os

# Variables
window = Tk()
calendar = Calendar.Calendar()
currentMonth = datetime.now().month
currentYear = datetime.now().year
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
		#self.master.resizable(width = False, height = False)
		self.master.configure(background = '#f2f2f2')
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
		topFrame = Frame(window)
		statusFrame = Frame(topFrame, bg = "#3b3b3b")
		inputFrame = Frame(topFrame, bg = UIConfig['Color_Blue'])
		status = Label(statusFrame, text = getHeaderText(), height = "2", background = "#3b3b3b", fg = "#ffffff", anchor = "w", padx = 8, font=("Sans-serif", 11, "normal"))
		self.TSSelect = Combobox(inputFrame, values = getTimesheets(True), state = "readonly", height = "4", width = "10")
		self.employeeSelect = Combobox(inputFrame, values = getEmployees(True), state = "readonly", height = "4", width = "38")
		self.scrollFrame = self.buildFrame()

		# Attributes
		status.grid(column = 0, columnspan = 2, row = 0)
		self.TSSelect.grid(column = 0, row = 1, pady = 16, padx = 8, sticky = "w")
		self.employeeSelect.grid(column = 1, row = 1, pady = 16, padx = 8, sticky = "w")
		statusFrame.pack(side = "top", fill = "x", expand = True, anchor = "n")
		inputFrame.pack(side = "top", fill = "x", expand = True, anchor = "n")
		topFrame.pack(side = "top", fill = "x", expand = True, anchor = "n")
		self.TSSelect.current(0)
		self.employeeSelect.current(0)

		# Events
		self.TSSelect.bind("<<ComboboxSelected>>", self.selectTimeSheet)
		self.employeeSelect.bind("<<ComboboxSelected>>", self.selectEmployee)

	def buildFrame(self):
		# Variables
		sf = ScrollFrame(window, "#f2f2f2")

		# Events
		sf.canvas.bind_all("<MouseWheel>", self.mw)
		sf.canvas.bind_all("<Button-4>", self.mw)
		sf.canvas.bind_all("<Button-5>", self.mw)

		# Return
		return sf

	def mw(self, event):
		# Checks
		if (event.num and event.num == 5):
			self.scrollFrame.canvas.yview_scroll(1, "units")
		elif (event.num and event.num == 4):
			self.scrollFrame.canvas.yview_scroll(-1, "units")
		elif (event.delta and event.delta < 0):
			self.scrollFrame.canvas.yview_scroll(1, "units")
		elif (event.delta and event.delta > 0):
			self.scrollFrame.canvas.yview_scroll(-1, "units")

	def focus(self, event):
		# Checks
		if (not event): return False
		if (not event.widget): return False
		if (not event.widget.get()): return False
		if (event.widget.get().lower() in ["start time", "end time"]):
			event.widget.delete(0, END)

	def blur(self, event, type = 0):
		# Checks
		if (not event): return False
		if (not event.widget): return False
		if (len(event.widget.get().strip()) <= 0):
			event.widget.insert(0, ("Start time" if type == 0 else "End time"))

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
		self.scrollFrame.pack_forget()
		self.scrollFrame = self.buildFrame()
		self.scrollFrame.pack(side = "top", fill = "both", expand = True)

		# Loops
		for date in calendar.itermonthdates(currentYear, currentMonth):
			# Checks
			if (not date.month == currentMonth): continue
			if (date.weekday() in AccountConfig['SkipDays']): continue

			# Variables
			bg = "#f2f3f5" if (row % 2 == 0) else "#ffffff"
			frame = Frame(self.scrollFrame.viewPort, bg = bg, bd = 1, relief = "solid")
			topFrame = Frame(frame, bg = bg)
			middleFrame = Frame(frame, bg = bg)
			bottomFrame = Frame(frame, bg = bg)
			date = Label(topFrame, text = date.strftime("%a, %B %d %Y"), height = "2", fg = "#3b3b3b", bg = bg, font=("Sans-serif", 11, "normal"))
			start = Entry(middleFrame)
			end = Entry(middleFrame)
			commentLabel = Label(bottomFrame, text = "Date Comments", height = "2", fg = "#3b3b3b", bg = bg, anchor = "w", font=("Sans-serif", 9, "normal"))
			comment = Text(bottomFrame, height = 2)

			# Attributes
			start.insert(0, "Start time")
			end.insert(0, "End time")
			date.grid(column = 0, row = 0, pady = 0, padx = 8, sticky = "w")
			start.grid(column = 0, row = 0, pady = 8, padx = 8, sticky = "w")
			end.grid(column = 1, row = 0, pady = 8, padx = 8, sticky = "w")
			commentLabel.pack(side = "top", fill = "x", expand = True, anchor = "w") #grid(column = 0, row = 0)
			comment.pack() #grid(column = 0, row = 1, pady = (0, 8), padx = 8)
			topFrame.pack(side = "top", fill = "x", expand = True)
			middleFrame.pack(side = "top", fill = "x", expand = True)
			bottomFrame.pack(side = "top", fill = "x", expand = True)
			frame.pack(side = "top", fill = "x", expand = True, anchor = "n")

			# Events
			start.bind("<FocusIn>", self.focus)
			start.bind("<FocusOut>", lambda e: self.blur(e, 0))
			end.bind("<FocusIn>", self.focus)
			end.bind("<FocusOut>", lambda e: self.blur(e, 1))

			# Increment
			row = row+1

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
