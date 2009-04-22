<?php
/*
	Plugin Name: Google Reader Shared
	Plugin URI: http://mike.crute.org/
	Description: A sidebar add-in for Google Reader shared items.
	Version: 1.0
	Author: Mike Crute
	Author URI: http://mike.crute.org/
*/

// Format the plugin page
if (is_plugin_page()) { 
	if (isset($_POST['update_reader'])) {
		update_option('GoogleReader_FeedURL', $_POST['url']);
		update_option('GoogleReader_NumDisplay', $_POST['numdisp']);
		update_option('GoogleReader_CSSClass', $_POST['cssclass']);
		echo('<div class="updated"><p>Options changes saved.</p></div>');
}
?>
	<div class="wrap">
		<h2>Google Reader Shared Items Options</h2>
		
		<form method="post">		
			<fieldset class="options">
				<p><strong>Google Reader</strong></p>
				
				<label for="url">Feed URL:</label>
        		<input name="url" type="text" id="url" value="<?php echo get_option('GoogleReader_FeedURL'); ?>" />
        		
				<label for="numdisp">Number to Display (max is 20):</label>
		        <input name="numdisp" type="text" id="numdisp" value="<?php echo get_option('GoogleReader_NumDisplay'); ?>" />
		        
		        <label for="cssclass">CSS Class:</label>
		        <input name="cssclass" type="text" id="cssclass" value="<?php echo get_option('GoogleReader_CSSClass'); ?>" />
        	</fieldset>

		  	<p><div class="submit"><input type="submit" name="update_reader" value="Save Settings" style="font-weight:bold;" /></div></p>
        </form>       
    </div>
<?php
}

else {
	function readerShared() {
		$feedurl = trim(get_option('GoogleReader_FeedURL'));
		$display = trim(get_option('GoogleReader_NumDisplay'));
		$class = trim(get_option('GoogleReader_CSSClass'));
	
		printf('<ul%s>', ($class != '') ? " class=\"$class\"" : '');
		$feed = simplexml_load_file($feedurl);
		$loopcount = 0;
		
		foreach ($feed->entry as $item) {
			if ($loopcount < $display) {
				printf('<li><a href="%s" rel="nofollow">%s - %s</a></li>',$item->link[1]['href'],$item->title,$item->source->title);
				$loopcount++;
			}
		}
		echo('</ul>');
	}
}	
	
function readerShared_Menu() {
	add_options_page('Google Reader Shared Options', 'Google Reader', 9, basename(__FILE__));
}

add_action('admin_menu', 'readerShared_Menu');
?>