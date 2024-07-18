import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
import requests
import pickle
import os
import vlc
from PIL import Image, ImageTk

class IHeartPyPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("iHeart PyPlayer")

        self.data_directory = "data"
        self.filename = os.path.join(self.data_directory, "stations.dat")
        self.current_station_index = 0

        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

        if not os.path.exists(self.filename):
            self.fetch_and_save_data()

        self.stations = self.load_stations()

        self.label = tk.Label(root, text="iHeartRadio Stations")
        self.label.pack(pady=10)

        self.band_label = tk.Label(root, text="Select Band:")
        self.band_label.pack()

        self.band_var = tk.StringVar(value="FM")
        self.band_slider = tk.Scale(root, from_=0, to=2, orient=tk.HORIZONTAL, showvalue=0, command=self.update_band)
        self.band_slider.pack()
        self.band_slider.set(0)

        self.band_display = tk.Label(root, text="FM")
        self.band_display.pack(pady=5)

        self.freq_search_button = tk.Button(root, text="Search by Frequency", command=self.freq_search)
        self.freq_search_button.pack(pady=10)

        self.info_frame = tk.Frame(root, bd=2, relief=tk.SOLID)
        self.info_frame.pack(pady=10)

        self.logo_label = tk.Label(self.info_frame)
        self.logo_label.pack(pady=5)

        self.station_name_label = tk.Label(self.info_frame, font=("Arial", 14, "bold"))
        self.station_name_label.pack(pady=5)

        self.station_description_label = tk.Label(self.info_frame, wraplength=400, justify=tk.LEFT)
        self.station_description_label.pack(pady=5)

        self.play_stream_button = tk.Button(root, text="Play Stream", command=self.play_stream)
        self.play_stream_button.pack(pady=10)

        self.stop_stream_button = tk.Button(root, text="Stop Stream", command=self.stop_stream)
        self.stop_stream_button.pack(pady=10)

        self.prev_button = tk.Button(root, text="Previous Station", command=self.prev_station)
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(root, text="Next Station", command=self.next_station)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        self.developed_label = tk.Label(self.root, text="Developed by Ghosty-Tongue", anchor='se', fg='grey')
        self.developed_label.pack(side=tk.BOTTOM, pady=5, padx=5, anchor='se')

        self.update_station_display()

    def fetch_and_save_data(self):
        try:
            response = requests.get("https://api.iheart.com/api/v2/content/liveStations/?limit=999999999")
            response.raise_for_status()
            stations = response.json()['hits']
            with open(self.filename, 'wb') as file:
                pickle.dump(stations, file)
            messagebox.showinfo("Success", "Stations data fetched and saved successfully.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

    def load_stations(self):
        with open(self.filename, 'rb') as file:
            return pickle.load(file)

    def update_station_display(self):
        filtered_stations = self.filtered_stations()
        if not filtered_stations:
            self.clear_station_info()
            return

        station = filtered_stations[self.current_station_index]

        # Update logo
        logo_path = self.cache_logo(station)
        if logo_path:
            img = Image.open(logo_path)
            img = img.resize((100, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.logo_label.config(image=photo)
            self.logo_label.image = photo

        # Update station name and description
        self.station_name_label.config(text=station['name'])
        self.station_description_label.config(text=station['description'])

    def clear_station_info(self):
        self.logo_label.config(image='')
        self.station_name_label.config(text='')
        self.station_description_label.config(text='')

    def cache_logo(self, station):
        if not os.path.exists(os.path.join(self.data_directory, "images")):
            os.makedirs(os.path.join(self.data_directory, "images"))

        logo_filename = str(station['id']) + ".png"
        logo_path = os.path.join(self.data_directory, "images", logo_filename)

        if not os.path.exists(logo_path):
            response = requests.get(station['logo'])
            with open(logo_path, 'wb') as file:
                file.write(response.content)

        return logo_path

    def play_stream(self):
        try:
            station = self.filtered_stations()[self.current_station_index]
            stream_url = self.get_stream_url(station)
            if stream_url:
                if hasattr(self, 'player') and self.player is not None:
                    self.player.stop()
                self.player = vlc.MediaPlayer(stream_url)
                self.player.play()
                messagebox.showinfo("Info", "Stream is playing.")
            else:
                messagebox.showwarning("Warning", "Stream URL not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play stream: {e}")

    def stop_stream(self):
        try:
            if hasattr(self, 'player') and self.player is not None:
                self.player.stop()
                messagebox.showinfo("Info", "Stream has been stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop stream: {e}")

    def next_station(self):
        if len(self.filtered_stations()) == 0:
            return
        self.current_station_index = (self.current_station_index + 1) % len(self.filtered_stations())
        self.update_station_display()

    def prev_station(self):
        if len(self.filtered_stations()) == 0:
            return
        self.current_station_index = (self.current_station_index - 1) % len(self.filtered_stations())
        self.update_station_display()

    def get_stream_url(self, station):
        if 'streams' in station:
            stream_urls = [station['streams'].get('shoutcast_stream', ''),
                           station['streams'].get('secure_shoutcast_stream', '')]
            for url in stream_urls:
                if url:
                    return url
        return None

    def update_band(self, value):
        bands = ["FM", "AM", "Digital"]
        self.band_display.config(text=bands[int(value)])
        self.update_station_display()

    def filtered_stations(self):
        band = self.band_display.cget("text")
        if band == "Digital":
            return [station for station in self.stations if 'markets' in station and any('DIGITAL-NAT' in market['name'] for market in station['markets'])]
        else:
            return [station for station in self.stations if station.get('band', '').upper() == band.upper()]

    def freq_search(self):
        band = self.band_display.cget("text")
        if band not in ["AM", "FM"]:
            messagebox.showwarning("Invalid Band", "Frequency search is only available for AM and FM bands.")
            return

        freq = simpledialog.askstring("Frequency Search", f"Enter the frequency for {band} band:")
        if not freq:
            return

        freq_stations = [station for station in self.stations if station.get('freq') == freq and station.get('band', '').upper() == band.upper()]
        if not freq_stations:
            messagebox.showinfo("No Stations", f"No {band} stations found for frequency {freq}.")
            return

        if len(freq_stations) == 1:
            self.show_station_info(freq_stations[0])
        else:
            self.show_station_selection_gui(freq_stations)

    def show_station_info(self, station):
        self.current_station_index = self.stations.index(station)
        self.update_station_display()

    def show_station_selection_gui(self, stations):
        station_selection_window = Toplevel(self.root)
        station_selection_window.title("Select Station")

        label = tk.Label(station_selection_window, text="Multiple stations found. Select one:")
        label.pack(pady=10)

        station_buttons = []
        for station in stations:
            button = tk.Button(station_selection_window, text=station['name'], command=lambda s=station: self.show_station_info_and_close_gui(s, station_selection_window))
            button.pack(pady=5)
            station_buttons.append(button)

    def show_station_info_and_close_gui(self, station, window):
        self.show_station_info(station)
        window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IHeartPyPlayer(root)
    root.mainloop()
