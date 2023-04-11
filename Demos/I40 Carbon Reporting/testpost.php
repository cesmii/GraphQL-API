<?php
//Try to prepare the logs
$logpath = null;
try {
	clearstatcache();
	$logpath = "logs";
        if (!file_exists($logpath)) {
                mkdir($logpath, 0774, true);
        }
        $logpath = getcwd() . "/" . $logpath . "/postdata.log";
        if (!file_exists($logpath)) {
                $logfile=fopen($logpath, "x");
                fwrite($logfile, "Here comes some data...".PHP_EOL);
                fclose($logfile);
        }
} catch (exception $e) {
	//Fail with web server log and move on
	unset($logpath);
        $error_msg = "Non-fatal error: " . $_SERVER [‘SCRIPT_NAME’] . " was unable to create a log file. Check directory permissions for web server user.";
	error_log($error_msg, 0);
        echo ($error_msg);
}

if (isset($logpath)) {
	$rawdata = "POST DATA:" . file_get_contents("php://input");
	file_put_contents($logpath, $rawdata.PHP_EOL, FILE_APPEND);
        print_r($rawdata);
}
?>
