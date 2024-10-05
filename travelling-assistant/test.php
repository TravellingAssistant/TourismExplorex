<?php
$servername = "localhost";
$username = "root";
$password = "root";
$dbname = "minip";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$city = "Adoni"; // Replace with a valid city from your database
$sql = "SELECT name_of_place as name, image FROM places WHERE place = '$city'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "Name: " . $row["name"]. " - Image: " . $row["image"]. "<br>";
    }
} else {
    echo "0 results";
}

$conn->close();
?>
