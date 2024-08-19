
from Algorithms.recommendations import recommendations
from AniListAPI.AniListCalls import AniListCalls
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


    #ge first set of recommendations
    titleList,rec_input = get_recommendations(username=username)

    # set current page number and maximum page number (each page has 9)
    page = 1

    #print list of recommendations (with page switching options)
    while (True):
        addSpacing()

        maxPage = int((len(titleList) / 9 + 1.5))


        print("Page " + str(page) + "/" + str(maxPage))
        # shows anime in page
        for x in range(1, 10):
            if (x <= len(titleList) - (page - 1) * 9):
                listIndex = x - 1 + (page - 1) * 9
                listAnime = list(titleList[listIndex].keys())[0]
                print(str(x) + "." + str(listAnime) +" - " + str(list(titleList[listIndex].values())[0]['similarity_score']))

        # gets user input
        print("         ")
        print("Q. Previous Page ")
        print("E. Next Page")
        print("A. Choose Page")
        print("             ")
        print("S. Search")
        print("R. Calculate Recommendations")
        print('U. Update list')
        print("O. Options")
        print("X. Exit Program ")
        ans = input()
        print("\n\n\n\n\n\n\n\n\n\n")


        #user is given options to change pages (Q,E)

        # goes back a page if user chooses "Q"
        if (ans == "Q" or ans == "q"):
            page -= 1

        # goes forward a page if user chooses "E"
        elif (ans == "E" or ans == "e"):
            page += 1

        # goes to user specified page
        elif (ans == "A" or ans == "a"):
            page = int(input())

        elif (ans == "S" or ans == "s"):
            animeName = search_anime()

            for anime in titleList:
                if list(anime.keys())[0] == animeName:
                    #TODO: get detailed information about the anime
                    print(list(anime.values())[0])
                    input('Press Enter to Continue...')
                    break
                

        elif (ans == "R" or ans == "r"):
            
            titleList,rec_input = get_recommendations(username=username)

        elif (ans == 'X' or ans == 'x'):
            break

        elif (ans == 'u' or ans == 'U'):
            titleList,rec_input = get_recommendations(username=username, rec_input=rec_input)

        elif (int(ans) < 10 and int(ans) > 0):
            addSpacing()
            
            listIndex = int(ans) - 1 + (page - 1) * 9
            animeName = list(titleList[listIndex].keys())[0]
           
            print(list(titleList[listIndex].values())[0])
            input('Press Enter to Continue...')

    #if user selects an anime, they get detailed information about the anime, including
    # the tags, the genres, and description about the anime
        #they also get an option to remove it from the recommendation list


    #user is also given options to update their list (U)

    #user is also given option to get new recommendations (r [options], with r just printing recommendations_help)



    pass




def get_recommendations(help_only=False, username=None, rec_input=None):

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
        if(rec_input is None):
            ans = input()
        else:
            ans = rec_input

        print(ans)

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
                return titleList,ans
                

def search_anime():
    print("Name of anime to search")
    animeName = input()
    titleList = AniListCalls.getAnimeSearchList(animeName, 5)

    page = 1

    while True:

        try:
    # set current page number and maximum page number (each page has 9)
            addSpacing()

            maxPage = int((len(titleList) / 9 + 1.5))


            print("Page " + str(page) + "/" + str(maxPage))
            # shows anime in page
            for x in range(1, 10):
                if (x <= len(titleList) - (page - 1) * 9):
                    listIndex = x - 1 + (page - 1) * 9
                    listAnime = titleList[listIndex]
                    print(str(x) + "." + str(listAnime))

            ans = input("Type number to get detailed information")

            if(int(ans) <= len(titleList) and int(ans) > 0):
                return titleList[int(ans) - 1]

            
        except:
            print('Invalid Input. Try Again')

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