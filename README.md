hipsterpics
===========

In one sentence, this project is a simple search engine (complete with a crawler) that retrieves an image from a gallery
on imgur based on how well a user's query matches the content of the gallery's comments. The user is encouraged to 
input something they "love" so that the user may see how so-called "hipsters" have ruined it.

Results are ranked 35% on a simple frequency analysis based on the words in the query. The other 65%  of the ranking
is due to input from a click-tracking, artificial neural network. Users are encouraged to click one of the ten
ranked results, whichever looks the most "hipster-looking."

Theoretically, with enough ongoing clicks, this neural network could become the best source of information on the 
evolving trends within the "hipster" community. Ads would be sold for scarves and pbr and crap like that to monetize,
with ad content varying over time with the observed trends.

NOTE: Instances of the crawlers included in this project are currently running to fill the database. 
In the meantime, expect many queries to return few or no results. Feel free to run an instance of the crawler to help 
populate the database with images.
