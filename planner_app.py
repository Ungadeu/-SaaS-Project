import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import calendar

class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Planner")
        self.root.minsize(600, 400)  # Set the minimum window size

        self.tasks = {}  # Dictionary to store tasks: {date: [task1, task2, ...]}

        # Calendar Frame
        self.calendar_frame = ttk.Frame(root, padding="10")
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)

        self.show_week_calendar()

        # Task List Display
        self.task_list = tk.Text(root, height=10, width=50)
        self.task_list.pack(pady=10)
        self.task_list.config(state=tk.DISABLED)

        # Buttons Frame
        button_frame = ttk.Frame(root, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Add Event", command=self.prompt_add_event).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Tasks", command=self.view_tasks).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Show Month", command=self.show_month_calendar).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Show Week", command=self.show_week_calendar).grid(row=0, column=4, padx=5)

    def show_week_calendar(self):
        self.clear_calendar_frame()
        today = datetime.date.today()
        start_week = today - datetime.timedelta(days=today.weekday())
        for i in range(7):
            current_day = start_week + datetime.timedelta(days=i)
            day_label = ttk.Label(self.calendar_frame, text=current_day.strftime("%a %Y-%m-%d"))
            day_label.grid(row=0, column=i, padx=5, pady=5)
            day_tasks = self.tasks.get(str(current_day), [])
            for j, task in enumerate(day_tasks):
                task_label = ttk.Label(self.calendar_frame, text=task)
                task_label.grid(row=j + 1, column=i, padx=5, pady=2)

    def show_month_calendar(self):
        self.clear_calendar_frame()
        today = datetime.date.today()
        month_calendar = calendar.monthcalendar(today.year, today.month)
        for row_index, week in enumerate(month_calendar):
            for col_index, day in enumerate(week):
                day_str = ""
                if day != 0:
                    current_day = datetime.date(today.year, today.month, day)
                    day_str = current_day.strftime("%Y-%m-%d")
                    day_label = ttk.Label(self.calendar_frame, text=day_str)
                    day_label.grid(row=row_index, column=col_index, padx=5, pady=5)
                    day_tasks = self.tasks.get(day_str, [])
                    for j, task in enumerate(day_tasks):
                        task_label = ttk.Label(self.calendar_frame, text=task)
                        task_label.grid(row=row_index + j + 1, column=col_index, padx=5, pady=2)
                else:
                    empty_label = ttk.Label(self.calendar_frame, text="")
                    empty_label.grid(row=row_index, column=col_index, padx=5, pady=5)

    def clear_calendar_frame(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

    def prompt_add_event(self):
        result = messagebox.askyesno("Add Event", "Do you want to add an event?")
        if result:
            self.add_event_window()

    def add_event_window(self):
        event_window = tk.Toplevel(self.root)
        event_window.title("Add Event")

        # Date Frame
        date_frame = ttk.Frame(event_window, padding="10")
        date_frame.pack(fill=tk.X)

        ttk.Label(date_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        date_entry = ttk.Entry(date_frame)
        date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Title Frame
        title_frame = ttk.Frame(event_window, padding="10")
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="Event Title:").grid(row=0, column=0, sticky=tk.W)
        title_entry = ttk.Entry(title_frame)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Add Button
        add_button = ttk.Button(event_window, text="Add", command=lambda: self.add_event(date_entry.get(), title_entry.get(), event_window))
        add_button.pack(pady=10)

    def add_event(self, date_str, event_title, event_window):
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Validate date format
            if date_str in self.tasks:
                self.tasks[date_str].append(event_title)
            else:
                self.tasks[date_str] = [event_title]
            messagebox.showinfo("Success", "Event added successfully!")
            event_window.destroy()  # Close the event window after adding
            self.show_week_calendar()  # Update the calendar
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Useтрибу-MM-DD.")

    def view_tasks(self):
        date_str = simpledialog.askstring("View Tasks", "Enter date (YYYY-MM-DD):")

        if date_str:
            if date_str in self.tasks:
                tasks = self.tasks[date_str]
                self.task_list.config(state=tk.NORMAL)
                self.task_list.delete(1.0, tk.END)
                self.task_list.insert(tk.END, f"Tasks for {date_str}:\n")
                for task in tasks:
                    self.task_list.insert(tk.END, f"- {task}\n")
                self.task_list.config(state=tk.DISABLED)
            else:
                self.task_list.config(state=tk.NORMAL)
                self.task_list.delete(1.0, tk.END)
                self.task_list.insert(tk.END, f"No tasks found for {date_str}.")
                self.task_list.config(state=tk.DISABLED)

    def delete_task(self):
        date_str = simpledialog.askstring("Delete Task", "Enter date (YYYY-MM-DD):")
        task = simpledialog.askstring("Delete Task", "Enter task title:")

        if date_str and task:
            if date_str in self.tasks and task in self.tasks[date_str]:
                self.tasks[date_str].remove(task)
                if not self.tasks[date_str]:
                    del self.tasks[date_str]  # Remove date if no tasks left
                messagebox.showinfo("Success", "Task deleted successfully!")
                self.show_week_calendar() #update calendar
            else:
                messagebox.showerror("Error", "Task not found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()


#Details:{}
#Tkinter GUI: Uses Tkinter for a simple graphical user interface.
#Date Input: Allows users to enter dates in YYYY-MM-DD format.
#Task Input: Users can enter tasks to be associated with specific dates.
#Add Task: Adds tasks to the internal tasks dictionary.
#View Tasks: Displays the tasks for a given date in the text area.
#Delete Task: Removes a task from a given date.
#Date Validation: Checks the date format to prevent errors.
#Error Handling: Uses messagebox to display error and success messages.
#Task Storage: Uses a Python dictionary to store tasks.
#The code now displays a calendar in the calendar_frame.
#show_week_calendar(): Displays the current week.
#show_month_calendar(): displays the current month.
#clear_calendar_frame(): clears the frame so the new calendar can be displayed.
#The calendar displays the dates and any tasks associated with those dates.
#Added buttons to switch between week and month views.
#Uses datetime and calendar modules to calculate dates and create the calendar display.
#Tasks are displayed below their corresponding dates in the calendar.
#self.root.minsize(600, 400) was added to the init function to set the minimum size of the window.
#The calendar is updated after adding or deleting tasks.
#
#