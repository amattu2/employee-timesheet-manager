import tkinter as tk

class ScrollFrame(tk.Frame):
	def __init__(self, parent, background):
		super().__init__(parent)

		self.canvas = tk.Canvas(self, borderwidth=0, background=background, height = "1000")
		self.viewPort = tk.Frame(self.canvas, background=background)
		self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.vsb.set)

		self.vsb.pack(side="right", fill="y")
		self.canvas.pack(side="left", fill="both", expand=True)
		self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort")

		self.viewPort.bind("<Configure>", self.onFrameConfigure)

	def onFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
