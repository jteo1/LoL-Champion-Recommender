# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 22:22:34 2015

@author: jteo1
"""

import json
import urllib2
import time
import sys
from scipy.stats import linregress

#Collect the raw player info of master and challenger tier players of a specific region
def getMasterPlayers(region, api_key):
    try:
        data = json.loads(urllib2.urlopen('https://' + region + '.api.pvp.net/api/lol/' + region + '/v2.5/league/master?type=RANKED_SOLO_5x5&api_key=' + api_key).read())
    except urllib2.HTTPError:
        print "HTTP error occured, try again"
        sys.exit()
    return data
def getChallengerPlayers(region, api_key):
    try:
        data = json.loads(urllib2.urlopen('https://' + region + '.api.pvp.net/api/lol/' + region + '/v2.5/league/challenger?type=RANKED_SOLO_5x5&api_key=' + api_key).read())
    except urllib2.HTTPError:
        print "HTTP error occured, try again"
        sys.exit()
    return json.loads(urllib2.urlopen('https://' + region + '.api.pvp.net/api/lol/' + region + '/v2.5/league/challenger?type=RANKED_SOLO_5x5&api_key=' + api_key).read())

#retrieves the entire list of playersIDs from a certain region and returns it in one list
def getPlayerList(region, api_key):
    master_players = getMasterPlayers(region, api_key)
    challenger_players = getChallengerPlayers(region, api_key)
    #retrieve only the playerIDs from the data
    master_list = [player["playerOrTeamId"] for player in master_players["entries"]]
    challenger_list = [player["playerOrTeamId"] for player in challenger_players["entries"]]
    return master_list + challenger_list

def getPlayerMatchList(region, playerID, api_key):
    data = json.loads(urllib2.urlopen('https://' + region + '.api.pvp.net/api/lol/' + region + '/v2.2/matchlist/by-summoner/' + str(playerID) + '?api_key=' + api_key).read())
    if "matches" not in data.keys():
        print "The input usrename has no ranked matches"
        sys.exit()
    return data["matches"]

def getSummonerID(region, username, api_key):
    username_url = username
    if ' ' in username:
        username_url = username.replace(" ", "%20")
    try:
        data = json.loads(urllib2.urlopen('https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/' + username_url + '?api_key=' + api_key).read())
    except urllib2.HTTPError:
        print "Username couldn't be found"
        sys.exit()

    return data

def getPlayerChampionDict(region, player_list):
    print "Getting \"" + region + "\" player champion information"
    players = {}
    player_num = 1
    for playerID in player_list:
        player_matchlist = getPlayerMatchList(region, playerID)
        matchlist_size = len(player_matchlist)
        players.setdefault(playerID, {})
        for match in player_matchlist:
            champion = match["champion"]
            if players[playerID].has_key(champion):
                players[playerID][champion] += 1.0/matchlist_size
            else:
                players[playerID][champion] = 1.0/matchlist_size
        print player_num
        player_num += 1
        time.sleep(1.3)

    dump_file = 'C:/Users/jteo1/.spyder2/all region data/' + region + '_matchlist.json'
    with open(dump_file, 'w') as f:
        print "dumping json to location: " + dump_file
        json.dump(players, f)
    return players

def openFile(region):
    fileIn = open('all region data/' + str(region) + '_matchlist.json', 'r')
    data = json.loads(fileIn.read())
    fileIn.close()
    return data

#rerranges data from riot API to have ID as the key and name as value
def convertChampionIDsToChampions(api_key):
    champions_by_name = json.loads(urllib2.urlopen('https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?api_key=' + api_key).read())["data"]
    champions_by_id = {}
    for name, info in champions_by_name.iteritems():
        champions_by_id[info["id"]] = name
    return champions_by_id

def printRecommendedChampions(recommendations, user_champions, api_key, n = 5):
    static_championID_conversions = convertChampionIDsToChampions(api_key)
    sorted_user_champions = sorted(user_champions.items(), key = lambda x: x[1], reverse = True)
    print "For reference, your current proportion of champions played in ranked collected from the API is: "
    for i in sorted_user_champions:
        print "%s: %f" % (static_championID_conversions[int(i[0])], i[1])

    #couldnt find enough data, so no recommendations were found
    if len(recommendations) == 0:
        print "Sorry, couldn't find enough data to make a recommendation"
        return

    loop_range = n if n < len(recommendations) else len(recommendations)
    print "\nYour predicted champions are:"
    for i in range(loop_range):
        print "%s with predicted playing proprtion of %f" % (static_championID_conversions[int(recommendations[i][0])], recommendations[i][1])



def getRecommendations(user_matches, userID, all_region_data):
    #make similarity dict for each region
    similarity_list = [{} for _ in range(len(all_region_data))]

    #get similarity score for all players
    for i in range(len(all_region_data)):
        for playerID, player_matches in all_region_data[i].iteritems():
            if playerID != str(userID):
                x = []
                y = []
                for champion in user_matches.keys():
                    #  and user_matches[champion] > 0.01 and player_matches[str(champion)] > 0.01
                    if str(champion) in player_matches.keys():
                        x.append(user_matches[champion])
                        y.append(player_matches[str(champion)])
                #filter out insignifcant graphs with few points
                if len(x) > 9 and max(y) > 0.05: #TODO: figure out these parameters
                    similarity_list[i][playerID] = linregress(x, y)[2]

    #user similarity_list to create weighted estimate of a user's future interest in a champion
    #we store the aggregate of all 4 regions under the same totals/sim_sums for higher accuracy
    totals = {}
    similarity_sums = {}
    for i in range(len(all_region_data)):
        for playerID, player_matches in all_region_data[i].iteritems():
            if playerID == str(userID) or playerID not in similarity_list[i].keys():
                continue
            player_similarity = similarity_list[i][playerID]
            if player_similarity < 0:
                continue
            for champion, proportion in player_matches.iteritems():
                #only calculate for champions not in user's own pool
                if int(champion) not in user_matches.keys():
                    totals.setdefault(champion, 0)
                    totals[champion] += player_similarity * player_matches[str(champion)]
                    similarity_sums.setdefault(champion, 0)
                    similarity_sums[champion] += player_similarity

    predicted_proportions = [(champion, total/similarity_sums[champion]) for champion, total in totals.iteritems()]
    predicted_proportions.sort(key = lambda x: x[1], reverse = True) #sort using the the second term in 2-tuple
    return predicted_proportions

def main():
    #switch to false to renew base data (warning: takes a very long time due to rate limiting)
    use_cache = True
    api_key = "ffa6bd78-47f4-4f7d-8531-4f8baf74079b"


    if not use_cache:
        #Get NA challenger and master player IDs
        na_player_list = getPlayerList("na", api_key)
        print "na list created"

        #Get EU challenger and master player IDs
        euw_player_list = getPlayerList("euw", api_key)
        print "eu list created"

        #Get EUNE challenger and master player IDs
        eune_player_list = getPlayerList("eune", api_key)
        print "eune list created"

        #Get KR challenger and master player IDs
        kr_player_list = getPlayerList("kr", api_key)
        print "kr list created"


        #iterate over all IDs and populate their proportion of champions played
        na_players = getPlayerChampionDict("na", na_player_list)
        eune_players = getPlayerChampionDict("eune", eune_player_list)
        euw_players = getPlayerChampionDict("euw", euw_player_list)
        kr_players = getPlayerChampionDict("kr", kr_player_list)
    else:
        na_players = openFile("na")
        eune_players = openFile("eune")
        euw_players = openFile("euw")
        kr_players = openFile("kr")

     #Enter username to find user's in-game ID number
    username = "ramsey80" #TODO: change to argument input
    return_username = username.replace(" ", "")
    print username
    #assume user is on NA server
    userID = getSummonerID("na", username, api_key)[return_username]['id']

    user = getPlayerMatchList("na", userID, api_key)

    user_champions = {}
    matchlist_size = len(user)
    for match in user:
        champion = match["champion"]
        if user_champions.has_key(champion):
            user_champions[champion] += 1.0/matchlist_size
        else:
            user_champions[champion] = 1.0/matchlist_size

    all_region_data = [na_players, euw_players, eune_players, kr_players]
    recommendations = getRecommendations(user_champions, userID, all_region_data)

    printRecommendedChampions(recommendations, user_champions, api_key, 10)







if __name__ == "__main__":
    main()
