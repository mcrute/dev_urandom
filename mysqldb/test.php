<?php
require_once 'mysqldb.php';

$connect_vars  = array('user' => 'root',
					   'pass' => 'password',
					   'name' => 'sysadmin'
					  );

$a = array('test'  => 'abc',
		   'test1' => 'def',
		   'test2' => 'ghi',
		   'test3' => 'adsf32',
		   'test3' => 'test"',
		   'test4' => '"ing"'
		  );
		

$d = new DB_Connection($connect_vars);
$b = array();

foreach ($d->raw_execute("SELECT * FROM clients") as $i) {
	array_push($b,$i);
}

echo json_encode($b);
?>
