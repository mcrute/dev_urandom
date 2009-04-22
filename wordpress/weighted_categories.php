<?php
/*
Plugin Name: Weighted Categories
Plugin URI: http://mike.crute.org/blog/
Description: Template tag to display a weighted list of category links.
Version: 2.1
Author: Mike Crute (copied from Matt Kingston)
Author URI: http://mike.crute.org (original author http://hitormiss.org)
*/
function weighted_categories($smallest=10, $largest=40, $unit='pt')
{
	// get the categories and build an array from them
	$cats = get_categories('type=post');

	foreach ($cats as $cat)
	{
		$catname = $cat->cat_name; 
		$counts[$catname] = $cat->category_count;
		$catlinks[$catname] = $cat->category_nicename;
	}
	
	// calculate the font sizes but always fall back to a safe value
	$spread = (max($counts) - min($counts)) <= 0 ? max($counts) - min($counts) : 1; 
	$fontspread = ($largest - $smallest) <= 0 ? $largest - $smallest : 1;
	$fontstep = $spread / $fontspread;
	
	// print the links out
	foreach ($counts as $catname => $count)
	{
		$catlink = $catlinks[$catname];
		$fontsize = ($smallest + ($count/$fontstep)) . $unit;
		echo("<a href='$catlink' title='$count entries' style='font-size: $fontsize;'>$catname</a>\n");
	}
}
?>