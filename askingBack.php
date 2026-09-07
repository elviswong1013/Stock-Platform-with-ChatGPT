<?php
header('Content-Type: text/html; charset="utf-8"');
if (isset($_POST['userInput'])) {
    $userInput = $_POST['userInput'];
    $command = escapeshellcmd('.\\.venv\\Scripts\\python .\chatgpt-strategy.py '.$userInput); 
    $result = shell_exec($command);
    echo $result;
}
if (isset($_POST['strategy'])) {
    $strategy = $_POST['strategy'];
    $command = escapeshellcmd('.\\.venv\\Scripts\\python .\chatgpt-Explanation.py '.$strategy); 
    $result = shell_exec($command);
    // 把python結果轉為UTF-8編碼，前後端頁面都要設定為utf-8編碼
    echo iconv(mb_detect_encoding($result, mb_detect_order(), true), "UTF-8", $result);
}
if (isset($_POST['execution'])) {
    $execution = $_POST['execution'];
    $command = escapeshellcmd('.\\.venv\\Scripts\\python .\main.py '.$execution); 
    $result = shell_exec($command);
    echo $result;
}
?>
