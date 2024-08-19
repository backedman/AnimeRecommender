from ctypes import sizeof
import AniListAPI.animeList
import AniListAPI.AniListCalls
from AniListAPI.animeList import animeList
from AniListAPI.AniListCalls import AniListCalls
from AniListAPI.AniListAccess import *
from Algorithms.valManip import valManip
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr
import numpy as np
import pandas as pd
from tqdm import tqdm
import math



class recommendations():
    """description of class"""

    average = None


    def calculate_similarity(anime2, dataset1, priorites={}):

        # Pre-calculate the values of anime2genretag and anime2_popularity_avg_score_recommendations
        anime2genretag = anime2[[genretag for genretag in anime2.index if genretag not in ['animeName', 'popularity', 'user_score', 'recommendations']]]
        anime2_popularity_avg_score_recommendations = (anime2['popularity'] ** 0.25) * anime2['average_score'] * (anime2['recommendations'])

        # Pre-calculate the values of anime1genretag for each anime in dataset1
        dataset1genretag = dataset1[[genretag for genretag in dataset1.columns if genretag not in ['animeName', 'popularity', 'user_score', 'recommendations']]]

        # Calculate the cosine similarity between the binary-encoded genres and tags using vectorized operations
        genres_tags_similarity = cosine_similarity(dataset1genretag, np.array(anime2genretag).reshape( 1,-1)).flatten()

        # Weight the similarity score by the user's rating for the anime in dataset 1
        similarity_score = np.sum(genres_tags_similarity * dataset1['user_score'])

        similarity_score *= anime2_popularity_avg_score_recommendations/30

        return similarity_score


    def findReccomended_new(user="", priorities = {}):
        #global aniData, genresTags
        

        # Import necessary libraries

        tqdm.pandas()

        aniData = {}
        genresTags = {}

        print("waiting to get user's anime")

        # Create a dataframe using data from the AniList API
        aniData = AniListCalls.retAnimeListDet(user=user)
        
        print('waiting to get a list of all the anime...')

        allAnime = AniListCalls.getAllAnime(remNonPTW=True)


        print('waiting to get a list of genre tags')
        
        genresTags = AniListCalls.getAllGenreTags()

        print('got list of genretags')

        # Extract genres and tags from the data
        genres = genresTags[0]
        tags = genresTags[1]

        # Initialize dictionaries to store watched anime and recommendations
        watchedDict = {}
        rec_scores = {}

        # Process each entry in the aniData list
        for x in aniData:

            # Only consider entries with status 'DROPPED' or 'COMPLETED'
            if(x['status'] == 'DROPPED' or x['status'] == 'COMPLETED'):
                # Process each anime in the entries list
                for anime in x['entries']:
                    # Extract the name of the anime
                    name = anime['media']['title']['userPreferred']

                    # Initialize a dictionary to store data for this anime
                    diction = {}
                    diction['animeName'] = name

                    # Initialize genre and tag data for this anime
                    for genre in genres:
                        diction.setdefault(genre, 0)
                    for tag in tags:
                        diction.setdefault(tag, 0)

                    # Set genre and tag data for this anime based on the data from the API
                    for genre in anime['media']['genres']:
                        if(genre in diction):
                            diction[genre] = 1
                    for tag in anime['media']['tags']:
                        if(tag['name'] in diction):
                            diction[tag['name']] = tag['rank']/100

                    # Set average score and popularity data for this anime based on the data from the API
                    diction['average_score'] = anime['media']['averageScore']
                    diction['popularity'] = math.log(anime['media']['popularity'] + 1, 2)


                    # Set user score data for this anime based on the data from the API
                    try:
                        diction['user_score'] = anime['score']
                    except:
                        print(anime)

                    # Process recommendations for this anime from the API data
                    for recs in anime['media']['recommendations']['edges']:
                        if(recs['node']['mediaRecommendation'] != None):
                            rec_name = recs['node']['mediaRecommendation']['title']['userPreferred']
                            rating = recs['node']['rating']

                            # Update recommendations dictionary with data from this recommendation
                            if(rec_name not in rec_scores):
                                if(rating < 0 or diction['user_score'] < 0.7):
                                    rec_scores.setdefault(rec_name, 0)
                                else:
                                    rec_scores.setdefault(rec_name, valManip.logKeepNeg(rating+1) * (diction['user_score']/10 + 0.3))
                            else:
                                if(rating < 0):
                                    continue
                                else:
                                    if(diction['user_score'] >= 0.7):
                                        rec_scores[rec_name] += valManip.logKeepNeg(rating + 1) * (diction['user_score']/10 + 0.3)

                    # Add this anime's data to the watchedDict dictionary
                    watchedDict[name] = diction

        print(watchedDict.keys())
                    

        # Initialize a dictionary to store data for all anime
        allDict = {}

        # Process each anime in the allAnime list
        for anime in allAnime:
            # Extract the name of the anime
            name = anime['title']['userPreferred']

            #skip if anime was watched or dropped before
            if name in watchedDict:
                continue

            # Initialize a dictionary to store data for this anime
            diction = {}
            diction['animeName'] = name

            # Initialize genre and tag data for this anime
            for genre in genres:
                diction.setdefault(genre, 0)
            for tag in tags:
                diction.setdefault(tag, 0)

            # Set genre and tag data for this anime based on the data from the API
            for genre in anime['genres']:
                if(genre in diction):
                    diction[genre] = 1
            for tag in anime['tags']:
                if(tag['name'] in diction):
                    diction[tag['name']] = tag['rank']/100

            # Set average score and popularity data for this anime based on the data from the API
            diction['average_score'] = anime['averageScore']
            diction['popularity'] = math.log(anime['popularity'] + 1, 2)

            # Add this anime's data to the allDict dictionary
            allDict[name] = diction

        # Create a dataframe of recommendations from the recommendations dictionary
        names = pd.DataFrame(rec_scores.keys(), columns=['animeName'])
        scores = pd.DataFrame(rec_scores.values(), columns=['recommendations'])
        recs = names.join([scores])

        # Normalize recommendation scores using a square root transformation
        recs['recommendations'] = ((recs['recommendations'] - recs['recommendations'].min())/(recs['recommendations'].max() - recs['recommendations'].min())) ** 0.5 + 1

        # Create dataframes from the watchedDict and allDict dictionaries
        training_set = pd.DataFrame(watchedDict.values())
        all_set = pd.DataFrame(allDict.values())

        # Merge recommendation data into the training_set and all_set dataframes
        #print(training_set.head())
        training_set = training_set.merge(recs, how='left', on="animeName").fillna(1)
        all_set = all_set.merge(recs, how='left', on="animeName").fillna(1)

        # Normalize user scores in the training_set dataframe using a square root transformation
        training_set['user_score'] = (training_set['user_score'] - training_set['user_score'].mean())/training_set['user_score'].std()
        training_set['user_score'] = training_set['user_score'].apply(lambda x: valManip.sqrtKeepNeg(x))

        # Calculate the minimum and maximum popularity values across both dataframes
        popularity_min = min(training_set['popularity'].min(), all_set['popularity'].min())
        popularity_max = max(training_set['popularity'].max(), all_set['popularity'].max())

        # Replace average scores of 1 in the all_set dataframe with the mean average score
        all_set['average_score'][all_set['average_score'] == 1] = all_set['average_score'].mean()

        # Normalize average scores in both dataframes by dividing by 100
        training_set['average_score'] = training_set['average_score']/100
        all_set['average_score'] = all_set['average_score']/100

        # Normalize popularity values in both dataframes
        training_set['popularity'] = (training_set['popularity'] - popularity_min) / (popularity_max - popularity_min) + 1
        all_set['popularity'] = (all_set['popularity'] - popularity_min) / (popularity_max - popularity_min) + 1

        # Create copies of the training_set and all_set dataframes
        dataset1 = training_set.copy()
        new_set = all_set.copy()

        # Apply priority weights to tag data in both dataframes based on the priorities dictionary
        for priority_weight in priorities:
            for tag in priorities[priority_weight]:
                if(priority_weight > 1):
                    dataset1.loc[dataset1['user_score'] < 0, tag] = 0
                    dataset1.loc[dataset1['user_score'] >= 0, tag] *= priority_weight
                    new_set[tag] *= priority_weight
                elif(priority_weight < 0):
                    dataset1.loc[dataset1['user_score'] < 0, tag] *= priority_weight *-1
                    dataset1.loc[dataset1['user_score'] >= 0, tag] = 0
                    new_set[tag] *= priority_weight * -1

        # Calculate similarity scores for each anime in the new_set dataframe using the calculate_similarity function
        new_set['similarity_score'] = new_set.progress_apply(lambda x: recommendations.calculate_similarity(x, dataset1, priorites=priorities), axis=1)
        #print(dataset1)

        # Sort the new_set dataframe by similarity score in descending order
        new_set = new_set.sort_values(by="similarity_score", ascending=False)
        print(new_set)

        # Return a list of recommended anime names from the new_set dataframe
        return new_set[['animeName', 'average_score', 'popularity', 'recommendations', 'similarity_score']]


    def process_input(input, current_user=None):

        between_quote=""
        values = []
        Start = False
        for char in input:

            if(char == '"'):
                Start = not Start
                values.append(between_quote)
                between_quote = ""
            elif(Start):
                between_quote += char
            else:
                if(char is not " "):
                    between_quote += char
                else:
                    values.append(between_quote)
                    between_quote = ""

        values.append(between_quote)

        values = list(filter(None, values))



        next = ""
        legacy = False
        
        genres = []
        res_genres = []
        tags = []
        res_tags = []

        genretags = AniListCalls.getAllGenreTags()
        genre_list = genretags[0]
        tag_list = genretags[1]

        if(values[0] == "r"):
            for x in values:
                if(x == "-list"):
                    genre_list = genretags[0]
                    tag_list = genretags[1]

                    print("-----GENRES-------")
                    for genre in genre_list:
                        print(genre)
                    print("------TAGS---------")
                    for tag in tag_list:
                        print(tag)

                    return
                
                elif(x == "-glist"):
                    print("-----GENRES-------")
                    for genre in genre_list:
                        print(genre)

                    return
                
                elif(x == "-tlist"):
                    print("------TAGS---------")
                    for tag in tag_list:
                        print(tag)

                    return

                elif(x == "-g=" or x == "-genre="):
                    next = "genre"

                elif(x == "-t=" or x == "-tag="):
                    next = "tag"
                
                elif(x == "-rg=" or x == "-restrictgenre="):
                    next = "res_genre"
                
                elif(x == "-rt=" or x == "-restricttag="):
                    next = "res_tag"
                elif(x == "-l" or x== "-legacy"):
                    legacy = True

                elif(next == "genre"):
                    genres += (x.split(","))
                    next = ""
                elif(next == "res_genre"):
                    res_genres += (x.split(","))
                    next = ""
                elif(next == "tag"):
                    tags += x.split(",")
                    next = ""
                elif(next == "res_tag"):
                    res_tags += (x.split(","))
                    next = ""
                elif(next == "exp"):
                    next = ""
        else:
            return


        for genre in genres:
            if(not genre in genre_list):
                genres.remove(genre)
                print(genre + " IS NOT A VALID GENRE")

        for tag in tags:
            if(not tag in tag_list):
                tags.remove(tag)
                print(tag + " IS NOT A VALID TAG")

        if(legacy):
            recommendation_list = recommendations.findReccomendedLegacy(priority_genres=genres, priority_tags=tags, restrict_genres=res_genres, restrict_tags=res_tags)
        else:

            priorities = {'100' : [], '-100' : []}
            
            priorities[100] = genres
            priorities[100] += tags
            
            priorities[-100] = res_genres
            priorities[-100] += res_tags

            recommendation_list = recommendations.findReccomended_new(priorities=priorities, user=current_user)
            print(recommendation_list)

        return recommendation_list