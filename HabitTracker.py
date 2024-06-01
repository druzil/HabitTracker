import tkinter as tk
from tkinter import simpledialog, ttk
from datetime import datetime, timedelta
import json
import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# File for saving state
state_file = "habit_tracker_state.json"

# Default application size
default_size = "1000x600"

# Create the main application window
root = tk.Tk()
root.title("Habit Tracker")
root.iconbitmap('HabitTracker.ico')

# Save window size before closing
def on_closing():
    state['window_size'] = root.geometry()  # Save current geometry
    save_state()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Setup the notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# Load saved state
# Load and handle state properly
def load_state():
    if os.path.exists(state_file):
        with open(state_file, 'r') as file:
            data = json.load(file)
        # Prepare state data
        for key, value in data.items():
            if isinstance(value, dict) and 'start_date' not in value:
                value['start_date'] = datetime.now().strftime("%Y-%m-%d")  # Set today if missing
        return data
    else:
        return {}


# Define constants
days_to_display = 60
icons = ["✔️", "❌", "❓"]
current_day = datetime.today()


# Save current state
def save_state():
    global state  # This ensures that the function accesses the global state variable
    with open(state_file, 'w') as file:
        json.dump(state, file)


# Function to change the icon
def change_icon(button, day_str, tracker):
    current_icon = button["text"]
    next_icon = icons[(icons.index(current_icon) + 1) % len(icons)]
    button.config(text=next_icon)
    state[tracker]['days'][day_str] = next_icon
    save_state()  # No argument needed

# Function to add or create a new tracker
def add_new_tracker():
    tracker_name = simpledialog.askstring("New Tracker", "Enter name for the new tracker:")
    if tracker_name and tracker_name not in state:
        start_date = datetime.now().strftime("%Y-%m-%d")  # Use correct date formatting
        state[tracker_name] = {'title': tracker_name, 'days': {}, 'start_date': start_date}  # Use 'start_date'
        create_tracker(tracker_name)
        save_state()

# Create a tracker tab
def create_tracker(tracker_name):
    tracker_info = state[tracker_name]
    tracker_frame = ttk.Frame(notebook)

    # Customize tab label with title and a close icon
    tab_text = f"{tracker_info['title']}  ❌"
    notebook.add(tracker_frame, text=tab_text)

    # Add a mouse click event to the notebook to handle clicks on the 'X'
    notebook.bind('<Button-3>', on_right_click, add="+")

    # Correct the key here to 'start_date'
    start_date = datetime.strptime(tracker_info['start_date'], "%Y-%m-%d")
    tab_id = notebook.index(tracker_frame)
    
    calendar_frame = tk.Frame(tracker_frame)
    calendar_frame.pack(pady=20)
    
    # Generate buttons from the start date
    for i in range(days_to_display):
        day = start_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        date_label = tk.Label(calendar_frame, text=day.strftime("%d %b"))
        date_label.grid(row=((i // 7) * 2) + 1, column=i % 7, padx=5, pady=2)
        
        icon = tracker_info['days'].get(day_str, "❓")
        day_button = tk.Button(calendar_frame, text=icon, width=5, height=2)
        day_button.grid(row=((i // 7) * 2) + 2, column=i % 7, padx=5, pady=2)
        day_button.config(command=lambda b=day_button, ds=day_str, t=tracker_name: change_icon(b, ds, t))

def on_right_click(event):
    # Identify the tab under cursor
    clicked_tab = notebook.tk.call(notebook._w, "identify", "tab", event.x, event.y)
    if clicked_tab != "":
        tracker_name = notebook.tab(notebook.tabs()[int(clicked_tab)], "text").split("  ❌")[0]  # Remove '❌' from name
        confirm_delete(tracker_name)

def confirm_delete(tracker_name):
    response = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{tracker_name}'?")
    if response:
        delete_tracker(tracker_name)

def delete_tracker(tracker_name):
    for tab in notebook.tabs():
        if notebook.tab(tab, "text").startswith(tracker_name):
            notebook.forget(tab)
            break
    if tracker_name in state:
        del state[tracker_name]
        save_state()

# Correctly handling the title update
def update_title(event, tab_id, tracker_name):
    new_title = event.widget.get()
    notebook.tab(tab_id, text=new_title)  # Correct usage
    state[tracker_name]['title'] = new_title
    save_state()

# Update only tracker creation, excluding window_size
state = load_state()
for name, details in state.items():
    if name == 'window_size':
        continue  # Skip the window size key
    create_tracker(name)

# Ensure the geometry is set from a valid source
window_size = state.get('window_size', default_size)
root.geometry(window_size)

if not state:
    state["Default Tracker"] = {"title": "Default Tracker", "days": {}}
    save_state()

new_tracker_tab = ttk.Frame(notebook)
notebook.add(new_tracker_tab, text="+ Add New Tracker")
new_tracker_tab.bind("<Visibility>", lambda e: add_new_tracker())

root.mainloop()
