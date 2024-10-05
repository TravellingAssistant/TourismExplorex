<?php
$servername = "localhost";
$username = "root";
$password = "password";
$dbname = "minip";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get city from query parameter
$city = isset($_GET['city']) ? $conn->real_escape_string($_GET['city']) : '';

if ($city) {
    // Prepare and execute SQL statement
    $stmt = $conn->prepare("SELECT hotel_name, rating, address, image_link FROM hotel WHERE place = ?");
    $stmt->bind_param("s", $city);
    $stmt->execute();
    $result = $stmt->get_result();

    $hotels = array();

    // Fetch results
    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $hotels[] = array(
                'name' => $row['hotel_name'],
                'rating' => $row['rating'],
                'address' => $row['address'],
                'image' => $row['image_link']
            );
        }
    }

    // Close connections
    $stmt->close();
    $conn->close();

    // Set content type and output JSON
    header('Content-Type: application/json');
    echo json_encode($hotels);
} else {
    // No city provided
    header('Content-Type: application/json');
    echo json_encode([]);
}
?>
