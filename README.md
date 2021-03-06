# LoL-Champion-Recommender
# Overview
This program is a champion recommendation system that uses a user's list of ranked games across the NA, EUW, EUNE, and KR servers (using Riot's API) to infer what champions that they will end up playing in the future.

For those who are unfamiliar with what League of Legends is, it is an online multiplayer game created by a company named Riot. It involves players controlling a single unit known as a "champion". The user will interact with this single champion for the entire span of a game, and upon starting another game, may choose to use a different champion. For the most part, people have a few favorite champions to play, along with a "pool" of other champions that they are capable to play as well. The game currently has 126 champions for users to choose from, with new champions coming out every few weeks/months.

One shortcoming of this program is that the user has to have played a substantial amount of ranked games and at least 10 separate champions to get accurate results. While this program was initially intended to help new players or casual players find a new champion to play, it is thus far impossible for this program to work without enough ranked games played, since at this point in time the Riot API only releases ranked game information. On the bright side, I hope it may help seasoned ranked players to liven their experience with new champions or to help other people who find themselves stuck with a small concentrated champion pool (such as myself) expand their champion pool diversity.

# Usage
This script was written using Python version 2.7. Additionally, this script relies on the use of external libraries such as json, urllib2, matplotlib.pyplot, and scipy.stats. Please install these libraries from the command line if necessary.

Then, to run the app, simply type:

python ChampionRecommendation.py <i>username</i> 

If the desired username has as space it in, make sure to surround the username with quotation marks, so that the program will register the username as a single phrase rather than two distinct words.

Optionally, you can add the -n argument as such:

python ChampionRecommendation.py <i>username</i> -n <i>num</i>

This will print out the top <i>num</i> recommendations. For further assistance, use the -h argument to bring up a list of options and instructions.

Lastly, this program uses a local .json storage to store the player matches from master/challenger tier for NA, EUW, EUNE, and KR from running once. To refresh it, you can set the use_local variable to False right at the beginning of main(). However, this takes a very long time due to the rate limiting restrictions of the Riot API.

#Example Output
This section demonstrates the expected output of this program. As an example, I will use my own username "jteo1". After running the command:

python ChampionRecommendation.py jteo1

Username: jteo1

Printing user's proportion of ranked games played for each champion for reference: <br>
orianna: 0.472393 <br>
lucian: 0.153374 <br>
ahri: 0.104294 <br>
leesin: 0.092025 <br>
thresh: 0.073620 <br>
zed: 0.030675 <br>
syndra: 0.018405 <br>
elise: 0.018405 <br>
cassiopeia: 0.006135 <br>
zyra: 0.006135 <br>
swain: 0.006135 <br>
lulu: 0.006135 <br>
morgana: 0.006135 <br>
jinx: 0.006135 <br>

The predicted champions are: <br>
graves with predicted playing proprtion of 0.025693 <br>
riven with predicted playing proprtion of 0.025600 <br>
yasuo with predicted playing proprtion of 0.025528 <br>
vayne with predicted playing proprtion of 0.024985 <br>
leblanc with predicted playing proprtion of 0.023337 <br>

Firstly, my own current ranked champion proportions are shown. Then, the recommended champions with the predicted proportions are displayed.

