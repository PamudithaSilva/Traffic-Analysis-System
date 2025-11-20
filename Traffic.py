# Author: Pamuditha Shaluka Silva
# Date: 12/20/2024
# Student ID: 20240048 / w2119838

import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict


# ======================================================
#                PART A – CSV PROCESSING LOGIC
# ======================================================

def process_csv_data(file_path):
    """Load CSV file data."""
    with open(file_path, mode="r") as file:
        return list(csv.DictReader(file))


def generate_statistics(outcomes, file_name):
    """Compute traffic statistics but return as text."""

    total_vehicles = len(outcomes)
    total_trucks = [r for r in outcomes if r["VehicleType"].lower() == "truck"]
    total_elec = [r for r in outcomes if r["elctricHybrid"].lower() == "true"]
    total_two = [r for r in outcomes if r["VehicleType"].lower() in
                 {"bicycle", "motorcycle", "scooter"}]
    total_buses_north = [
        r for r in outcomes
        if r["JunctionName"] == "Elm Avenue/Rabbit Road"
           and r["travel_Direction_out"] == "N"
           and r["VehicleType"].lower() == "buss"
    ]
    vehicles_no_turn = [
        r for r in outcomes if r["travel_Direction_in"] == r["travel_Direction_out"]
    ]
    percentage_trucks = f"{round(len(total_trucks) / total_vehicles * 100)}%" if total_vehicles else "0%"
    total_bikes = [r for r in outcomes if r["VehicleType"].lower() == "bicycle"]
    avg_bikes_per_hour = int(len(total_bikes) / 24) if total_bikes else 0
    over_speed = [
        r for r in outcomes if int(r["VehicleSpeed"]) > int(r["JunctionSpeedLimit"])
    ]

    elm = [r for r in outcomes if r["JunctionName"] == "Elm Avenue/Rabbit Road"]
    hanley = [r for r in outcomes if r["JunctionName"] == "Hanley Highway/Westway"]

    scooters = [r for r in outcomes if r["VehicleType"].lower() == "scooter"]
    scooters_at_elm = [r for r in scooters if r["JunctionName"] == "Elm Avenue/Rabbit Road"]
    scooters_percent = f"{round(len(scooters_at_elm) / len(elm) * 100)}%" if elm else "0%"

    # Peak Hour Calculation
    peak_hours = defaultdict(int)
    for r in hanley:
        hour = r["timeOfDay"].split(":")[0]
        peak_hours[hour] += 1

    busiest_count = max(peak_hours.values(), default=0)

    peak_times = [
        f"{hour}:00 - {int(hour) + 1}:00"
        for hour, count in peak_hours.items()
        if count == busiest_count
    ]

    # Rainy hours
    rainy_hours = [
        r["timeOfDay"].split(":")[0]
        for r in outcomes
        if r.get("Weather_Conditions", "").strip().lower() in ("light rain", "heavy rain")
    ]
    rainy_count = len(set(rainy_hours))

    # Return formatted text
    text = f"Selected File: {file_name}\n"
    text += f"Total Vehicles: {total_vehicles}\n"
    text += f"Total Trucks: {len(total_trucks)}\n"
    text += f"Total Electric Vehicles: {len(total_elec)}\n"
    text += f"Total Two-Wheeled Vehicles: {len(total_two)}\n"
    text += f"Buses Heading North (Elm): {len(total_buses_north)}\n"
    text += f"Vehicles With No Turning: {len(vehicles_no_turn)}\n"
    text += f"Percentage Trucks: {percentage_trucks}\n"
    text += f"Average Bikes per Hour: {avg_bikes_per_hour}\n"
    text += f"Over Speed Vehicles: {len(over_speed)}\n"
    text += f"Elm Avenue Vehicles: {len(elm)}\n"
    text += f"Hanley Highway Vehicles: {len(hanley)}\n"
    text += f"Scooters Percentage at Elm: {scooters_percent}\n"
    text += f"Highest Vehicle Count in an Hour: {busiest_count}\n"
    text += "Peak Hours: " + ", ".join(peak_times) + "\n"
    text += f"Hours with Rain: {rainy_count}\n"
    return text


# ======================================================
#                PART B – HISTOGRAM WINDOW
# ======================================================

