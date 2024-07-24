import tkinter as tk
from tkinter import messagebox, Toplevel
import requests
import pickle
import os
import vlc
from PIL import Image, ImageTk
import threading

class IHeartPyPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("iHeart PyPlayer")

        self.data_directory = "data"
        self.filename = os.path.join(self.data_directory, "stations.dat")
        self.current_station_index = 0
        self.player = None
        self.track_info_update_id = None

        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

        if not os.path.exists(self.filename):
            self.fetch_and_save_data()

        self.stations = self.load_stations()

        self.create_widgets()
        self.update_station_display()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="iHeartRadio Stations")
        self.label.pack(pady=10)

        self.band_label = tk.Label(self.root, text="Select Category:")
        self.band_label.pack()

        self.category_var = tk.StringVar(value="FM")
        self.category_slider = tk.Scale(self.root, from_=0, to=2, orient=tk.HORIZONTAL, showvalue=0, command=self.update_category)
        self.category_slider.pack()
        self.category_slider.set(0)

        self.category_display = tk.Label(self.root, text="FM")
        self.category_display.pack(pady=5)

        self.info_frame = tk.Frame(self.root, bd=2, relief=tk.SOLID)
        self.info_frame.pack(pady=10)

        self.logo_label = tk.Label(self.info_frame)
        self.logo_label.pack(pady=5)

        self.station_name_label = tk.Label(self.info_frame, font=("Arial", 14, "bold"))
        self.station_name_label.pack(pady=5)

        self.station_description_label = tk.Label(self.info_frame, wraplength=400, justify=tk.LEFT)
        self.station_description_label.pack(pady=5)

        self.track_info_label = tk.Label(self.info_frame, font=("Arial", 12))
        self.track_info_label.pack(pady=5)

        self.play_stream_button = tk.Button(self.root, text="Play Stream", command=self.play_stream)
        self.play_stream_button.pack(pady=10)

        self.stop_stream_button = tk.Button(self.root, text="Stop Stream", command=self.stop_stream)
        self.stop_stream_button.pack(pady=10)

        self.prev_button = tk.Button(self.root, text="Previous Station", command=self.prev_station)
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(self.root, text="Next Station", command=self.next_station)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        self.developed_label = tk.Label(self.root, text="Developed by Ghosty-Tongue", anchor='se', fg='grey')
        self.developed_label.pack(side=tk.BOTTOM, pady=5, padx=5)

        self.stats_button = tk.Button(self.root, text="Stats", command=self.open_stats_window)
        self.stats_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        self.check_changes_button = tk.Button(self.root, text="Check for Changes", command=self.check_for_changes)
        self.check_changes_button.pack(pady=10)

    def fetch_and_save_data(self):
        try:
            response = requests.get("https://api.iheart.com/api/v2/content/liveStations/?limit=999999999")
            response.raise_for_status()
            stations = response.json().get('hits', [])
            if stations:
                with open(self.filename, 'wb') as file:
                    pickle.dump(stations, file)
                messagebox.showinfo("Success", "Stations data fetched and saved successfully.")
            else:
                messagebox.showwarning("No Data", "No station data found.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

    def load_stations(self):
        try:
            with open(self.filename, 'rb') as file:
                return pickle.load(file)
        except (IOError, pickle.PickleError) as e:
            messagebox.showerror("Error", f"Failed to load stations: {e}")
            return []

    def update_station_display(self):
        filtered_stations = self.filtered_stations()
        if not filtered_stations:
            self.clear_station_info()
            return

        station = filtered_stations[self.current_station_index]

        logo_path = self.cache_logo(station)
        if logo_path:
            img = Image.open(logo_path)
            img = img.resize((100, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.logo_label.config(image=photo)
            self.logo_label.image = photo

        self.station_name_label.config(text=station.get('name', 'Unknown'))
        self.station_description_label.config(text=station.get('description', 'No description available'))

        if station.get('band', '').upper() == 'AM':
            self.track_info_label.config(text='No track info available for AM stations.')
        else:
            self.fetch_and_display_track_info(station)

    def clear_station_info(self):
        self.logo_label.config(image='')
        self.station_name_label.config(text='No station selected')
        self.station_description_label.config(text='No description available')
        self.track_info_label.config(text='Loading track info...')

    def cache_logo(self, station):
        logo_url = station.get('logo')
        if not logo_url:
            return None

        if not os.path.exists(os.path.join(self.data_directory, "images")):
            os.makedirs(os.path.join(self.data_directory, "images"))

        logo_filename = str(station.get('id', 'unknown')) + ".png"
        logo_path = os.path.join(self.data_directory, "images", logo_filename)

        if not os.path.exists(logo_path):
            try:
                response = requests.get(logo_url)
                response.raise_for_status()
                with open(logo_path, 'wb') as file:
                    file.write(response.content)
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to download logo: {e}")

        return logo_path

    def play_stream(self):
        try:
            station = self.filtered_stations()[self.current_station_index]
            stream_url = self.get_stream_url(station)
            if stream_url:
                if self.player:
                    self.player.stop()
                self.player = vlc.MediaPlayer(stream_url)
                self.player.play()
                messagebox.showinfo("Info", "Stream is playing.")
                self.start_periodic_track_info_fetch()
            else:
                messagebox.showwarning("Warning", "Stream URL not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play stream: {e}")

    def stop_stream(self):
        try:
            if self.player:
                self.player.stop()
                self.player = None
                messagebox.showinfo("Info", "Stream has been stopped.")
                self.stop_periodic_track_info_fetch()
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

    def update_category(self, value):
        categories = ["FM", "AM", "Digital"]
        self.category_display.config(text=categories[int(value)])
        self.update_station_display()

    def filtered_stations(self):
        category = self.category_display.cget("text")
        if category == "Digital":
            return [station for station in self.stations if self.is_digital_station(station)]
        elif category == "AM":
            return [station for station in self.stations if 'am' in station.get('band', '').lower()]
        else:
            return [station for station in self.stations if 'fm' in station.get('band', '').lower()]

    def is_digital_station(self, station):
        markets = station.get('markets', [])
        for market in markets:
            if 'type' in market and market['type'] == 'LiveMarketResponse':
                return True
        return False

    def fetch_and_display_track_info(self, station):
        if station.get('band', '').upper() == 'AM':
            self.track_info_label.config(text='No track info available for AM stations.')
            return

        secure_hls_stream_url = station.get('streams', {}).get('secure_hls_stream', '')
        if not secure_hls_stream_url:
            self.track_info_label.config(text='No track info available.')
            return

        def fetch_track_info():
            try:
                response = requests.get(secure_hls_stream_url)
                response.raise_for_status()
                m3u8_url = self.extract_m3u8_url(response.text)
                if not m3u8_url:
                    self.track_info_label.config(text='No track info available.')
                    return

                m3u8_response = requests.get(m3u8_url)
                m3u8_response.raise_for_status()
                track_info = self.extract_track_info(m3u8_response.text)
                self.track_info_label.config(text=f"Now Playing:\n{track_info}")
            except requests.exceptions.RequestException:
                self.track_info_label.config(text='Error fetching track info.')

        threading.Thread(target=fetch_track_info).start()

    def extract_m3u8_url(self, text):
        for line in text.splitlines():
            if line.endswith(".m3u8"):
                return line.strip()
        return None

    def extract_track_info(self, m3u8_text):
        for line in reversed(m3u8_text.splitlines()):
            if line.startswith("#EXTINF"):
                try:
                    info = line.split(',', 1)[1]
                    title = self.extract_value(info, 'title')
                    artist = self.extract_value(info, 'artist')
                    if title == artist:
                        return f"{title}"
                    else:
                        return f"{title}\n{artist}"
                except IndexError:
                    return "Track info not found"
        return "Track info not available"

    def extract_value(self, info, key):
        try:
            return info.split(f'{key}="')[1].split('"')[0]
        except IndexError:
            return "Unknown"

    def start_periodic_track_info_fetch(self):
        if self.track_info_update_id:
            self.root.after_cancel(self.track_info_update_id)
        self.track_info_update_id = self.root.after(2000, self.fetch_and_display_track_info, self.filtered_stations()[self.current_station_index])

    def stop_periodic_track_info_fetch(self):
        if self.track_info_update_id:
            self.root.after_cancel(self.track_info_update_id)
            self.track_info_update_id = None

    def open_stats_window(self):
        stats_window = Toplevel(self.root)
        stats_window.title("Station Statistics")

        total_stations = len(self.stations)
        fm_stations = len([station for station in self.stations if 'fm' in station.get('band', '').lower()])
        am_stations = len([station for station in self.stations if 'am' in station.get('band', '').lower()])
        digital_stations = len([station for station in self.stations if self.is_digital_station(station)])

        stats_text = (f"Total Stations: {total_stations}\n"
                      f"FM Stations: {fm_stations}\n"
                      f"AM Stations: {am_stations}\n"
                      f"Digital Stations: {digital_stations}")

        stats_label = tk.Label(stats_window, text=stats_text, padx=20, pady=20)
        stats_label.pack()

        close_button = tk.Button(stats_window, text="Close", command=stats_window.destroy)
        close_button.pack(pady=10)

    def check_for_changes(self):
        try:
            response = requests.get("https://api.iheart.com/api/v2/content/liveStations/?limit=999999999")
            response.raise_for_status()
            new_stations = response.json().get('hits', [])
            new_filename = os.path.join(self.data_directory, "stations_new.dat")

            if new_stations:
                with open(new_filename, 'wb') as file:
                    pickle.dump(new_stations, file)

                if not os.path.exists(self.filename) or not self.compare_station_files(self.filename, new_filename):
                    os.rename(new_filename, self.filename)
                    self.stations = new_stations
                    self.update_station_display()
                    messagebox.showinfo("Info", "Stations data updated successfully.")
                else:
                    os.remove(new_filename)
                    messagebox.showinfo("Info", "No changes detected.")
            else:
                messagebox.showwarning("No Data", "No station data found.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to check for changes: {e}")

    def compare_station_files(self, file1, file2):
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() == f2.read()

if __name__ == "__main__":
    root = tk.Tk()
    app = IHeartPyPlayer(root)
    root.mainloop()
