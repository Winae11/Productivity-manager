import tkinter as tk
from tkinter import ttk, messagebox
from task_manager import TaskManager, Priority
from pomodoro_timer import PomodoroTimer
from progress_tracker import ProgressTracker
from motivation import QuoteManager
import datetime

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity App")
        self.root.geometry("1000x700")  # Larger window
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # or 'alt', 'default', 'classic' depending on your OS
        
        # Configure colors
        style.configure(".", font=('Helvetica', 10))
        style.configure("Treeview", rowheight=25)
        style.configure("TButton", padding=6, relief="flat", background="#2980b9")
        style.configure("Accent.TButton", background="#27ae60")
        
        # Configure custom styles for priority levels
        style.configure("High.TLabel", foreground="red")
        style.configure("Medium.TLabel", foreground="orange")
        style.configure("Low.TLabel", foreground="green")

        self.task_manager = TaskManager()
        self.pomodoro = PomodoroTimer()
        self.quote_manager = QuoteManager()
        
        self.setup_gui()
        self.refresh_tasks()

    def setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True)

        # Tasks tab
        tasks_frame = ttk.Frame(notebook)
        notebook.add(tasks_frame, text="Tasks")
        
        # Add task form
        form_frame = ttk.Frame(tasks_frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Task:").grid(row=0, column=0, padx=5)
        self.task_entry = ttk.Entry(form_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Priority:").grid(row=0, column=2, padx=5)
        self.priority_var = tk.StringVar(value=Priority.MEDIUM.value)
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var)
        priority_combo['values'] = [p.value for p in Priority]
        priority_combo.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Deadline:").grid(row=0, column=4, padx=5)
        self.deadline_entry = ttk.Entry(form_frame, width=10)
        self.deadline_entry.grid(row=0, column=5, padx=5)
        self.deadline_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        ttk.Button(form_frame, text="Add Task", command=self.add_task).grid(row=0, column=6, padx=5)

        # Tasks table
        self.tree = ttk.Treeview(tasks_frame, columns=("ID", "Task", "Priority", "Status", "Deadline"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Task actions
        actions_frame = ttk.Frame(tasks_frame)
        actions_frame.pack(pady=5)
        ttk.Button(actions_frame, text="Toggle Status", command=self.toggle_task_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)

        # Pomodoro tab
        pomodoro_frame = ttk.Frame(notebook)
        notebook.add(pomodoro_frame, text="Pomodoro")

        self.timer_label = ttk.Label(pomodoro_frame, text="25:00", font=("Arial", 48))
        self.timer_label.pack(pady=20)

        timer_buttons = ttk.Frame(pomodoro_frame)
        timer_buttons.pack(pady=10)
        ttk.Button(timer_buttons, text="Start", command=self.start_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_buttons, text="Pause", command=self.pause_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_buttons, text="Reset", command=self.reset_timer).pack(side=tk.LEFT, padx=5)

        self.quote_label = ttk.Label(pomodoro_frame, text="", wraplength=400)
        self.quote_label.pack(pady=20)

        # Progress tab
        progress_frame = ttk.Frame(notebook)
        notebook.add(progress_frame, text="Progress")
        self.progress_tracker = ProgressTracker(progress_frame)

        # Statistics tab
        self.create_stats_tab(notebook)

    def add_task(self):
        name = self.task_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a task name")
            return

        priority = Priority(self.priority_var.get())
        deadline = self.deadline_entry.get()

        self.task_manager.add_task(name, priority, deadline)
        self.task_entry.delete(0, tk.END)
        self.refresh_tasks()

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = self.task_manager.get_all_tasks()
        for task in tasks:
            self.tree.insert("", tk.END, values=task)

        # Update progress chart
        stats = self.task_manager.get_progress_stats()
        if stats:
            # Get priority stats for the enhanced chart
            priority_stats = self.task_manager.get_tasks_by_priority()
            self.progress_tracker.update_charts(stats[0] or 0, stats[1] or 0, priority_stats)

    def toggle_task_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task_id = self.tree.item(selected[0])['values'][0]
        self.task_manager.toggle_task_status(task_id)
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            task_id = self.tree.item(selected[0])['values'][0]
            self.task_manager.delete_task(task_id)
            self.refresh_tasks()

    def update_timer_display(self, remaining_time, is_break):
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        if remaining_time == 0:
            self.quote_label.config(text=self.quote_manager.get_quote())

    def start_timer(self):
        self.pomodoro.start(self.update_timer_display)

    def pause_timer(self):
        self.pomodoro.pause()

    def reset_timer(self):
        self.pomodoro.reset()

    def create_stats_tab(self, notebook):
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        
        # Today's Summary
        summary_frame = ttk.LabelFrame(stats_frame, text="Today's Summary")
        summary_frame.pack(pady=10, padx=10, fill="x")
        
        self.stats_labels = {
            'focus_time': ttk.Label(summary_frame, text="Total Focus Time: 0h 0m"),
            'completed_tasks': ttk.Label(summary_frame, text="Completed Tasks: 0"),
            'pomodoros': ttk.Label(summary_frame, text="Pomodoro Sessions: 0/4")
        }
        
        for label in self.stats_labels.values():
            label.pack(pady=5)
        
        # Weekly view
        weekly_frame = ttk.LabelFrame(stats_frame, text="Weekly Overview")
        weekly_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.weekly_progress = ProgressTracker(weekly_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop() 