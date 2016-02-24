<?php

include("simple_html_dom.php");

function crawl_site($u) {
  $html = file_get_html("http://serienjunkies.org/search/".$u);
  $rss_head = "<rss version=\"2.0\"><channel>";
  $rss_title = "<title>Serienjunkies-Suche</title>";
  $rss_desc = "<description>Serienjunkies-RSS-Feed-Generator</description>";
  $rss_link = "<link>http://serienjunkies.org/search/".$u."/</link>";
  $rss_item = "";
  $rss_tail = "</channel></rss>";

  foreach($html->find('p') as $element) {
    $title = $element->find('strong', 0)->plaintext;
    $urls = $element->find('a');

    // there are more possible download links per file, so we chose one url while we iterate through all of them
    foreach($urls as $url) {
      // filter 'share-online' links
      if (!strpos($url, "/ul_") === false) {
	// filter awkward links also if they are from 'upload'
	if (strpos($title, "Dauer:") === false && !empty($title)) {
	  $rss_item = $rss_item."<item>";
	  $rss_item = $rss_item."<title>".$title."</title>";
	  $rss_item = $rss_item."<link>".$url->href."</link>";
	  $rss_item = $rss_item."</item>";
	  // some lines for debugging purpose
	  /*echo $title."\n";
	  echo $url->href."\n";
	  echo "---------------\n";*/
	}
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
crawl_site($_GET['var']);

?>