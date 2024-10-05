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

$sql = "SELECT name, image FROM places WHERE city = $city";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $city);
$stmt->execute();
$result = $stmt->get_result();

$places = array();

while($row = $result->fetch_assoc()) {
    $places[] = $row;
}

$stmt->close();
$conn->close();

header('Content-Type: application/json');
echo json_encode($places);
?>
