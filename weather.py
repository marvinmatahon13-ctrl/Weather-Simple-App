import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import requests
import pytz
import json, os
from timezonefinder import TimezoneFinder


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("900x600+300+150")
        self.root.config(bg="#f5f5f5")
        self.root.resizable(False, False)

        self.api_key = "92c5bc6d3aa8ab8d54a59930e325c003"

        self.box_label = None
        self.setup_ui()

        # Load last searched city if available
        last_city = self.load_last_city()
        if last_city:
            self.textfield.delete(0, tk.END)
            self.textfield.insert(0, last_city)
            self.get_weather()
        else:
            self.textfield.delete(0, tk.END)
            self.textfield.insert(0, "Enter city")

    # ---------- File persistence ----------
    def load_last_city(self):
        """Load most recent searched city"""
        if os.path.exists("last_city.json"):
            try:
                with open("last_city.json", "r") as f:
                    data = json.load(f)
                    cities = data.get("recent_cities", [])
                    return cities[0] if cities else ""
            except json.JSONDecodeError:
                return ""
        return ""

    def save_last_city(self, city):
        """Save valid searched city to history"""
        cities = []
        if os.path.exists("last_city.json"):
            try:
                with open("last_city.json", "r") as f:
                    data = json.load(f)
                    cities = data.get("recent_cities", [])
            except json.JSONDecodeError:
                pass

        city = city.capitalize()
        if city in cities:
            cities.remove(city)
        cities.insert(0, city)

        # Keep only last 5 cities
        cities = cities[:5]

        with open("last_city.json", "w") as f:
            json.dump({"recent_cities": cities}, f, indent=4)

    # ---------- UI Setup ----------
    def setup_ui(self):
        # Search bar
        bar_img = Image.new("RGBA", (400, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bar_img)
        draw.rounded_rectangle((0, 0, 400, 50), radius=25, fill="#2f2f2f")
        bar_photo = ImageTk.PhotoImage(bar_img)
        Label(self.root, image=bar_photo, bg="#f5f5f5").place(x=250, y=40)
        self.root.bar_photo = bar_photo

        # Text entry
        self.textfield = Entry(self.root, font=("poppins", 18, "bold"),
                               bg="#2f2f2f", fg="white", bd=0, insertbackground="white")
        self.textfield.place(x=270, y=50, width=300, height=30)
        self.textfield.insert(0, "Enter city")
        self.textfield.bind("<FocusIn>", self._on_focus_in)
        self.textfield.bind("<FocusOut>", self._on_focus_out)

        # Search button/icon
        icon_img = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_img)
        draw.ellipse((2, 2, 14, 14), outline="#b3b3b3", width=2)
        draw.line((13, 13, 20, 20), fill="#b3b3b3", width=2)
        search_icon = ImageTk.PhotoImage(icon_img)
        self.root.search_icon = search_icon
        Button(self.root, image=search_icon, bg="#2f2f2f", activebackground="#2f2f2f",
               border=0, cursor="hand2", command=self.get_weather).place(x=580, y=50)

        # City and time
        self.city_label = Label(self.root, font=("poppins", 18, "bold"), bg="#f5f5f5")
        self.city_label.place(x=100, y=110)
        self.time_label = Label(self.root, font=("poppins", 13), bg="#f5f5f5")
        self.time_label.place(x=100, y=140)

        # Logo
        try:
            logo_img = Image.open("logo.png").convert("RGBA")
            logo_img = logo_img.resize((200, 200))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = Label(self.root, image=logo_photo, bg="#f5f5f5")
            logo_label.place(x=260, y=120)
            self.root.logo_photo = logo_photo
        except Exception:
            pass

        # Temperature & Description
        self.temp_label = Label(self.root, font=("poppins", 50, "bold"), fg="#FF6666", bg="#f5f5f5")
        self.temp_label.place(x=500, y=160)
        self.desc_label = Label(self.root, font=("poppins", 10, "bold"), bg="#f5f5f5")
        self.desc_label.place(x=460, y=235)
        self.suggestion_label = Label(self.root, font=("poppins", 11, "italic"), fg="#333", bg="#f5f5f5")
        self.suggestion_label.place(x=460, y=265)

        # Info box
        self.create_info_box("#00AEEF")

        # Forecast (7-day) with proper alignment
        self.forecast_frame = Frame(self.root, bg="#f5f5f5")
        self.forecast_frame.place(x=60, y=500)

        self.forecast_labels = []

        for i in range(7):
            day_frame = Frame(self.forecast_frame, width=110, height=80, bg="#f5f5f5")
            day_frame.grid(row=0, column=i, padx=8)

            lbl = Label(day_frame, font=("poppins", 10, "bold"),
                        bg="#f5f5f5", justify="center")
            lbl.place(relx=0.5, rely=0.5, anchor="center")

            self.forecast_labels.append(lbl)

    def _on_focus_in(self, event):
        if self.textfield.get() == "Enter city":
            self.textfield.delete(0, tk.END)

    def _on_focus_out(self, event):
        if self.textfield.get().strip() == "":
            self.textfield.insert(0, "Enter city")

    # ---------- Info box ----------
    def create_info_box(self, color):
        if getattr(self, "box_label", None):
            self.box_label.destroy()
            for widget in [self.w, self.h, self.d, self.p]:
                try:
                    widget.destroy()
                except Exception:
                    pass

        box_img = Image.new("RGBA", (800, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(box_img)
        draw.rounded_rectangle((0, 0, 800, 100), radius=25, fill=color)
        box_photo = ImageTk.PhotoImage(box_img)
        self.box_label = Label(self.root, image=box_photo, bg="#f5f5f5")
        self.box_label.image = box_photo
        self.box_label.place(x=50, y=370)

        label_font = ("poppins", 10, "bold")
        value_font = ("poppins", 14, "bold")
        fg = "white"

        Label(self.root, text="WIND", font=label_font, fg=fg, bg=color).place(x=130, y=380)
        self.w = Label(self.root, font=value_font, fg=fg, bg=color)
        self.w.place(x=130, y=410)

        Label(self.root, text="HUMIDITY", font=label_font, fg=fg, bg=color).place(x=310, y=380)
        self.h = Label(self.root, font=value_font, fg=fg, bg=color)
        self.h.place(x=330, y=410)

        Label(self.root, text="DESCRIPTION", font=label_font, fg=fg, bg=color).place(x=470, y=380)
        self.d = Label(self.root, font=value_font, fg=fg, bg=color, width=14, anchor="w")
        self.d.place(x=470, y=410)

        Label(self.root, text="PRESSURE", font=label_font, fg=fg, bg=color).place(x=710, y=380)
        self.p = Label(self.root, font=value_font, fg=fg, bg=color)
        self.p.place(x=725, y=410)

    # ---------- Utility ----------
    def get_color_by_weather(self, desc):
        desc = (desc or "").lower()
        if any(k in desc for k in ["rain", "storm", "snow", "thunder"]):
            return "#FF6B6B"
        elif any(k in desc for k in ["cloud", "mist", "haze", "overcast"]):
            return "#00AEEF"
        else:
            return "#32CD32"

    def get_suggestion(self, temp, desc):
        desc = (desc or "").lower()
        if "rain" in desc:
            return "🌧 Bring an umbrella!"
        if "clear" in desc and temp > 30:
            return "☀ Stay hydrated!"
        if "clear" in desc:
            return "😎 Enjoy the nice weather!"
        if "cloud" in desc:
            return "☁ Might be gloomy, wear something comfy."
        if temp < 20:
            return "🧥 It's cold! Wear a jacket."
        return "😊 The weather looks fine today!"

    def clear_outputs(self):
        self.city_label.config(text="")
        self.time_label.config(text="")
        self.temp_label.config(text="")
        self.desc_label.config(text="")
        self.suggestion_label.config(text="")
        for field in ("w", "h", "d", "p"):
            lbl = getattr(self, field, None)
            if lbl:
                lbl.config(text="")
        for lbl in self.forecast_labels:
            lbl.config(text="")
        self.create_info_box("#00AEEF")

    # ---------- Weather fetching ----------
    def get_weather(self):
        city = self.textfield.get().strip()
        if not city or city == "Enter city":
            self.city_label.config(text="Enter a city name")
            return

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            resp = requests.get(url, timeout=8)
            data = resp.json()

            if data.get("cod") != 200:
                self.clear_outputs()
                self.city_label.config(text="City not found", font=("poppins", 12, "bold"), fg="red")
                return

            # Save city to recent list
            self.save_last_city(city)

            temp = data["main"]["temp"]
            pressure = data["main"]["pressure"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            desc = data["weather"][0]["description"]
            lon, lat = data["coord"]["lon"], data["coord"]["lat"]

            tf = TimezoneFinder()
            tz = tf.timezone_at(lng=lon, lat=lat)
            local_time = datetime.now(pytz.timezone(tz)) if tz else datetime.now()

            self.city_label.config(text=city.capitalize())
            self.time_label.config(text=local_time.strftime("%I:%M %p"))
            self.temp_label.config(text=f"{int(temp)}°")
            self.desc_label.config(text=f"{desc.capitalize()} | Feels like {int(temp)}°")
            self.suggestion_label.config(text=self.get_suggestion(temp, desc))

            color = self.get_color_by_weather(desc)
            self.create_info_box(color)
            self.w.config(text=f"{wind:.2f}")
            self.h.config(text=f"{humidity}")
            self.d.config(text=f"{desc}")
            self.p.config(text=f"{pressure}")

            self.get_forecast(city)

        except Exception as e:
            print("Error fetching:", e)
            self.clear_outputs()
            self.city_label.config(text="Error fetching data")

    def get_forecast(self, city):
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric"
            resp = requests.get(url, timeout=8)
            data = resp.json()

            if data.get("cod") not in ["200", 200]:
                for lbl in self.forecast_labels:
                    lbl.config(text="")
                return

            forecast_data = {}

            # Group entries by date
            for entry in data.get("list", []):
                date_txt = entry["dt_txt"].split(" ")[0]

                # Only future dates
                if date_txt > datetime.now().strftime("%Y-%m-%d"):
                    temp = entry["main"]["temp"]
                    desc = entry["weather"][0]["main"]

                    forecast_data.setdefault(date_txt, {"temps": [], "desc": []})
                    forecast_data[date_txt]["temps"].append(temp)
                    forecast_data[date_txt]["desc"].append(desc)

            # Get next 7 days
            days = list(forecast_data.keys())[:7]

            for i in range(7):
                if i < len(days):
                    day = days[i]
                    temps = forecast_data[day]["temps"]
                    descs = forecast_data[day]["desc"]

                    avg_temp = sum(temps) / len(temps) if temps else 0
                    main_desc = max(set(descs), key=descs.count) if descs else ""

                    day_name = datetime.strptime(day, "%Y-%m-%d").strftime("%a")

                    self.forecast_labels[i].config(
                        text=f"{day_name}\n{int(avg_temp)}°C\n{main_desc}"
                    )
                else:
                    self.forecast_labels[i].config(text="")

        except Exception as e:
            print("Forecast error:", e)
            for lbl in self.forecast_labels:
                lbl.config(text="")


# ---------- Run ----------
if __name__ == "__main__":
    root = Tk()
    app = WeatherApp(root)
    root.mainloop()
