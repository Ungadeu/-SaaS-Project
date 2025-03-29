import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import datetime
import calendar
import schedule
import time
import threading
from PIL import Image, ImageTk  # For image handling
import pytesseract
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Planner")
        self.root.minsize(800, 600)  # Increased size
        self.root.geometry("800x600")

        self.tasks = {}  # {date: [(title, type, time, location, reminder, image_path, recurring_days), ...]}
        self.default_tasks = []  # [(title, type, time, location), ...]
        self.reminder_jobs = {}  # {task_id: schedule_job}
        self.next_task_id = 1

        self.create_widgets()
        self.show_week_calendar()
        self.start_reminder_thread()

    def create_widgets(self):
        # Menu Bar
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Import Image Schedule", command=self.import_image_schedule)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

        # Calendar Frame
        self.calendar_frame = ttk.Frame(self.root, padding="10")
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)

        # Task List Display
        self.task_list = tk.Text(self.root, height=10, width=50)
        self.task_list.pack(pady=10)
        self.task_list.config(state=tk.DISABLED)

        # Buttons Frame
        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.pack(fill=tk.X)

        ttk.Button(self.button_frame, text="Add Task", command=self.prompt_add_task).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="View Tasks", command=self.view_tasks).grid(row=0, column=1, padx=5)
        ttk.Button(self.button_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        ttk.Button(self.button_frame, text="Show Month", command=self.show_month_calendar).grid(row=0, column=3, padx=5)
        ttk.Button(self.button_frame, text="Show Week", command=self.show_week_calendar).grid(row=0, column=4, padx=5)
        ttk.Button(self.button_frame, text="Default Tasks", command=self.manage_default_tasks).grid(row=0, column=5, padx=5)

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
                task_label = ttk.Label(self.calendar_frame, text=self.format_task_text(task))
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
                        task_label = ttk.Label(self.calendar_frame, text=self.format_task_text(task))
                        task_label.grid(row=row_index + j + 1, column=col_index, padx=5, pady=2)
                else:
                    empty_label = ttk.Label(self.calendar_frame, text="")
                    empty_label.grid(row=row_index, column=col_index, padx=5, pady=5)

    def clear_calendar_frame(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

    def format_task_text(self, task):
        title, task_type, time, location, reminder, image_path, recurring_days = task
        text = f"{title} ({task_type})"
        if time:
            text += f" @ {time}"
        if location:
            text += f" at {location}"
        return text

    def prompt_add_task(self):
        task_type = simpledialog.askstring("Add Task", "Enter task type (General, Appointment, To-Do):")
        if task_type:
            self.add_task_window(task_type)

    def add_task_window(self, task_type):
        task_window = tk.Toplevel(self.root)
        task_window.title(f"Add {task_type} Task")

        # Date Frame
        date_frame = ttk.Frame(task_window, padding="10")
        date_frame.pack(fill=tk.X)

        ttk.Label(date_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        date_entry = ttk.Entry(date_frame)
        date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Title Frame
        title_frame = ttk.Frame(task_window, padding="10")
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="Task Title:").grid(row=0, column=0, sticky=tk.W)
        title_entry = ttk.Entry(title_frame)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Time Frame (Optional)
        time_frame = ttk.Frame(task_window, padding="10")
        time_frame.pack(fill=tk.X)

        ttk.Label(time_frame, text="Time (HH:MM):").grid(row=0, column=0, sticky=tk.W)
        time_entry = ttk.Entry(time_frame)
        time_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Location Frame (Optional)
        location_frame = ttk.Frame(task_window, padding="10")
        location_frame.pack(fill=tk.X)

        ttk.Label(location_frame, text="Location:").grid(row=0, column=0, sticky=tk.W)
        location_entry = ttk.Entry(location_frame)
        location_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Reminder Frame (Optional)
        reminder_frame = ttk.Frame(task_window, padding="10")
        reminder_frame.pack(fill=tk.X)

        ttk.Label(reminder_frame, text="Reminder (HH:MM before):").grid(row=0, column=0, sticky=tk.W)
        reminder_entry = ttk.Entry(reminder_frame)
        reminder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Recurring Frame (Optional)
        recurring_frame = ttk.Frame(task_window, padding="10")
        recurring_frame.pack(fill=tk.X)

        ttk.Label(recurring_frame, text="Recurring Days (e.g., Mon,Wed,Fri):").grid(row=0, column=0, sticky=tk.W)
        recurring_entry = ttk.Entry(recurring_frame)
        recurring_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Image Frame (Optional)
        image_frame = ttk.Frame(task_window, padding="10")
        image_frame.pack(fill=tk.X)

        ttk.Label(image_frame, text="Image:").grid(row=0, column=0, sticky=tk.W)
        image_button = ttk.Button(image_frame, text="Browse", command=lambda: self.select_image(image_path_var))
        image_button.grid(row=0, column=1, padx=5)
        image_path_var = tk.StringVar()

        # Add Button
        add_button = ttk.Button(task_window, text="Add",
                                command=lambda: self.add_task(date_entry.get(), title_entry.get(), task_type,
                                                            time_entry.get(), location_entry.get(), reminder_entry.get(),
                                                            image_path_var.get(), recurring_entry.get(), task_window))
        add_button.pack(pady=10)

    def select_image(self, image_path_var):
        filename = filedialog.askopenfilename(initialdir="./", title="Select Image",
                                             filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("all files", "*.*")))
        if filename:
            image_path_var.set(filename)

    def add_task(self, date_str, task_title, task_type, time_str, location, reminder_str, image_path, recurring_days_str,
                 task_window):
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Validate date format

            time = time_str if time_str else None
            reminder = int(reminder_str) if reminder_str else None
            recurring_days = recurring_days_str.split(',') if recurring_days_str else []

            task = (task_title, task_type, time, location, reminder, image_path, recurring_days)

            if date_str in self.tasks:
                self.tasks[date_str].append(task)
            else:
                self.tasks[date_str] = [task]

            messagebox.showinfo("Success", "Task added successfully!")
            task_window.destroy()
            self.show_week_calendar()
            self.schedule_reminders()

        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")

    def view_tasks(self):
        date_str = simpledialog.askstring("View Tasks", "Enter date (YYYY-MM-DD):")

        if date_str:
            if date_str in self.tasks:
                tasks = self.tasks[date_str]
                self.task_list.config(state=tk.NORMAL)
                self.task_list.delete(1.0, tk.END)
                self.task_list.insert(tk.END, f"Tasks for {date_str}:\n")
                for task in tasks:
                    self.task_list.insert(tk.END, f"- {self.format_task_text(task)}\n")
                self.task_list.config(state=tk.DISABLED)
            else:
                self.task_list.config(state=tk.NORMAL)
                self.task_list.delete(1.0, tk.END)
                self.task_list.insert(tk.END, f"No tasks found for {date_str}.")
                self.task_list.config(state=tk.DISABLED)

    def delete_task(self):
        date_str = simpledialog.askstring("Delete Task", "Enter date (YYYY-MM-DD):")
        task_to_delete = simpledialog.askstring("Delete Task", "Enter task title:")

        if date_str and task_to_delete and date_str in self.tasks:
            new_tasks = []
            for task in self.tasks[date_str]:
                if task[0] != task_to_delete:
                    new_tasks.append(task)
            if len(new_tasks) < len(self.tasks[date_str]):
                self.tasks[date_str] = new_tasks
                if not new_tasks:
                    del self.tasks[date_str]
                messagebox.showinfo("Success", "Task deleted successfully!")
                self.show_week_calendar()
                self.schedule_reminders()
            else:
                messagebox.showerror("Error", "Task not found.")
        else:
            messagebox.showerror("Error", "Task not found.")

    def import_image_schedule(self):
        filename = filedialog.askopenfilename(initialdir="./", title="Select Image",
                                             filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("all files", "*.*")))
        if filename:
            try:
                text = pytesseract.image_to_string(Image.open(filename))
                self.parse_schedule_text(text)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading image: {e}")

    def parse_schedule_text(self, text):
        # This is a very basic example; you'll need to adapt it to your schedule format
        lines = text.split('\n')
        for line in lines:
            parts = line.split(' ')  # Simple split; improve with regex for complex formats
            if len(parts) >= 3:
                try:
                    date_str = parts[0]
                    datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Validate date
                    task_title = ' '.join(parts[1:])
                    self.add_task(date_str, task_title, "General", None, None, None, None, None, None)
                except ValueError:
                    pass  # Skip lines that don't match date format
        self.show_week_calendar()
        self.schedule_reminders()

    def manage_default_tasks(self):
        default_task_window = tk.Toplevel(self.root)
        default_task_window.title("Manage Default Tasks")

        # Listbox to display default tasks
        task_listbox = tk.Listbox(default_task_window)
        for task in self.default_tasks:
            task_listbox.insert(tk.END, self.format_task_text(task))
        task_listbox.pack(pady=10)

        # Buttons to add and delete default tasks
        add_button = ttk.Button(default_task_window, text="Add Default Task", command=self.add_default_task)
        add_button.pack(side=tk.LEFT, padx=5)
        delete_button = ttk.Button(default_task_window, text="Delete Default Task", command=lambda: self.delete_default_task(task_listbox))
        delete_button.pack(side=tk.LEFT, padx=5)
        use_button = ttk.Button(default_task_window, text="Use Default Task", command=lambda: self.use_default_task(task_listbox))
        use_button.pack(side=tk.LEFT, padx=5)

    def add_default_task(self):
        task_type = simpledialog.askstring("Add Default Task", "Enter task type:")
        task_title = simpledialog.askstring("Add Default Task", "Enter task title:")
        time = simpledialog.askstring("Add Default Task", "Enter time (HH:MM):")
        location = simpledialog.askstring("Add Default Task", "Enter location:")

        if task_type and task_title:
            self.default_tasks.append((task_title, task_type, time, location, None, None, None))
            self.manage_default_tasks()  # Refresh the default task window

    def delete_default_task(self, task_listbox):
        selected_index = task_listbox.curselection()
        if selected_index:
            self.default_tasks.pop(selected_index[0])
            self.manage_default_tasks()

    def use_default_task(self, task_listbox):
        selected_index = task_listbox.curselection()
        if selected_index:
            task = self.default_tasks[selected_index[0]]
            date_str = simpledialog.askstring("Use Default Task", "Enter date (YYYY-MM-DD):")
            if date_str:
                try:
                    datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    if date_str in self.tasks:
                        self.tasks[date_str].append(task)
                    else:
                        self.tasks[date_str] = [task]
                    self.show_week_calendar()
                    self.schedule_reminders()
                    messagebox.showinfo("Success", "Default task added to schedule.")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format.")

    def schedule_reminders(self):
        schedule.clear()
        self.reminder_jobs.clear()

        for date_str, task_list in self.tasks.items():
            try:
                task_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            for task in task_list:
                title, task_type, time, location, reminder, image_path, recurring_days = task
                if time and reminder:
                    try:
                        task_time = datetime.datetime.strptime(time, "%H:%M").time()
                        reminder_time = (datetime.datetime.combine(task_date, task_time) - datetime.timedelta(minutes=reminder)).time()

                        def reminder_function(task_title=title, task_date=task_date):
                            messagebox.showinfo("Reminder", f"Reminder: {task_title} on {task_date}")

                        schedule.every().day.at(reminder_time.strftime("%H:%M")).do(reminder_function)
                        self.reminder_jobs[self.next_task_id] = schedule.jobs[-1]  # Store the job
                        self.next_task_id += 1

                    except ValueError:
                        print(f"Invalid time format for task: {title}")

    def start_reminder_thread(self):
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        reminder_thread = threading.Thread(target=run_schedule, daemon=True)
        reminder_thread.start()

    def check_weather_and_traffic(self, date_str, task):
        title, task_type, time, location, reminder, image_path, recurring_days = task
        if location:
            try:
                geolocator = Nominatim(user_agent="planner_app")
                location_obj = geolocator.geocode(location)
                if location_obj:
                    lat, lon = location_obj.latitude, location_obj.longitude

                    # Weather Check (Replace with your preferred API)
                    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=YOUR_WEATHER_API_KEY"  # Replace with your key
                    weather_response = requests.get(weather_url)
                    weather_data = weather_response.json()
                    weather_description = weather_data['weather'][0]['description']

                    # Traffic Check (Complex; Requires a good traffic API)
                    # You'll likely need a paid Google Maps API for reliable traffic.
                    # For now, a simplified placeholder:
                    traffic_warning = "Traffic check unavailable (replace with API call)"

                    if "rain" in weather_description or "snow" in weather_description:
                        messagebox.showwarning("Weather Alert", f"Weather alert for {title}: {weather_description}")
                    if "heavy traffic" in traffic_warning:  # Placeholder
                        messagebox.showwarning("Traffic Alert", f"Traffic alert for {title}: {traffic_warning}")

            except Exception as e:
                print(f"Error checking weather/traffic for {title}: {e}")

    def suggest_breaks(self, date_str):
        tasks = self.tasks.get(date_str, [])
        time_specific_tasks = [task for task in tasks if task[2]]  # Check for time

        if len(time_specific_tasks) > 2:
            messagebox.showinfo("Break Reminder",
                              "Consider scheduling breaks today to avoid stress. (AI-powered personalized suggestions are a future feature!)")

    def run_daily_checks(self):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        tasks_today = self.tasks.get(today_str, [])

        self.suggest_breaks(today_str)

        for task in tasks_today:
            self.check_weather_and_traffic(today_str, task)

    def start_daily_check_thread(self):
        def run_daily():
            while True:
                self.run_daily_checks()
                time.sleep(60 * 60 * 24)  # Check daily

        daily_check_thread = threading.Thread(target=run_daily, daemon=True)
        daily_check_thread.start()

    def add_todo_task(self):
        todo_task_window = tk.Toplevel(self.root)
        todo_task_window.title("Add To-Do Task")

        # Title Frame
        title_frame = ttk.Frame(todo_task_window, padding="10")
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="Task Title:").grid(row=0, column=0, sticky=tk.W)
        title_entry = ttk.Entry(title_frame)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Days of the Week Frame
        days_frame = ttk.Frame(todo_task_window, padding="10")
        days_frame.pack(fill=tk.X)

        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_vars = [tk.BooleanVar() for _ in days_of_week]
        for i, day in enumerate(days_of_week):
            check_button = ttk.Checkbutton(days_frame, text=day, variable=day_vars[i])
            check_button.grid(row=0, column=i, padx=5)

        # Add Button
        add_button = ttk.Button(todo_task_window, text="Add",
                                command=lambda: self.add_todo_task_to_schedule(title_entry.get(), day_vars,
                                                                             todo_task_window))
        add_button.pack(pady=10)

    def add_todo_task_to_schedule(self, task_title, day_vars, todo_task_window):
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        selected_days = [days_of_week[i] for i, var in enumerate(day_vars) if var.get()]

        if task_title and selected_days:
            today = datetime.date.today()
            for day in selected_days:
                day_index = days_of_week.index(day)
                days_until_next = (day_index - today.weekday()) % 7
                next_occurrence = today + datetime.timedelta(days=days_until_next)
                date_str = next_occurrence.strftime("%Y-%m-%d")

                task = (task_title, "To-Do", None, None, None, None, [day])  # Store the day in recurring_days
                if date_str in self.tasks:
                    self.tasks[date_str].append(task)
                else:
                    self.tasks[date_str] = [task]

            messagebox.showinfo("Success", "To-Do task added to schedule!")
            todo_task_window.destroy()
            self.show_week_calendar()
            self.schedule_reminders()
        else:
            messagebox.showerror("Error", "Please enter a task title and select at least one day.")

    def add_recurring_tasks(self):
        today = datetime.date.today()
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for date_str, task_list in self.tasks.copy().items():  # Iterate over a copy to avoid modification errors
            for task in task_list.copy():
                title, task_type, time, location, reminder, image_path, recurring_days = task
                if recurring_days:
                    try:
                        task_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        for day in recurring_days:
                            day_index = days_of_week.index(day)
                            days_until_next = (day_index - task_date.weekday()) % 7
                            next_occurrence = task_date + datetime.timedelta(days=days_until_next)

                            # If the next occurrence is in the future, add the task
                            if next_occurrence > today:
                                next_date_str = next_occurrence.strftime("%Y-%m-%d")
                                if next_date_str in self.tasks:
                                    self.tasks[next_date_str].append(
                                        (title, task_type, time, location, reminder, image_path, recurring_days))
                                else:
                                    self.tasks[next_date_str] = [(
                                        title, task_type, time, location, reminder, image_path, recurring_days)]

                    except ValueError:
                        print(f"Invalid date format for recurring task: {title}")

    def start_recurring_task_thread(self):
        def run_recurring_task_check():
            while True:
                self.add_recurring_tasks()
                self.show_week_calendar()
                self.schedule_reminders()
                time.sleep(60 * 60 * 24)  # Check daily

        recurring_task_thread = threading.Thread(target=run_recurring_task_check, daemon=True)
        recurring_task_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    app.start_daily_check_thread()
    app.start_recurring_task_thread()
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