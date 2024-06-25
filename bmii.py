import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

# Create a database or connect to one
conn = sqlite3.connect('bmi_data.db')

# Create a cursor
c = conn.cursor()

# Create table
c.execute("""CREATE TABLE IF NOT EXISTS bmi_data (
            user_name TEXT,
            height REAL,
            weight REAL,
            bmi REAL,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")

# Commit changes
conn.commit()

# Close connection
conn.close()

# Function to calculate BMI and return category
def calculate_bmi(height, weight):
    bmi = weight / (height ** 2)
    if bmi < 16:
        return 'severely underweight', bmi
    elif 16 <= bmi < 18.5:
        return 'underweight', bmi
    elif 18.5 <= bmi < 25:
        return 'healthy', bmi
    elif 25 <= bmi < 30:
        return 'overweight', bmi
    elif bmi >= 30:
        return 'obese', bmi

# Function to insert data into the database
def save_to_db(user_name, height, weight, bmi, category):
    conn = sqlite3.connect('bmi_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO bmi_data (user_name, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?)",
              (user_name, height, weight, bmi, category))
    conn.commit()
    conn.close()

# Function to fetch historical data
def fetch_data(user_name):
    conn = sqlite3.connect('bmi_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bmi_data WHERE user_name = ?", (user_name,))
    data = c.fetchall()
    conn.close()
    return data

# Function to display historical data
def view_history(user_name):
    data = fetch_data(user_name)
    if data:
        history_window = tk.Toplevel()
        history_window.title("BMI History")
        
        for idx, record in enumerate(data):
            record_label = tk.Label(history_window, text=f"Record {idx+1}: {record[1:]}").pack()
    else:
        messagebox.showinfo("No Data", "No historical data found for the user.")

# Function to plot BMI trend
def plot_bmi_trend(user_name):
    data = fetch_data(user_name)
    if data:
        dates = [record[-1] for record in data]
        bmis = [record[3] for record in data]
        
        fig, ax = plt.subplots()
        ax.plot(dates, bmis, marker='o')
        ax.set(xlabel='Date', ylabel='BMI', title='BMI Trend Over Time')
        ax.grid()

        trend_window = tk.Toplevel()
        trend_window.title("BMI Trend")

        canvas = FigureCanvasTkAgg(fig, master=trend_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        messagebox.showinfo("No Data", "No historical data found for the user.")

# Function to handle calculate button click
def on_calculate():
    user_name = entry_name.get()
    height = float(entry_height.get())
    weight = float(entry_weight.get())
    
    if user_name and height > 0 and weight > 0:
        category, bmi = calculate_bmi(height, weight)
        result_label.config(text=f"BMI: {bmi:.2f}, Category: {category}")
        save_to_db(user_name, height, weight, bmi, category)
    else:
        messagebox.showerror("Input Error", "Please provide valid inputs.")

# Main Application
app = tk.Tk()
app.title("BMI Calculator")

# User Input Fields
tk.Label(app, text="Name").grid(row=0, column=0)
entry_name = tk.Entry(app)
entry_name.grid(row=0, column=1)

tk.Label(app, text="Height (meters)").grid(row=1, column=0)
entry_height = tk.Entry(app)
entry_height.grid(row=1, column=1)

tk.Label(app, text="Weight (kilograms)").grid(row=2, column=0)
entry_weight = tk.Entry(app)
entry_weight.grid(row=2, column=1)

# Calculate Button
calculate_button = tk.Button(app, text="Calculate BMI", command=on_calculate)
calculate_button.grid(row=3, column=0, columnspan=2)

# Result Label
result_label = tk.Label(app, text="BMI: N/A, Category: N/A")
result_label.grid(row=4, column=0, columnspan=2)

# History Button
history_button = tk.Button(app, text="View History", command=lambda: view_history(entry_name.get()))
history_button.grid(row=5, column=0, columnspan=2)

# Plot Trend Button
plot_button = tk.Button(app, text="Plot BMI Trend", command=lambda: plot_bmi_trend(entry_name.get()))
plot_button.grid(row=6, column=0, columnspan=2)

# Run the application
app.mainloop()