In addition to this, two plots from the matplotlib library are used to illustrate these two groups of data. To show my own proportion of champion games, I used a pie chart:
![alt tag](https://github.com/jteo1/LoL-Champion-Recommender/blob/master/README%20pictures/example_pie_chart.PNG)

Then, a bar graph of my own champion proportions alongside the recommended champions is displayed to compare the predicted proportions (in red) with my own current proportions (in yellow).

![alt tag](https://github.com/jteo1/LoL-Champion-Recommender/blob/master/README%20pictures/example_bar_graph.PNG)

Evidently, my champion proportions are very strongly skewed towards Orianna, especially since I don't play many ranked games and hence have a relatively small pool of sample data to work with. Even though the proportion seems very low, it is common for a player to have 1-2 champions to play in each of the 5 roles in the game anyway, which makes the predicted proportions seem deceivingly low. 

# Notes about the program/algorithm
This project serves not only to help other players find new champions, but to entertain my interest in learning data science
principles such as machine learning and python. More specifically, I wanted to apply collaborative filtering on league's database of players to see how accurate the predictions would be. In general, the idea behind collaborative filtering is that we can deduce what a user would like based on what a lot of other people similar to that user liked. As an exmaple, if a critic gave a certain trend of movie scores similar to you, then you would likely enjoy another movie that the critic rated highly that you have yet to watch. The first step for this program was to decide on a metric to rate the "score" a user gave to a champion. Naively, we could use games played, but that would create a signifcant rift between two players who have played different amounts of ranked games that may have similar preferences. To avoid this bias, we can use a proportion of games played with a certain champion to the total number of ranked games played. Reasonably, a player's score of a champion will thus be higher for champions that they play more frequently.

The method of collaborative filtering works here by collecting the champion preferences of a user using the aforementioned proportion, and compares this against other players' proportions with the underlying assumption that two players with similar tastes will like similar champions. Thus, if player A and B have the a very similar champion pool, and player B also plays champions that player A doesn't, then one may assume that player A will also like those champions. Firstly, we need to generate a list of ranked matches for each user in our data set, and calculate the proportion of total games they played with each champoin in their pool. Then, we need to determine a "similarity score" between the user and each other player using this information against our own proportions for each champion. For example, we can view the intersection of these two player's champion pool's proportion and plot the proportions of the two as pairs of points, with the two users representing the axes:

<b>Graph illustrating a positive linear correlating between two players</b>
![alt tag](https://github.com/jteo1/LoL-Champion-Recommender/blob/master/README%20pictures/proportion%20regression.PNG)


My own data is on the x-axis, and the other player's data is along the y-axis. Each data point implictly represents a champion. For example, the point on the far right shows one of my favorite champions that I play that this other player plays at a relatively high rate considering the intersection between my champion pool and the other player's. To determine the 
similarity score, we can use the Pearson coefficient (r) for a regression line to rate the similarity. Ideally, we want to find users with positive <i>r</i> values, which indicates that your champion preferences correlate positively and linearly to their preferences. A negative correlation would indicate that your preferences with any player is inverted. Ideally, we would want to know which champions a player dislikes, but this is impossible to deduce solely on the data given by the API and would probably involve much more advanced techniques.

However, programming with this sole approach is too permissive and is likely to produce unreasonable results. For example, if we compare the intersection of two player's champion pools, it might possibly leave out a player's favorite champion and incorrectly assume two players are very similar based on the part of your pool that is related to your lesser played champions. Also as seen in the above graph, the other player does also play my favorite champion, but at a pretty low rate compared to his own champion pool, thereby giving a high similarity score when the comparison was between the other player's lesser played champions. To account for these cases we can create a weighted score based on the similarity score of the user to produce a predicted proportion for each champion. Therefore, for each user/champion, we can produce a weighted score defined by (similarity score * champion proportion score) to get a sum of weighted scores for that champion. This gives players with higher similarity scores a higher contriubtion to the predicted proportion. Lastly, we divide by the total sum of similarity scores to get a prediction for that champion. Note that each user only contributes to champions in his own pool and omits the rest. By aggregating these reuslts for every champion not in the user's pool across all four regions, we can get relatively high accuracy results. Lastly, we can simply sort from highest to lowest to produce the top n recommended champions.

In the case that this script were actually ever used commercially or launched as part of a website, I would likely avoid showing the exact statistic of the proportion estimate. To an uninformed user, they may assume that a proportion score of 0.04 is extremely low and that the script was inaccurate or inconclusive. However, upon closer inspection, this score is actually relatively high; for a typically diverse champion pool, this would indicate the introduction of a new 3rd or 4th favorite champion to a user. Given that it is already unlikely for a user with the sufficient ranked experience for this script to have not established a core group of 2-3 favorite champions, this prediction would then have displayed amazing results. Hence, realistically it would be a better idea to omit the proportion scores, or to at least clearly display a user's own champion pool proportions for reference. In any case, for the purpose of this personal experiment I see it more fit to allow deeper demonstration the inner workings of the program.

# Results
From reviewing the results of various usernames, it appears that the algorithm is relatively accurate but doesn't produce any definitive results. For example, the program does tend to recognize the type of role/lane that the user typically plays, which demonstrates that it does indeed find highly similar players that also prefer the same role/lane. Furthermore, the results also tend to adhere to the current meta since the recommendations are based off the frequently played champions of high elo players. However, it does not always produce accurate results, especially for users with under approximately 50 games or with a small champion pool, since it won't be able to generate enough points to find a strong correlation. Forthermore, it cannot detect dramatic changes in champion roles, such as that of morgana ambiguously being played as either a mid laner or support. In any case, whether or not the program works effectively is up to the discretion of the user to decide whether they are willing to invest in these results and to evaluate it's accuracy. For myself, the program produced legitimate prospective champions that reflect my interest in high skill-cap champions.

Future iterations of this project are still possible, especially if Riot's API changes to include a larger set of available matches and random users. This set of users is only reflective of the champion tendencies of the top 1% of all of league players, which may prevent diversified results. In any case, there is still a lot to find from the current set of data, which may eventually provide insight to the patterns and tendencies of player psychology in the future.
 


