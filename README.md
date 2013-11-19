hipsterpics
===========

In one sentence, this project is a simple search engine (complete with a specialized crawler) that retrieves a ranked
list of images/gifs from galleries on imgur.com based on how "hipster-looking" the pictures are for a given activity
inputted by the user. I wrote it in a week's time to help me secure a machine learning role.

Results are ranked 35% on a simple frequency analysis applied to gallery comments, specifically the frequency of words
in the activity submitted by the user. The other 65%  of the ranking is due to input from a click-tracking, artificial 
neural network. Users are encouraged to click one of the ten ranked results, whichever looks the most "hipster-looking"
to train the network.

With enough ongoing clicks and a constant supply of fresh imgur photos, this neural network could become the best 
predictor of evolving trends within the "hipster" community. It would be fun to experiment with monetization if the 
userbase grows by serving ad content focused on the negative of observed "hip" trends.

--

NOTE: The initial database has 1,200 photos in it. Some queries may return few or no results due to this.
