# LoL-Champion-Recommender
# Overview
This program is a champion recommendation system that uses a user's list of ranked games across the NA, EUW, EUNE, and KR servers (using Riot's API) to infer what champions that they will end up playing in the future.

For those who are unfamiliar with what League of Legends is, it is online multiplayer game that involves controlling a single
unit known as a "champion". The user will interact with this single champion for the entire span of a game, and upon 
starting another game, may choose to use a different champion. For the most part, people have a few favorite champions to play, along with a "pool" of other champions that they are willing to play as well.

One shortcoming of this program is that the user has to have played a substantial amout of ranked games and at least 10 champion to get accurate results. While this program was initially intended to help new players or casual players find a new champion to play, it is thus far impossible for this program to work without enough ranked games under their belt, since at this point in time the Riot API only releases ranked game information. On the bright side, I hope it may help seasoned ranked players to liven their experience with new champions and to help other people who find themselves stuck with a small concentrated champion pool (such as myself) to expand their champion pool diversity.

# Usage
To run the app, simply type:

python ChampionRecommendation.py <i>username</i> 

If the desired username has as space it in, make sure to surround the username with quotation marks, so that the program will register the username as a single phrase rather than two distinct words.

Optionally, you can add the -n argument as so:

python ChampionRecommendation.py <i>username</i> -n <i>num</i>

This will print out the top <i>num</i> recommendations. For further assistance, use the -h argument to bring up a list of options and instructions.

Lastly, this program uses a local .json storage to store the player matches from master/challenger tier for NA, EUW, EUNE, and KR from running once. To refresh it, you can set the use_local variable to False right at the beginning of main(). However, this takes a very long time due to the rate limiting restrictions of the Riot API.

# Notes about the program/algorithm
This project serves not only to help other players find new champions, but to entertain my interest in learning data science
principles such as machine learning and python. More specifically, I wanted to apply collaborative filtering on league's database of players to see how accurate the predictions would be. This method works by collecting the champion preferences of a user in the form of proportion of games played for a champion, and compares this against other players with the underlying assumption that two players with similar tastes will like similar champions. Thus, if player A and B have the a very similar champion pool, and player B also plays champions that player A doesn't, then one may assume that player A will also like those champions. Firstly, we need to determine a "similarity score" between the user and each other player. For example, we can view the intersection of these two player's champion pools and plot the proportions of the two as pairs of points, with the two users representing the axes:

![alt tag](https://github.com/jteo1/LoL-Champion-Recommender/blob/master/all%20region%20data/Capture.PNG)

My own data is on the x-axis, and the other player ID is along the y-axis. Each data point implictly represents a champion. For example, the point on the far right shows one of my favorite champions that I play that this other player plays at a relatively high rate considering the intersection between my champion pool and the other player's. To determine the 
similarity score, we can use the pearson coefficient (r) for a regression line to rate the similarity. Ideally, we want to find users with positive <i>r</i> values, which indicates that your champion preferences correlate linearly. A negative correlation would indicate that the other player doesnt play the champions that you like much and vice versa. Ideally, we would want to know which champions a player dislikes, which is impossible to deduce solely on the data given by the API.

However, programming with this sole approach is too permissive and is likely to produce unreasonable. For example, if we compare the intersection of two player's champion pools, it might possibly leave out a player's favorite champion and incorrectly assume two players are very similar. Also as seen in the above graph, the other player does also play my favorite champion, but at a pretty pretty low rate compared to his own champion pool. To account for these cases we can create a weighted score based on the similarity score of the user to produce a predicted proportion for the user. Therefore, for each user/champion, we can produce a weighted score defined by similarity score * their proportion score for that champion. This gives players with higher similarity scores a higher contriubtion to the predicted proportion. Lastly, we divide by the total of the similarity scores to get a prediction for that champion. Note that each user only contributes to champions in his pool own. By aggregating the reuslts of every champion not in the user's pool across all four regions, we can get relatively high accuracy results. For the last step, we can simply sort from highest to lowest to produce the top n recommended champions.

# Results
From reviewing the results of various usernames, it appears the the algorithm is relatively accurate but doesn't produce any definitive results. For example, the program does tend to recognize the type of role/lane that the user typically plays, which demonstrates that it does indeed find highly similar players that also main the same lane. Furthermore, the results also tend to adhere to the current meta since the recommendations are based off the frequently played champions of high elo players. However, does not always produce accurate results, especially for users with under around 50 games and low existing champion diversity. For example, it cannot detect dramatic changes in champion roles, such as that of morgana ambiguously being played as either a mid laner or support. In any case, whether or not the program works effectively is up to the discretion of the user to decide whether they are willing to invest in these results and to evaluate it's accuracy. For myself, I believe that the results are legitimate prospective champions that reflective my interest in high skill-cap champions.

Future iterations of this project are still possible, especially if Riot's API changes to include a larger set of available matches and random users. This set of users is only reflective of the champion tendencies of the top 1% of all of league players, which may prevent diverse results. In any case, there is still a lot to find from the current set of data that may prove to provide insight to the patterns and tendencies of player decisions in the future.



