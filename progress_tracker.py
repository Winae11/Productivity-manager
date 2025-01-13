import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class ProgressTracker:
    def __init__(self, master):
        self.master = master
        self.figure = Figure(figsize=(8, 5), dpi=100)
        
        # Create multiple subplots
        self.daily_plot = self.figure.add_subplot(121)
        self.priority_plot = self.figure.add_subplot(122)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_charts(self, completed, pending, priority_stats):
        # Clear previous plots
        self.daily_plot.clear()
        self.priority_plot.clear()
        
        # Daily progress chart
        tasks = ['Completed', 'Pending']
        counts = [completed, pending]
        bars = self.daily_plot.bar(tasks, counts, color=['#2ecc71', '#e74c3c'])
        self.daily_plot.set_title('Daily Progress')
        
        # Priority breakdown pie chart
        priorities = [stat[0] for stat in priority_stats]
        totals = [stat[1] for stat in priority_stats]
        self.priority_plot.pie(totals, labels=priorities, autopct='%1.1f%%')
        self.priority_plot.set_title('Tasks by Priority')
        
        self.figure.tight_layout()
        self.canvas.draw() 