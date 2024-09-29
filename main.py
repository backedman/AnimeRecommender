
import pandas as pd
from Algorithms.recommendations import recommendations
from AniListAPI.AniListCalls import AniListCalls
from config import Config
import json
import os
from AniListAPI.animeList import animeList

def main():
    global ignore_list, ignore_list_file

    
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

        # Initialize the ignore list
    ignore_list_file = 'ignore_list.json'
    if os.path.exists(ignore_list_file):
        with open(ignore_list_file, 'r') as f:
            ignore_list = json.load(f)
    else:
        ignore_list = []



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
    titleList,rec_input,rec_info = get_recommendations(username=username)

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

        #user is also given option to get new recommendations (r [options], with r just printing recommendations_help)
        elif (ans == "R" or ans == "r"):
            
            titleList,rec_input,rec_info = get_recommendations(username=username)

        elif (ans == 'X' or ans == 'x'):
            break
        
        #user is also given options to update their list (U)
        elif (ans == 'u' or ans == 'U'):
            titleList,rec_input,rec_info = get_recommendations(username=username, rec_input=rec_input)

        elif (ans == "o" or ans == "O"):
            print("I. View Ignore List")
            ans = input()

            if ans.lower() == 'i':
                manage_ignore_list(ignore_list, ignore_list_file)





        #if user selects an anime, they get detailed information about the anime, including
        elif (int(ans) < 10 and int(ans) > 0):
            addSpacing()
            
            listIndex = int(ans) - 1 + (page - 1) * 9
            animeName = list(titleList[listIndex].keys())[0]
           
            # the tags, the genres, and description about the anime
            detailed_info = AniListCalls.getAnimeDetailed(animeName, description=True)




            #they also get an option to remove it from the recommendation list
            delete = anime_desciption_help(detailed_info, rec_info)

            if delete:
                # Re-fetch recommendations to update the list
                del titleList[listIndex]
                ignore_list.append(animeName)
                with open(ignore_list_file, 'w') as f:
                    json.dump(ignore_list, f)
                print(f"'{animeName}' has been added to the ignore list and will not appear in future recommendations.")






    pass


def manage_ignore_list(ignore_list, ignore_list_file):
    if len(ignore_list) == 0:
        print("No anime in the ignore list.")
        input()
        return

    print("\nIgnored Anime List:")
    for i, anime in enumerate(ignore_list, start=1):
        print(f"{i}. {anime}")

    # Option to remove a specific anime from the ignore list
    try:
        while True:
            choice = input("Enter the number of the anime to remove from the ignore list (or press x to cancel): ")
            
            if(choice.lower == 'x'):
                break
            
            choice = int(choice)
            
            if 1 <= choice <= len(ignore_list):
                removed_anime = ignore_list.pop(choice - 1)
                # Save the updated ignore list
                with open(ignore_list_file, 'w') as f:
                    json.dump(ignore_list, f)
                print(f"'{removed_anime}' has been removed from the ignore list.")
            else:
                print("Invalid selection.")
    except ValueError:
        print("Canceling... No changes made.")


def get_recommendations(help_only=False, username=None, rec_input=None):
    global ignore_list

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

        if(ans.lower().strip() == 'x'):
            titleList = []
            break
        else:
            result = recommendations.process_input(ans, current_user=username)
            #print(result)
            
            if result is not None:
                # Filter out ignored anime
                result = result[~result['animeName'].isin(ignore_list)]



                titleList = []

                for index, anime in result.iterrows():
                    titleList.append({f"{anime['animeName']}" : anime})

                #titleScoreList = [f"{anime['animeName']} - {anime['similarity_score']}" for anime in result]
                #print(titleScoreList[0])
                return titleList,ans,result

