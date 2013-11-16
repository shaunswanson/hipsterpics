hipsterpics
===========

In one sentence, this project is a simple search engine (complete with a specialized crawler) that retrieves a ranked
list of images/gifs from galleries on imgur.com based on how well a user's query matches the content of the gallery's 
comments. As a fun twist, the user is encouraged to input an activity they love so that they may see how hipsters
have ruined it.

Results are ranked 35% on a simple frequency analysis based on the words in the query. The other 65%  of the ranking
is due to input from a click-tracking, artificial neural network. Users are encouraged to click one of the ten
ranked results, whichever looks the most "hipster-looking."

Theoretically, with enough ongoing clicks and a strong initial spread of photos, this neural network could 
become the best predictor of evolving trends within the "hipster" community. It would be fund to experiment with
monetization eventually by serving ad content focused on the opposite of observed "hip" trends.

NOTE: Instances of the crawlers included in this project are currently running to fill the database. 
In the meantime, expect many queries to return few or no results. :(
