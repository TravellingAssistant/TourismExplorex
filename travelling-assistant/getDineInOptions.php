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

$sql = "SELECT  name_of_restaurant as name, cuisine as cui , address_of_restaurant as address, image_link as image FROM dinein WHERE place = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $city);
$stmt->execute();
$result = $stmt->get_result();

$dinein_options = array();
while($row = $result->fetch_assoc()) {
    $dinein_options[] = $row;
}

$stmt->close();
$conn->close();

echo json_encode($dinein_options);
?>