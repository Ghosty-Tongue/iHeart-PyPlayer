# iHeart PyPlayer (Deprecated)

**This project is now deprecated** Until I find a fix/workaround

## Overview
iHeart PyPlayer is a Python application built using Tkinter and VLC to stream and display information about iHeartRadio stations.

## Features
- View and select iHeartRadio stations based on bands (FM, AM, Digital).
- Play and stop streaming of station broadcasts.
- Navigate between stations and view their logos, names, and descriptions.
- View station statistics including total count and counts by band type.
- Check for updates to station data and refresh if necessary.

## Requirements
- Python 3.x
- tkinter (for GUI)
- requests (for API requests)
- python-vlc (for media playback)
- Pillow (PIL) (for image handling)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Ghosty-Tongue/iHeart-PyPlayer.git
   ```
2. Navigate to the directory:
   ```bash
   cd iHeart-PyPlayer
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python iHeart.py
   ```

2. Use the band slider to select FM, AM, or Digital.
3. Use the "Play Stream" and "Stop Stream" buttons to control the media playback.
4. Navigate between stations using the "Previous Station" and "Next Station" buttons.
5. Click the "Stats" button to view the total number of stations and their distribution by band type.
6. Use the "Check for Changes" button to update the station data if there are any changes in the API.

## Contributing
Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
