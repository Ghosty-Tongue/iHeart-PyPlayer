# iHeart WebPlayer

## Overview
iHeart WebPlayer is a web application designed for streaming and managing iHeartRadio stations. It features a user-friendly interface for exploring and listening to over 3,700 iHeartRadio stations.

## Features
- Browse and select iHeartRadio stations by bands (FM, AM, Digital).
- Search for stations by frequency within FM and AM bands.
- Stream and control playback of station broadcasts.
- Navigate between stations and view their logos, names, and descriptions.
- Manage your favorite stations and toggle between light and dark modes.

## Requirements
- Web browser (latest versions of Chrome, Firefox, Safari, or Edge)
- PHP 7.4 or higher

## Installation

### Using a Web Hosting File Manager

1. **Choose a Web Host**: For a free web hosting service, you can use platforms such as [InfinityFree](https://www.infinityfree.net/), [000WebHost](https://www.000webhost.com/), or [AwardSpace](https://www.awardspace.com/).

2. **Sign Up and Set Up**:
   - Register for a free account with your chosen web host.
   - Follow the host’s instructions to set up a new website or project.

3. **Upload Files**:
   - Access the file manager provided by your web hosting service.
   - Upload the following files to the root directory of your website:
     - `index.php` (this should be the main API file located outside the Home folder)
     - `Home/index.php` (the main application file)
     - `Home/error.php` (error handling file)
     - `Home/config.php` (configuration file)
     - `Home/styles.css` (stylesheet)

4. **Configure API Details**:
   - Open `Home/config.php` using the file manager’s editor or a text editor.
   - Enter the required API details, including the URL for the iHeartRadio API, which will be served by `index.php` outside the Home folder.

5. **Check Permissions**:
   - Ensure that the files have the correct permissions set (usually 644 for files and 755 for directories).

6. **Access Your Web Application**:
   - Once uploaded and configured, you can access your web application via the URL provided by your hosting service.

## Usage
1. Open your web browser and navigate to the URL of your iHeart WebPlayer.
2. Use the navigation buttons to browse and select stations.
3. Use the search feature to find specific stations by frequency.
4. Enjoy streaming your favorite iHeartRadio stations!

## Contributing
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
