<?php

include("simple_html_dom.php");

function crawl_site($u) {
  $html = file_get_html("http://www.hd-area.org/?s=search&q=".$u);
  $content = $html->find('div[id=content]');

  $rss_head = "<rss version=\"2.0\"><channel>";
  $rss_title = "<title>HD-Area Suche</title>";
  $rss_desc = "<description>HD-Area-RSS-Feed-Generator</description>";
  $rss_link = "<link>http://www.hd-area.org/?s=search&q=".$u."/</link>";
  $rss_item = "";
  $rss_tail = "</channel></rss>";

  foreach($html->find('div[id=content]') as $element) {
    $urls = $element->find('a');
    foreach($urls as $url) {
      $title = $url->title;
      $link = $url->href;

      if (!empty($title)) {
	$rss_item = $rss_item."<item>";
	$rss_item = $rss_item."<title>".$title."</title>";
	$rss_item = $rss_item."<link>".$link."</link>";
	$rss_item = $rss_item."</item>";
      }
    }
  }

  echo $rss_head;
  echo $rss_title;
  echo $rss_desc;
  echo $rss_link;
  echo $rss_item;
  echo $rss_tail;
  echo "\n";
}

//crawl_site($argv[1]);
crawl_site($_GET['var'])

?>