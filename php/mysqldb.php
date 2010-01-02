<?php
/**
 * MySQL Database Abstraction Layer
 *
 * The goal of this class is to abstract the mundane details of creating and maintaining a MySQL 
 * connection and recordset.
 */
class DB_Connection {
	// SQL Query Types
	const SQL_SELECT = 0;
	const SQL_UPDATE = 1;
	const SQL_INSERT = 2;
	const SQL_DELETE = 3;
	
	// Private Class Variables
	private $connection = null;
	private $connect_vars  = array('host' => 'localhost',
								   'port' => '3306',
								   'sock' => '',
								   'user' => 'root',
								   'pass' => '',
								   'name' => ''
								   );
	
	// Merges the results of the connect variables passed with the defaults
	// values added/changed when the function is called take precedence over
	// the defaults. We also setup our MySQL connection here.
	public function __construct($connect_vars) {
		$this->connect_vars = array_merge($this->connect_vars, $connect_vars);
		
		$this->connection = new mysqli($this->connect_vars['host'], $this->connect_vars['user'],
								 $this->connect_vars['pass'], $this->connect_vars['name']
								);
		
		if(mysqli_connect_error()) 
			throw new DBException(sprintf("DB Connect Failed: %s\n", mysqli_connect_error()));
	}
	
	// Close down the connection when the class goes away
	public function __destruct() {
		$this->connection->close();
	}
	
	// Escape implementation that takes into account magic quotes and quote
	// encapsulation. In the end the majority of the work is done by 
	// mysql_real_escape_string
	public function escape($val, $quote=true) {
		$val = !get_magic_quotes_gpc() ?  $val : stripslashes($val);
		
		if (is_numeric($val)) 
			return $val;
		else
			if ($quote)
				return sprintf("'%s'", $this->connection->real_escape_string($val));
			else
				return $this->connection->real_escape_string($val);
	}
	
	// Generates a SQL query based on an array of data. This is the
	// quickest way to generate long insert and update statements.
	// Mainly because I'm lazy and HATE to maintain large SQL statements
	// in application code.
	public function get_sql_string($type, &$data, $table, $where='') {
		if (/*!defined($type) ||*/ !is_array($data) || !$table)
			throw new DBException('Not enough parameters, or invalid parameters passed.');
	
		$sql = '';
	
		switch ($type) {
			case self::SQL_UPDATE:
				$sql .= "UPDATE $table ";
				$iter = 0;
				
				foreach ($data as $key=>$val) {
					if ($iter++ == 0) 
						$sql .= sprintf("SET $key = %s", $this->escape($val));
					else	
						$sql .= sprintf(", $key = %s", $this->escape($val));
				}
			break;
			
			case self::SQL_INSERT:
				$sql .= "INSERT INTO $table";
				$iter = 0;
				$cols = '(';
				$vals = 'VALUES(';
				
				foreach ($data as $key=>$val) {
					if ($iter++ == 0) {
						$cols .= $key;
						$vals .= $val;
					} else { 
						$cols .= ",$key";
						$vals .= sprintf(",%s",$this->escape($val));
					}
				}
				
				$cols .= ')';
				$vals .= ')';
				
				$sql .= "$cols $vals";
			break;
		}
		
		if (is_string($where)) 
			$sql .= ($where) ? " WHERE $where" : '';
		
		return $sql;
	}
	
	// Same as the get_sql_string function, except that it actually executes
	// the SQL statement and returns a recordset object
	public function execute($type, $data, $table, $where) {
		return $this->raw_execute($this->get_sql_string($type, $data, $table, $where));
	}
	
	// Executes a given query string and returns a recordset object
	public function raw_execute($what) {
		return new Recordset($this->connection->query($what));
	}
}

class Recordset implements Iterator {	
	// SQL Result Fetch Type
	const RS_OBJECT = 0;
	const RS_ARRAY  = 1;
	const RS_ASSOC  = 2;
	
	// Private Class Variables
	private $my_recordset = null;
	private $pointer      = 0;
	private $return_type  = self::RS_OBJECT;
	private $current_row  = null;
	
	// Public Class Variables
	public $row_count     = 0;
	public $column_count  = 0;
	
	// Class constructor takes a mysqli recordset and 
	// loads important data into the class variables
	public function __construct(&$recordset) {
		$this->my_recordset = $recordset;
		$this->row_count    = $recordset->num_rows;
		$this->column_count = $recordset->field_count;
	}
	
	// Closes the recordset when the class dies
	public function __destruct() {
		$this->my_recordset->close();
	}
	
	// Rewind the recordset to the first item and clear the
	// record buffer
	public function rewind() {
		$this->pointer = 0;
		$this->my_recordset->data_seek(0);
		$this->current_row = null;
	}
	
	// Return the current item in the record buffer
	public function current() {
		/* 
			When rewound we won't have a row in the current_row buffer
			this will result in the first iteration of the loop failing
			to prevent this we fetch something into the current_row
			buffer if there isn't anything there. 
		*/
		if (!$this->current_row)
			$this->current_row = $this->get_row();
			
		return $this->current_row;
	}
	
	// Implementing key fetching is pretty pointless in this class
	// because we don't work with any key=>value pairs.
	public function key() {
		throw new RSException('Fetching keys is not implemented');
	}
	
	// Fetch the next row into the buffer
	public function next() {
		/*
			Foreach loops seek past the end of the array and call valid to
			determine they are at the end of the enumerable. If we toss an
			exception every time somebody seeks past the end of the object
			we would have to add extra logic to the calling code. Boo
		
		if ($this->pointer >= $this->row_count)
			return false;
		*/
		
		return $this->get_row(true);
	}
	
	// Go back a step in the recordset
	public function previous() {
		if ($this->pointer == 0)
			throw new RSException('Can not see past beginning of the recordset.');
	
		$this->my_recordset->data_seek($this->pointer - 1);
		return $this->get_row();
	}
	
	// Called by foreach to determine if it has hit the end of the recordset
	public function valid() {
		if ($this->pointer <= $this->row_count)
			return true;
		else
			return false;
	}
	
	// This function actually gets the row data in the format requested.
	// I'm providing this here because you may only have one row in the
	// recordset and there would be no reason to use a foreach loop to
	// extract a single row of data. This function does take care to move
	// the stack pointer so you could, theoretically, you should be able
	// to call this in a loop, similar to the old way we fetched MySQL 
	// records. But why would you want to do that?
	public function get_row($supress=false) {
		$this->pointer++;
		
		if (!$supress) {
			if ($this->pointer > $this->row_count)
				throw new RSException('Can not seek past end of the recordset.');
			elseif ($this->pointer < 0)
				throw new RSException('Can not seek past beginning of the recordset.');
		}
		
		switch ($this->return_type) {
			case self::RS_OBJECT:
				$this->current_row = $this->my_recordset->fetch_object();
			break;
			
			case self::RS_ARRAY:
				$this->current_row = $this->my_recordset->fetch_array();
			break;
			
			case self::RS_ASSOC:
				$this->current_row = $this->my_recordset->fetch_assoc();
			break;
		}
		
		return $this->current_row;
	}
	
	// Sets the return type. Look at the class constants for more information
	// about what can be passed to this function. Note it is optional to call
	// this function, the class will default to returning objects.
	public function return_as($type) {
		//if (defined($type))
			$this->return_type = $type;
		//else 
		//	throw new RSException('Return type not valid');
	}
}

class RSException extends DBException {};
class DBException extends Exception {};
?>