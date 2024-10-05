<?php
$servername = "localhost";
$username = "root";
$password = "password";
$dbname = "minip";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$city = $_GET['city'];

$sql = "SELECT name_of_place as name, image FROM places WHERE place = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $city);
$stmt->execute();
$result = $stmt->get_result();

$attractions = array();
while($row = $result->fetch_assoc()) {
    $attractions[] = $row;
}

$stmt->close();
$conn->close();

echo json_encode($attractions);
?>
