import json
#from main import addSpacing
from AniListAPI.AniListAccess import *
from AniListAPI.AniListCalls import *
from Algorithms.Sort import *
from Algorithms.Search import *
from Algorithms.valManip import *
from datetime import date


animeListPTW = []
animeListCompleted = []
animeListDropped = []
animeListPaused = []
animeListRepeating = []
animeListCurrent = []
animeListAll = []
animeListDet = []
listAll = []
statusTypes = []
genreTags = []

class animeList():



    def updateAniListAnimeList(username="", user_id=None):
        """Gets anime list from API and updates the anime list

        Args:
            username (str): The username of the AniList user.
            user_id (int): The user ID of the AniList user.
        """
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes

        # Get user ID if not provided
        try:
            if not username:
                user_id = user_id or AniListAccess.getUserID()
        except Exception as e:
            print(f"Error retrieving user ID: {e}", file=sys.stderr)
            return

        # Define the GraphQL query based on the provided user ID or username
        if user_id:
            query = '''
            query ($userID: Int)  {
                MediaListCollection(userId: $userID, type: ANIME) {
                    lists {
                        status
                        entries {
                            id
                            media {
                                id
                                title {
                                    userPreferred
                                }
                                mediaListEntry {
                                    status
                                    score
                                }
                            }
                        }
                    }
                }
            }
            '''
            variables = {'userID': user_id}
        elif username:
            query = '''
            query ($userName: String)  {
                MediaListCollection(userName: $userName, type: ANIME) {
                    lists {
                        status
                        entries {
                            id
                            media {
                                id
                                title {
                                    userPreferred
                                }
                                mediaListEntry {
                                    status
                                    score
                                }
                            }
                        }
                    }
                }
            }
            '''
            variables = {'userName': username}
        else:
            print("Error: No username or user ID provided", file=sys.stderr)
            return

        # Request data from the API
        try:
            anime_list_data = AniListAccess.getData(query, variables)['data']
        except Exception as e:
            print(f"Error retrieving anime list data: {e}", file=sys.stderr)
            return

        # Initialize variables
        status_types = []
        anime_list_ptw = {}
        anime_list_completed = {}
        anime_list_dropped = {}
        anime_list_paused = {}
        anime_list_repeating = {}
        anime_list_current = {}

        # Process each list in the user's anime list collection
        for list_info in anime_list_data['MediaListCollection']['lists']:
            status = list_info['status']
            status_types.append(status)

            if status == "PLANNING":
                anime_list_ptw = list_info
            elif status == "COMPLETED":
                anime_list_completed = list_info
            elif status == "DROPPED":
                anime_list_dropped = list_info
            elif status == "PAUSED":
                anime_list_paused = list_info
            elif status == "REPEATING":
                anime_list_repeating = list_info
            elif status == "CURRENT":
                anime_list_current = list_info

        # Update global variables
        animeListPTW = anime_list_ptw
        animeListCompleted = anime_list_completed
        animeListDropped = anime_list_dropped
        animeListPaused = anime_list_paused
        animeListRepeating = anime_list_repeating
        animeListCurrent = anime_list_current
        statusTypes = status_types

        # Sort all lists (assuming Sort.qSort is defined elsewhere)
        # Sort.qSort(animeListPTW)
        # Sort.qSort(animeListCompleted)
        # Sort.qSort(animeListDropped)
        # Sort.qSort(animeListPaused)
        # Sort.qSort(animeListRepeating)
        # Sort.qSort(animeListCurrent)

        # Combine all lists into one big list and sort it
        animeList.setAnimeListAll()  # Assuming this method combines all lists
        try:
            Sort.qSort(animeListAll)
        except Exception as e:
            print(f"Error sorting the combined anime list: {e}", file=sys.stderr)

        return anime_list_data['MediaListCollection']['lists']


    def updateAnimeListDet(sort="MEDIA_ID"):
        '''gets animeLists from API'''
        
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes, animeListDet
        animeListDet = AniListCalls.retAnimeListDet(user="", sort=sort)
        
        return animeListDet


    def updateFullAnime(reaquire=False, animeListType=None, animeName=None, status=None):
        """updates the data/text file containing the information on all the anime. The function can replace all the information in the
           data function by pulling from the API again (if reaquire=True), update whatever anime is on our list (animeListType=(type)) based on given list status, or the status
           of an individual anime (given animeName and new status). Only one of these things can occur, with reaquire taking precedence over updating based on list status
           and updating by list status taking precedence over updating an individual anime


        Args:
            reaquire (bool, optional): whether or not we should pull all information from the api or not. Defaults to False.
            animeListType (string, optional): updates the values of the anime in the text file based on the anime in a specific list (ex. animeListType="COMPLETED" will update all the currently completed anime in the full list to actually be completed)
            animeName (string, optional): name of the anime that is being updated. Defaults to None.
            status (string, optional): the status the anime is being changed to. Defaults to None.
        """

        if(reaquire):
            pass

        elif(animeListType is not None):
            
            List = animeList.getAnimeList(animeListType)['entries']
            animeData = animeList.getAnimeList("FULL")

            if(animeList is None or animeData is None):
                return None

            #print(List)

            progress = 10
            print(str(int(progress)) + "% done", end="\r")
            slices = 80/len(List)

            for anime in List:

                anime = anime['media']

                print(str(int(progress)) + "% done", end="\r")
                progress += slices


                if(animeListType == "ALL"):
                    curr_status = anime['mediaListEntry']['status']
                    #print(curr_status)
                else:
                    curr_status = animeListType

                title = anime['title']['userPreferred']

                for anime2 in animeData:

                    title2 = anime2['title']['userPreferred']
                    

                    if(title.title() == title2.title()):
                        #print(title + " changed to " + curr_status)
                        anime2['mediaListEntry'] = {'status' : curr_status}

                        break

            Path = valManip.getPath() + "data.txt"

            curr = 95
            print(str(int(progress)) + "% done", end="\r")

            with open(Path, "r+") as json_file:
                json.dump(animeData, json_file, indent = 4, ensure_ascii = True)

            curr = 100
            print(str(int(progress)) + "% done", end="\r")

        elif(animeName is not None or status is not None):

            animeData = animeList.getAnimeList("FULL")
            
            for anime in animeData:

                title = anime['title']

                if(title == animeName):
                    anime['mediaListEntry'] = {'status' : status}
                    break

            Path = valManip.getPath() + "data.txt"
            with open(Path, "r+") as json_file:
                json.dump(animeData, json_file, indent = 4, ensure_ascii = True)

        

    def setAnimeListAll():
        '''adds the entries of all the lists to animeListAll'''
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, listAll
        
        listAll = [animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent]


        animeListAll = []
        animeListAll = {
            'status' : 'ALL',
            'entries' : [],
            }


        for x in range(0, len(listAll)): #iterates through the amount of lists (PTW, Completed, Dropped, etc.)
            
            if(len(listAll[x]) == 0): #moves to the next list if list does not exist (user has no anime in that
                                      #list)
                continue
            
            aniListLen = len(listAll[x]['entries'])

            for y in range(0, aniListLen): #iterates through entries in the list, adding them to the all list
                animeEntry = listAll[x]['entries'][y]
                animeListAll['entries'].append(animeEntry)

        pass

    

            
                            
            
            