class HistogramApp:
    def __init__(self, traffic_data, date):
        self.data = traffic_data
        self.date = date

    def run(self):
        root = tk.Toplevel()
        root.title(f"Histogram - {self.date}")
        canvas = tk.Canvas(root, width=1400, height=700, bg="white")
        canvas.pack()

        hourly = {}
        for r in self.data:
            h = r["timeOfDay"].split(":")[0]
            j = r["JunctionName"]
            if h not in hourly:
                hourly[h] = {"Elm Avenue/Rabbit Road": 0,
                             "Hanley Highway/Westway": 0}
            hourly[h][j] += 1

        max_val = max(sum(v.values()) for v in hourly.values())

        x0 = 60
        y0 = 630
        bar_w = 40
        spacing = 10

        canvas.create_text(700, 40, text="Vehicle Histogram", font=("Arial", 18, "bold"))

        for i, (h, val) in enumerate(sorted(hourly.items())):
            x = x0 + i * (bar_w + spacing)
            elm_h = (val["Elm Avenue/Rabbit Road"] / max_val) * 500
            han_h = (val["Hanley Highway/Westway"] / max_val) * 500

            canvas.create_rectangle(x, y0 - elm_h, x + bar_w / 2, y0, fill="blue")
            canvas.create_rectangle(x + bar_w / 2, y0 - han_h, x + bar_w, y0, fill="red")
            canvas.create_text(x + bar_w / 2, y0 + 15, text=h, font=("Arial", 8))


# ======================================================
#                PART C – MAIN TKINTER GUI
# ======================================================

class TrafficGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Traffic Analysis System")
        self.root.geometry("820x650")
        self.root.resizable(False, False)

        self.selected_data = None
        self.csv_path = None

        self.build_gui()
        self.root.mainloop()

    # ------------------- GUI BUILD ---------------------
    def build_gui(self):

        title = tk.Label(self.root, text="Traffic Analysis System",
                         font=("Arial", 22, "bold"))
        title.pack(pady=10)

        # ----- Date selection -----
        date_frame = tk.Frame(self.root)
        date_frame.pack()

        tk.Label(date_frame, text="Day:").grid(row=0, column=0)
        tk.Label(date_frame, text="Month:").grid(row=0, column=2)
        tk.Label(date_frame, text="Year:").grid(row=0, column=4)

        self.day = ttk.Combobox(date_frame, values=[f"{i:02d}" for i in range(1, 32)], width=4)
        self.month = ttk.Combobox(date_frame, values=[f"{i:02d}" for i in range(1, 13)], width=4)
        self.year = ttk.Combobox(date_frame, values=[str(i) for i in range(2000, 2025)], width=6)

        self.day.grid(row=0, column=1, padx=5)
        self.month.grid(row=0, column=3, padx=5)
        self.year.grid(row=0, column=5, padx=5)

        # ----- Choose file button -----
        btn_file = tk.Button(self.root, text="Choose CSV File",
                             command=self.select_file, width=20, bg="#dddddd")
        btn_file.pack(pady=10)

        # ----- Output box -----
        tk.Label(self.root, text="Output", font=("Arial", 14, "bold")).pack()

        frame = tk.Frame(self.root)
        frame.pack()

        self.output = tk.Text(frame, width=90, height=20, wrap="word")
        self.output.pack(side="left")

        scrollbar = tk.Scrollbar(frame, command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.config(yscrollcommand=scrollbar.set)

        # ----- Buttons -----
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        tk.Button(bottom_frame, text="Show Histogram",
                  command=self.show_histogram, width=18, bg="#b5e3ff").grid(row=0, column=0, padx=10)

        tk.Button(bottom_frame, text="Exit",
                  command=self.root.quit, width=12, bg="#ff4d4d").grid(row=0, column=1, padx=10)

    # ------------------- BUTTON FUNCTIONS ---------------------

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        self.csv_path = path
        try:
            data = process_csv_data(path)
            self.selected_data = data

            result = generate_statistics(data, path.split("/")[-1])
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, result)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV file:\n{e}")

    def show_histogram(self):
        if not self.selected_data:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return
        date = f"{self.day.get()}/{self.month.get()}/{self.year.get()}"
        HistogramApp(self.selected_data, date).run()


# ======================================================
#                RUN APPLICATION
# =======================================================
if __name__ == "__main__":
    TrafficGUI()

