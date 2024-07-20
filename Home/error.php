<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - iHeart Radio Stations</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="error-container">
        <h1>Error</h1>
        <?php
        $error = isset($_GET['error']) ? $_GET['error'] : 'unknown';

        switch ($error) {
            case 'config_missing':
                echo "<p>The configuration file is missing. Please contact the administrator.</p>";
                break;
            case 'api_url_missing':
                echo "<p>The API URL is not set. Please check the configuration file.</p>";
                break;
            default:
                echo "<p>An unknown error occurred. Please try again later.</p>";
                break;
        }
        ?>
        <a href="index.php">Go back to the main page</a>
    </div>
</body>
</html>