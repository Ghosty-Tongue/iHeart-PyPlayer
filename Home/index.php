<?php
$config_file = 'config.php';
if (!file_exists($config_file)) {
    header("Location: error.php?error=config_missing");
    exit;
}
include($config_file);

function fetchData($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $output = curl_exec($ch);
    if (curl_errno($ch)) {
        return false;
    }
    curl_close($ch);
    return $output;
}

function getCookieValue($name) {
    return isset($_COOKIE[$name]) ? $_COOKIE[$name] : '';
}

function setCookieValue($name, $value, $days) {
    setcookie($name, $value, time() + (86400 * $days), "/");
}

$response = fetchData($apiUrl);
if ($response === false) {
    header("Location: error.php?error=api_url_missing");
    exit;
}

$data = json_decode($response, true);

if (is_array($data) && !empty($data)) {
    $stations = $data;
} else {
    header("Location: error.php?error=api_url_missing");
    exit;
}

$currentIndex = intval(getCookieValue('lastStation')) ?: 0;
$favorites = json_decode(getCookieValue('favorites'), true) ?: [];
$isDarkMode = getCookieValue('darkMode') === 'true';

setCookieValue('lastStation', $currentIndex, 3650);

$currentTimestamp = time();
setCookieValue('lastStationTimestamp', $currentTimestamp, 3650);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iHeart Radio Stations</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body class="<?php echo $isDarkMode ? 'dark-mode' : ''; ?>">
    <h1>iHeart Radio Stations</h1>
    <button onclick="toggleDarkMode()">Toggle Dark Mode</button>
    <button onclick="toggleFavorites()" class="my-favorites-btn">My Favorites</button>
    <button onclick="toggleSearch()">Search Stations</button>

    <div class="station-container">
        <img id="logo" src="" alt="">
        <h2 id="name"></h2>
        <p id="description"></p>
        <audio id="audio" controls autoplay>
            <source id="shoutcast_stream" src="" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <div class="controls">
            <button onclick="changeStation(-1)">Previous</button>
            <button onclick="changeStation(1)">Next</button>
            <button class="favorite-btn" onclick="toggleFavorite()">☆ Favorite</button>
        </div>
    </div>

    <div id="favoritesPopup" class="favorites-popup">
        <span class="close-btn" onclick="toggleFavorites()">✖</span>
        <h2>Favorites</h2>
        <div id="favoritesContainer" class="favorites-container"></div>
    </div>
    
    <div id="searchPopup" class="search-container">
        <span class="close-btn" onclick="toggleSearch()">✖</span>
        <input type="text" id="searchInput" placeholder="Search...">
        <ul id="searchResults" class="search-results"></ul>
    </div>

    <div id="notificationBanner" class="notification-banner"></div>

    <script>
        const stations = <?php echo json_encode($stations); ?>;
        let currentIndex = <?php echo $currentIndex; ?>;
        let favorites = <?php echo json_encode($favorites); ?>;
        const isDarkMode = <?php echo $isDarkMode ? 'true' : 'false'; ?>;

        function setCookie(name, value, days) {
            document.cookie = `${name}=${value};path=/;max-age=${86400 * days}`;
        }

        function updateStation(index) {
            if (index < 0 || index >= stations.length) return;

            currentIndex = index;
            const station = stations[currentIndex];
            
            document.getElementById('logo').src = station.logo;
            document.getElementById('logo').alt = station.name;
            document.getElementById('name').innerText = station.name;
            document.getElementById('description').innerText = station.description;
            document.getElementById('shoutcast_stream').src = station.streams.shoutcast_stream;

            const audioElement = document.getElementById('audio');
            audioElement.load();
            audioElement.play();

            setCookie('lastStation', currentIndex, 3650);

            updateFavoriteButton();
        }

        function changeStation(direction) {
            const newIndex = currentIndex + direction;
            updateStation(newIndex);
        }

        function toggleFavorite() {
            const isFavorite = favorites.includes(currentIndex);

            if (isFavorite) {
                favorites = favorites.filter(index => index !== currentIndex);
            } else {
                favorites.push(currentIndex);
            }
            setCookie('favorites', JSON.stringify(favorites), 3650);
            updateFavoriteButton();
            showNotification(isFavorite ? "Removed from Favorites" : "Added to Favorites", isFavorite ? "red" : "green");
        }

        function updateFavoriteButton() {
            const starButton = document.querySelector('.favorite-btn');
            if (favorites.includes(currentIndex)) {
                starButton.classList.add('gold');
            } else {
                starButton.classList.remove('gold');
            }
        }

        function showNotification(message, color) {
            const banner = document.getElementById('notificationBanner');
            banner.innerText = message;
            banner.className = `notification-banner ${color}`;
            banner.style.display = 'block';
            setTimeout(() => {
                banner.style.display = 'none';
            }, 3000);
        }

        function toggleFavorites() {
            const popup = document.getElementById('favoritesPopup');
            const favoritesContainer = document.getElementById('favoritesContainer');
            
            if (popup.style.display === 'none' || !popup.style.display) {
                popup.style.display = 'block';
                favoritesContainer.innerHTML = '';

                favorites.forEach(index => {
                    const station = stations[index];
                    const listItem = document.createElement('div');
                    listItem.classList.add('favorite-item');
                    
                    const logo = document.createElement('img');
                    logo.src = station.logo;
                    logo.alt = station.name;
                    logo.classList.add('favorite-logo');
                    logo.onclick = () => updateStation(index);
                    
                    listItem.appendChild(logo);
                    favoritesContainer.appendChild(listItem);
                });
            } else {
                popup.style.display = 'none';
            }
        }

        function toggleDarkMode() {
            const newDarkMode = !isDarkMode;
            document.body.classList.toggle('dark-mode', newDarkMode);
            setCookie('darkMode', newDarkMode, 3650);
        }

        function toggleSearch() {
            const searchPopup = document.getElementById('searchPopup');
            searchPopup.style.display = (searchPopup.style.display === 'none' || !searchPopup.style.display) ? 'block' : 'none';
        }

        function displaySearchResults(results) {
            const searchResults = document.getElementById('searchResults');
            searchResults.innerHTML = '';

            results.forEach((station, index) => {
                const listItem = document.createElement('li');
                listItem.innerText = station.name;
                listItem.onclick = () => updateStation(index);
                searchResults.appendChild(listItem);
            });
        }

        document.getElementById('searchInput').addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const filteredStations = stations.filter(station => station.name.toLowerCase().includes(query));
            displaySearchResults(filteredStations);
        });

        updateStation(currentIndex);
    </script>
</body>
</html>