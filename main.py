
from Algorithms.recommendations import recommendations
from config import Config
import json
from AniListAPI.animeList import animeList

def main():

    
    #loads config
    config_reader = Config()
    config_data = config_reader.get_config()
    
    #asks user for their username
    username = config_data['user_info']['username']
    
    #saves their username if does not exist
    if not username:
        username = input("What is your anilist username? ")
        config_data['user_info']['username'] = username
        config_reader.rewrite_config(config_data)


    #load user watched anime
    #gets the most up to date user's anime list from website
    try:
        aniList = animeList.updateAniListAnimeList(username=username)

        with open(f'{username}.json', 'w+') as json_file:
            json.dump(aniList, json_file, indent = 4, ensure_ascii = True)

    #if fails, use text file
    except Exception as e:
        print("failed to get list...attempting to load from file")
        
        with open(f'{username}.json') as json_file:
            aniList = json.loads(json_file)


    #print recommendations_help
    titleList = get_recommendations()

    #print list of recommendations (with page switching options)

    #if user selects an anime, they get detailed information about the anime, including
    # the tags, the genres, and description about the anime
        #they also get an option to remove it from the recommendation list

    #user is also given options to change pages (Q,E)

    #user is also given options to update their list (U)

    #user is also given option to get new recommendations (r [options], with r just printing recommendations_help)



    pass




def get_recommendations(help_only=False):

    print(
    '''

    About:
        A recommendation algorithm that uses your anilist scores to present 

    Usage:
      r [options]

    General Options:
      -g, -genre="Genre"             Manually prioritize a certain genre when finding recommendations
      -rg, -restrictgenre="Genre"    Manually unprioritizes a certain genre when finding recommendations


      -t, -tag="Tag"                 Manually prioritize a certain tag when finding recommendations
      -rt, -restricttag="Genre"      Manually unprioritizes a certain tag when finding recommendations
      
      -list                          Print out a list of all the available genres and tags
      -glist                         Print out a list of all the available genres
      -tlist                         Print out a list of all the available tags

      -type                           Uses an experimental version of the recommendation algorithm which uses a
                                     Neural Network to recommend anime (will take a few minutes to train the first
                                     time this is run)

    *Note: Multiple genres and tags can be used with one option if seperated by a comma

    Example: r -g="Comedy,Adventure" -rt="Male Protagonist" ---> recommendation algorithm prioritizing Comedy and Adventure 
                                                                 anime and deprioritizing anime with Male Protagonists


    
    '''    
    )

    if(help_only):
        return

    while True:
        ans = input()
        
        if(ans.lower().strip() == 'x'):
            titleList = []
            break
        else:
            result = recommendations.process_input(ans, current_user=username)
            print(result)
            
            if(result is not None):
                titleList = []
                for index, anime in result.iterrows():
                    titleList.append({f"{anime['animeName']}" : anime})

                #titleScoreList = [f"{anime['animeName']} - {anime['similarity_score']}" for anime in result]
                #print(titleScoreList[0])
                break


def addSpacing():
    for x in range(50):
       print("              ")

def recommendations_help():
    print(
    '''

    About:
        A recommendation algorithm that uses your anilist scores to present 

    Usage:
      r [options]

    General Options:
      -g, -genre="Genre"             Manually prioritize a certain genre when finding recommendations
      -rg, -restrictgenre="Genre"    Manually unprioritizes a certain genre when finding recommendations


      -t, -tag="Tag"                 Manually prioritize a certain tag when finding recommendations
      -rt, -restricttag="Genre"      Manually unprioritizes a certain tag when finding recommendations
      
      -list                          Print out a list of all the available genres and tags
      -glist                         Print out a list of all the available genres
      -tlist                         Print out a list of all the available tags

      -type                           Uses an experimental version of the recommendation algorithm which uses a
                                     Neural Network to recommend anime (will take a few minutes to train the first
                                     time this is run)

    *Note: Multiple genres and tags can be used with one option if seperated by a comma

    Example: r -g="Comedy,Adventure" -rt="Male Protagonist" ---> recommendation algorithm prioritizing Comedy and Adventure 
                                                                 anime and deprioritizing anime with Male Protagonists


    
    '''    
    )

main()