def anime_desciption_help(detailed_info, rec_info):

    # Ensure rec_info is a pandas DataFrame
    if not isinstance(rec_info, pd.DataFrame):
        rec_info = pd.DataFrame(rec_info)

    # Delete
    delete = False

    # Extract the necessary data from detailed_info
    anime_id = detailed_info.get("id", "N/A")
    mal_id = detailed_info.get("idMal", "N/A")
    title_user_preferred = detailed_info.get("title", {}).get("userPreferred", "N/A")
    tags = detailed_info.get("tags", [])
    season_year = detailed_info.get("seasonYear", "N/A")
    season = detailed_info.get("season", "N/A")
    popularity = detailed_info.get("popularity", "N/A")
    duration = detailed_info.get("duration", "N/A")
    format_ = detailed_info.get("format", "N/A")
    status = detailed_info.get("status", "N/A")
    description = detailed_info.get("description", "N/A")
    episodes = detailed_info.get("episodes", "N/A")
    genres = detailed_info.get("genres", [])
    average_score = detailed_info.get("averageScore", "N/A")
    favourites = detailed_info.get("favourites", "N/A")
    country_of_origin = detailed_info.get("countryOfOrigin", "N/A")
    start_date = detailed_info.get("startDate", {})
    end_date = detailed_info.get("endDate", {})
    studios = detailed_info.get("studios", {}).get("edges", [])
    relations = detailed_info.get("relations", {}).get("edges", [])
    recommendations = detailed_info.get("recommendations", {}).get("edges", [])

    # Create the AniList and MAL links
    anilist_link = f"https://anilist.co/anime/{anime_id}"
    mal_link = f"https://myanimelist.net/anime/{mal_id}"

    # Format dates
    def format_date(date_dict):
        year = date_dict.get("year", "N/A")
        month = date_dict.get("month", "N/A")
        day = date_dict.get("day", "N/A")
        if year == "N/A":
            return "N/A"
        else:
            return f"{year}-{month:02d}-{day:02d}"

    start_date_formatted = format_date(start_date)
    end_date_formatted = format_date(end_date)

    # Studios
    studio_names = [edge.get("node", {}).get("name", "N/A") for edge in studios]

    # Get similarity score for the main anime
    similarity_score_main = rec_info.loc[rec_info['animeName'] == title_user_preferred, 'similarity_score']
    if not similarity_score_main.empty:
        similarity_score_main = round(similarity_score_main.iloc[0], 2)
    else:
        similarity_score_main = "N/A (possibly watched?)"

    # Main formatted string
    result = f"Title: {title_user_preferred} | Recommendation Score: {similarity_score_main}\n"
    result += f"ID: {anime_id} | MAL ID: {mal_id}\n"
    result += f"Format: {format_} | Episodes: {episodes} | Duration: {duration} min per ep | Estimated Total Time: {episodes*duration} minutes\n"
    result += f"Status: {status} | Start Date: {start_date_formatted} | End Date: {end_date_formatted}\n"
    result += f"Season: {season} {season_year} | Country of Origin: {country_of_origin}\n\n"
    result += f"Studios: {', '.join(studio_names)}\n"
    result += f"Genres: {', '.join(genres)}\n"
    result += f"Average Score: {average_score}/100 | Popularity: {popularity} | Favourites: {favourites}\n"
    result += f"Description: {description}\n\n"

    result += f"AniList Link: {anilist_link}\n"
    result += f"MyAnimeList Link: {mal_link}\n\n"

    # Sections for submenus
    additional_options = "\n"
    additional_options += "T. Tags\n"
    additional_options += "R. relations\n"
    additional_options += "C. Recommendations\n"
    additional_options += "D. Delete\n"
    additional_options += "X. Exit\n"
    additional_options += "Enter the letter corresponding to the section you want to view in detail (or press Enter to skip): "

    print(result + additional_options)

    # Handle user input for submenus
    user_input = input().strip().lower()
    while user_input in ['t', 'r', 'c', 'd']:
        if user_input == 't':
            # Separate tags by categories
            categories = {}
            for tag in tags:
                category = tag.get("category", "Uncategorized")
                tag_name = tag.get("name", "N/A")
                tag_rank = tag.get("rank", "N/A")
                is_general_spoiler = tag.get("isGeneralSpoiler", False)
                is_media_spoiler = tag.get("isMediaSpoiler", False)
                spoiler = ""
                if is_general_spoiler:
                    spoiler = " (General Spoiler)"
                elif is_media_spoiler:
                    spoiler = " (Media Spoiler)"
                tag_info = f"{tag_name} [Rank: {tag_rank}]{spoiler}"
                categories.setdefault(category, []).append(tag_info)

            # Display tags separated by categories
            tags_result = "\nTags by Categories:\n"
            for category, tag_list in categories.items():
                tags_result += f"  {category}:\n"
                for tag_info in tag_list:
                    tags_result += f"    - {tag_info}\n"
            print(tags_result)
        elif user_input == 'r':
            # Sort relations by similarity score
            sorted_relations = []
            for edge in relations:
                relation_type = edge.get("relationType", "N/A")
                node_title = edge.get("node", {}).get("title", {}).get("userPreferred", "N/A")

                # Get similarity score from rec_info
                sim_score = rec_info.loc[rec_info['animeName'] == node_title, 'similarity_score']
                if not sim_score.empty:
                    sim_score = round(sim_score.iloc[0], 2)
                else:
                    sim_score = 0  # Set a low score for those without a similarity score

                sorted_relations.append((relation_type, node_title, sim_score))

            # Sort by similarity score in descending order
            sorted_relations = sorted(sorted_relations, key=lambda x: x[2], reverse=True)

            # Display sorted relations
            relations_result = "\nRelations by Recommendation Score:\n"
            for relation_type, node_title, sim_score in sorted_relations:
                sim_score_str = sim_score if not 0 else "N/A (possibly watched?)"
                relations_result += f"  - {relation_type}: {node_title} | Recommendation Score: {sim_score_str}\n"
            print(relations_result)

        elif user_input == 'c':
            # Sort recommendations by similarity score
            sorted_recommendations = []
            for edge in recommendations:
                rating = edge.get("node", {}).get("rating", "N/A")
                media_title = edge.get("node", {}).get("mediaRecommendation", {}).get("title", {}).get("userPreferred", "N/A")

                # Get similarity score from rec_info
                sim_score = rec_info.loc[rec_info['animeName'] == media_title, 'similarity_score']
                if not sim_score.empty:
                    sim_score = round(sim_score.iloc[0], 2)
                else:
                    sim_score = 0  # Set a low score for those without a similarity score

                sorted_recommendations.append((media_title, rating, sim_score))

            # Sort by similarity score in descending order
            sorted_recommendations = sorted(sorted_recommendations, key=lambda x: x[2], reverse=True)

            # Display sorted recommendations
            recommendations_result = "\nRecommendations by Recommendation Score:\n"
            for media_title, rating, sim_score in sorted_recommendations:
                sim_score_str = sim_score if not 0 else "N/A (possibly watched?)"
                recommendations_result += f"  - {media_title} [Rating: {rating}] | Recommendation Score: {sim_score_str}\n"
            print(recommendations_result)

        elif user_input == 'd':
            delete = not delete
            print(f'recommendation will{"" if delete else " NOT"} be ignored')
        
        # Ask for input again
        print(additional_options)        
        print("Enter another letter for more details or press Enter to exit: ", end="")
        user_input = input().strip().lower()

    return delete

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