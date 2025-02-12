from AniListAPI.AniListAccess import *
from Algorithms.valManip import *
from datetime import date
from tqdm import tqdm



class AniListCalls():

    def getAnimeDetailed(animeName, description=False):
        '''gets detailed list of anime'''

        #sets query and variables to get anime from API

        if(description):
            query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    id
                    idMal
                    title{
                        userPreferred
                    }
                    tags{
                        category
                        name
                        rank
                        isGeneralSpoiler
                        isMediaSpoiler
                    }
                    seasonYear
                    season
                    popularity
                    duration
                    format
                    status(version: 1)
                    description
                    episodes
                    genres
                    duration
                    averageScore
                    favourites
                    countryOfOrigin
                    startDate {
                      year
                      month
                      day
                    }
                    endDate {
                      year
                      month
                      day
                    }
                    studios{
                        edges{
                            node{
                                name
                            }
                        }
                    }
                    relations{
                        edges{
                            relationType(version: 2)
                            node{
                                title {
                                  userPreferred
                                }
                            }
                        }
                    }
                    recommendations{
                        edges{
                            node{
                                rating
                                mediaRecommendation{
                                    title{
                                        userPreferred
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
        else:
            query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    id
                    title{
                        userPreferred
                    }
                    tags{
                        name
                        rank
                    }
                    episodes
                    genres
                    duration
                    averageScore
                    meanScore
                    favourites
				    recommendations{
					    edges{
						    node{
                                rating
							    mediaRecommendation{
								    title{
									    userPreferred
								    }
							    }
						    }
					    }
				    }
                }
            }
            '''
        variables = {
            'animeName' : animeName
        }



        #returns json data of anime
        animeData = (AniListAccess.getData(query, variables))['data']['Media']

        return animeData

    def retAnimeListDet(user="", sort="MEDIA_ID"):

        if(user == ""):
            userName = AniListAccess.getUserName()
        else:
            userName = user

        if(sort is None):
            sort = "MEDIA_ID"

        #sets query to send to server.  This one asks for total number of
        #pages, total anime, name of the anime in a page, and what list the
        #anime is in
        query = '''
        query ($userName: String, $sortType: [MediaListSort])  {
                MediaListCollection(userName : $userName,  type: ANIME, sort: $sortType) {
                    
                     lists {
                          
                          status

                          entries {
                            score
                            mediaId
                            media {
                              title{
                                userPreferred
                              }

                              genres

                              tags{
                                name
                                rank
                                category
                              }

                              averageScore
                              popularity
                              

                              mediaListEntry {
                                score
                              }

                              recommendations{
                                edges{
                                    node{
                                        rating
                                        mediaRecommendation{
                                            title{
                                                userPreferred
                                            }
                                        }
                                    }
                        }
                    }

                            }

                          }
            }
                }
        }
        '''
        
        #sets correct information for the query.  If all anime in the list are
        #wanted, then status is not set
        variables = {
            'userName' : userName,
            'sortType' : sort
        }

        #requests data from API into a list
        animeListData = AniListAccess.getData(query, variables)['data']['MediaListCollection']['lists']

        return animeListData

    def getAnimeSearch(animeName):
        '''gets first search result of anime search'''
        query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    title{
                        userPreferred
                    }
                    id
                    episodes                  
                    duration

                }
            }
            '''
        variables = {
            'animeName' : animeName
        }
        
            #returns data of anime
        
        animeData = (AniListAccess.getData(query, variables))['data']['Media']
        return animeData

    def getAnimeSearchList(animeName, numResults):
        '''gets multiple search results'''
        
        query = '''
            query ($animeName: String, $perPage: Int)  {
            Page(perPage : $perPage){
  	                media(search : $animeName, type : ANIME)
                    {
                        title{
                            userPreferred
                        }
                        episodes                  
                        duration
                    }
                }
            }
        '''
        variables = {
                'animeName' : animeName,
                'perPage' : numResults
            }

        #returns anime results list
        queryData = (AniListAccess.getData(query,variables))['data']['Page']['media']
        
        animeData = []

        for anime in queryData:
            animeTitle = anime['title']['userPreferred']
            animeData.append(animeTitle)

        return animeData

    def getAllAnime(remNonPTW=False):
        """Gets all the anime that's ever been released.
        
        Args:
            rem_non_ptw (bool): If True, removes non-PTW (Planning to Watch) anime from the data.
        
        Returns:
            list: List of all anime data.
        """
        global animeListAll

        path = valManip.getPath() + "data.txt"  # Creates path to store the list of all anime

        # Check if the data file exists
        if os.path.exists(path):
            with open(path, "r+") as json_file:
                anime_data = json.load(json_file)

            # Remove non-PTW anime if required
            if remNonPTW:
                index = 0
                while index < len(anime_data):
                    anime = anime_data[index]
                    if anime['mediaListEntry'] is not None:
                        status = anime['mediaListEntry']['status']
                        if status in ["COMPLETED", "DROPPED", "CURRENT"]:
                            anime_data.pop(index)
                            index -= 1
                    index += 1

            return anime_data

        # If the file doesn't exist, fetch data from the API
        query = '''
            {
        '''
        variables = {}
        item = 0
        anime_data = []

        # Iterate through each year and fetch data
        for year in tqdm(range(1940, date.today().year + 1), desc="Fetching years"):
            for page in tqdm(range(1, 13), desc=f"Fetching pages for {year}", leave=False):  # 12 pages for each year (600 anime per year)
                query += (''' item%d: Page(page: %d) { 
                                media(type: ANIME, seasonYear: %d){ 
                                    title{ 
                                        userPreferred
                                    }
                                    recommendations{
                                        edges{
                                            node{
                                                rating
                                                mediaRecommendation{
                                                    title{
                                                        userPreferred
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    tags{
                                        name
                                        rank
                                    }
                                    genres
                                    popularity
                                    averageScore
                                    mediaListEntry {
                                        status
                                    }
                                }
                            }
                        ''' % (item, page, year))
                item += 1

            # Fetch data in 2-year increments due to API call limits
            if (date.today().year - year) % 2 == 0:
                query += "}"
                item = 0

                try:
                    query_data = AniListAccess.getData(query, variables)['data']
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data: {e}", file=sys.stderr)
                    return []

                for x in range(len(query_data)):  # Add data from each page to the full database
                    item_string = f'item{x}'
                    page_data = query_data[item_string]['media']
                    if page_data:
                        anime_data += page_data

                query = '''
                    {
                '''

        # Save data to file
        with open(path, "w+") as json_file:
            json.dump(anime_data, json_file, indent=4, ensure_ascii=True)
            json_file.seek(0)

        # Remove non-PTW anime if required
        if remNonPTW:
            index = 0
            while index < len(anime_data):
                anime = anime_data[index]
                if anime['mediaListEntry'] is not None:
                    status = anime['mediaListEntry']['status']
                    if status not in ["PLANNING", "PAUSED", "CURRENT"]:
                        anime_data.pop(index)
                        index -= 1
                index += 1

        return anime_data  # Return data

    def getAllGenreTags():
        '''returns all possible genres and tags available on anilist. Index 0 contains genres and Index 1 contains tags'''
        global genreTags

        query = '''
            {
                GenreCollection
                MediaTagCollection{
                    name
                }
            }
        '''

        variables = {
            }

        #returns anime results list
        animeData = (AniListAccess.getData(query,variables))['data']

        #splits tags and genres into seperate lists
        genre = animeData['GenreCollection']
        tags = animeData['MediaTagCollection']

        #removes the 'name' portion in the list to make it identical to the genre list
        for x in range(0, len(tags)):
            tags[x] = tags[x]['name']                   

        genreTags = [genre, tags]

        return genreTags