#
#                                below are all the get methods
#
    
    def getAnimeList(status):
        '''returns anime list with all information based on status'''

        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll

        #sets correct list based on status
        if(status == "PLANNING"):
            return animeListPTW
        elif(status == "COMPLETED"):
            return animeListCompleted
        elif(status == "DROPPED"):
            return animeListDropped
        elif(status == "PAUSED"):
            return animeListPaused
        elif(status == "REPEATING"):
            return animeListRepeating
        elif(status == "CURRENT"):
            return animeListCurrent
        elif(status == "ALL"):
            return animeListAll
        elif(status == "FULL"):
            return AniListCalls.getAllAnime()

        return None

        pass

    def getTitleList(status):
        '''returns a list containing only the names of the anime'''
        
        #gets correct list
        animeListStat = []
        try:
            animeListStat = animeList.getAnimeList(status)['entries']
        except TypeError:
            return []

        #sets variables for loop
        titleList = []
        index = 0


        #adds names of anime to title list
        for x in animeListStat:
            animeTitle = animeListStat[index]['media']["title"]["userPreferred"]
            titleList.append(animeTitle)
            index += 1
        titleList.sort()
        return titleList    
        
    
    
        pass


    def getAnimeListSorted(aniList):
        '''returns an alphabetically sorted anime list'''
        return Sort.qSort(aniList)

        
    def getAnimeListDet(sort=None):
        global animeListDet

        if(animeListDet == [] or sort is not None):
            animeListDet = animeList.updateAnimeListDet(sort=sort)
        return animeListDet



    def getEntryId(animeName = None, anime_id = None):
        '''gets list entry ID (required to change anything related to the anime on the website)'''
        global animeListAll

        if(animeName is not None):
            aniLoc = Search.bSearchAnimeList(animeListAll, animeName=animeName)
        
        elif(anime_id is not None):
            aniLoc = Search.bSearchAnimeList(animeListAll, anime_id=anime_id)

        if(aniLoc == None): #return None if the anime is not in any of the lists
            return None
        else:	
            entryId = aniLoc['id'] #gets the entry ID of the specific anime in the list
            return entryId

    def getMediaId(animeName):

        return AniListCalls.getAnimeSearch(animeName)['id']







