import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict
import ast


G = nx.read_graphml('synopsis_graph_final.graphml')
data = pd.read_csv('IMDB_movie_details_community.csv')


def get_recommendations(user_movie, preference):
    if preference == "You might like":
            return recommendation1(G, data, user_movie)
    if preference == "You might try":
            return recommendation2(G, data, user_movie)
    if preference == "Expand your horizons":
            return recommendation3(G, data, user_movie)
    if preference == "Something different":
            return recommendation4(G, data, user_movie)

def recommendation1(G, data, watched_film, top_n=10):
    titles= data['title'].tolist()
    if watched_film not in titles:
       raise ValueError("The watched film is not in the graph.")

    # Get the community of the watched film
    idx_film= data.loc[data['title'] == watched_film].index.tolist()[0]
    #print(idx_film)
    idx_community= data.loc[data['title'] == watched_film]['community'].tolist()[0]
    #print(idx_community)


    # Get all neighbors of the watched film
    neighbors = [int(el) for el in list(G.neighbors(f'{idx_film}'))]

    # Filter neighbors that belong to the same community
    same_community_neighbors = [neighbor for neighbor in neighbors if data['community'][neighbor] == idx_community]

    # Watched film genres
    watched_film_genres = set(ast.literal_eval(data['genre'][idx_film]))

    def ranking_criteria(film):
        # Genre similarity
        film_genres = set(ast.literal_eval(data['genre'][film]))
        common_genres_count = len(watched_film_genres.intersection(film_genres))

        similarity= G[f'{idx_film}'][f'{film}']['weight']  # Semantic similarity
        return common_genres_count, similarity



    # Rank neighbors using the ranking criteria
    ranked_neighbors = sorted(same_community_neighbors, key=ranking_criteria, reverse=True )

    # Return top N neighbors
    neighbors= ranked_neighbors[:top_n]
    suggested_films = {data.iloc[neighbor]['title']: ast.literal_eval(data.iloc[neighbor]['genre']) for neighbor in neighbors}

    return suggested_films


def recommendation2(G, data, watched_film, top_n=10):
    # Ensure the film is in the graph
    if watched_film not in data['title'].values:
        raise ValueError("The watched film is not in the dataset.")

    # Get the community of the watched film
    idx_film = data.loc[data['title'] == watched_film].index.tolist()[0]
    idx_community = data.loc[data['title'] == watched_film, 'community'].tolist()[0]

    # Get all neighbors of the watched film
    neighbors = [int(el) for el in list(G.neighbors(str(idx_film)))]

    # Filter neighbors that belong to the same community
    same_community_neighbors = [neighbor for neighbor in neighbors if data.loc[neighbor, 'community'] == idx_community]

    # Watched film genres
    watched_film_genres = set(ast.literal_eval(data.loc[idx_film, 'genre']))

    def ranking_criteria(film):
        # Ensure the genres are different from the watched film
        film_genres = set(ast.literal_eval(data.loc[film, 'genre']))
        different_genres_count = len(film_genres.difference(watched_film_genres))

        # Semantic similarity
        similarity_score = G[f'{idx_film}'][f'{film}']['weight']

        # Prioritize films with different genres and highest semantic similarity
        return different_genres_count, similarity_score  # negative for descending sort on similarity

    # Rank neighbors using the ranking criteria
    ranked_neighbors = sorted(same_community_neighbors, key=ranking_criteria, reverse=True)

    # Return top N neighbors
    neighbors = ranked_neighbors[:top_n]
    suggested_films = {data.iloc[neighbor]['title']: ast.literal_eval(data.iloc[neighbor]['genre']) for neighbor in neighbors}

    return suggested_films


def recommendation3(G, data, watched_film, top_n=10):
    # Ensure the film is in the graph
    if watched_film not in data['title'].values:
        raise ValueError("The watched film is not in the dataset.")

    # Get the index of the watched film
    idx_film = data.loc[data['title'] == watched_film].index.tolist()[0]
    watched_film_community = data.loc[data['title'] == watched_film, 'community'].tolist()[0]

    # Watched film genres
    #watched_film_genres = set(ast.literal_eval(data.loc[idx_film, 'genre']))

    # Find all nodes not in the same community
    different_community_neighbors = data[data['community'] != watched_film_community].index.tolist()

    # Compute shortest paths from the watched film to all other films
    shortest_paths = nx.single_source_dijkstra_path_length(G, str(idx_film))

    # Filter paths to only include nodes in different communities
    valid_paths = {int(node): length for node, length in shortest_paths.items() if int(node) in different_community_neighbors}

    def ranking_criteria(film):
        # Genre similarity
        #film_genres = set(ast.literal_eval(data.loc[film, 'genre']))
        #common_genres_count = len(watched_film_genres.intersection(film_genres))

        # Shortest path length
        path_length = valid_paths[film]

        # Semantic similarity
        similarity_score = G[f'{idx_film}'][f'{film}']['weight'] if G.has_edge(f'{idx_film}', f'{film}') else 0

        # Score calculation: prioritize shortest path and semantic similarity
        score = -path_length, similarity_score
        return score

    # Rank films using the ranking criteria
    ranked_neighbors = sorted(valid_paths.keys(), key=ranking_criteria, reverse=True)

    # Return top N neighbors
    neighbors = ranked_neighbors[:top_n]
    suggested_films = {data.iloc[neighbor]['title']: ast.literal_eval(data.iloc[neighbor]['genre']) for neighbor in neighbors}

    return suggested_films


def recommendation4(G, data, watched_film, top_n_per_community=2):
    # Ensure the film is in the graph
    if watched_film not in data['title'].values:
        raise ValueError("The watched film is not in the dataset.")

    # Get the index of the watched film
    idx_film = data.loc[data['title'] == watched_film].index.tolist()[0]
    watched_film_community = data.loc[data['title'] == watched_film, 'community'].tolist()[0]

    # Find all nodes not in the same community
    different_community_neighbors = data[data['community'] != watched_film_community].index.tolist()

    # Compute shortest paths from the watched film to all other films
    shortest_paths = nx.single_source_dijkstra_path_length(G, str(idx_film))

    # Filter paths to only include nodes in different communities
    valid_paths = {int(node): length for node, length in shortest_paths.items() if int(node) in different_community_neighbors}

    def ranking_criteria(film):
        # Shortest path length
        path_length = valid_paths[film]

        # Semantic similarity
        similarity_score = G[f'{idx_film}'][f'{film}']['weight'] if G.has_edge(f'{idx_film}', f'{film}') else 0

        # Score calculation: prioritize shortest path and semantic similarity
        
        return -path_length, similarity_score

    
    # Rank films using the ranking criteria
    ranked_neighbors = list(sorted(valid_paths.keys(), key=ranking_criteria, reverse=True))
 

    # Group the recommendations by community
    recommendations_by_community = defaultdict(list)
    for neighbor in ranked_neighbors:
        community = data.iloc[neighbor]['community']
        recommendations_by_community[community].append(neighbor)
        

   
    # Collect the top N recommendations per community
    top_recommendations = {}
    for community, neighbors in recommendations_by_community.items():
        top_neighbors = neighbors[:top_n_per_community]
      
        top_recommendations[community] = {data.iloc[neighbor]['title']: data.iloc[neighbor]['genre'] for neighbor in top_neighbors}
    data = sorted(top_recommendations.items(), key=lambda x: x[0])
    films = []
    genres = []
    for entry in data:
        for film, genre_list in entry[1].items():
            films.append(film)
            genres.append(eval(genre_list))
    df = pd.DataFrame({"Film": films, "Genres": genres})
    return df

def main():
    # Streamlit app
    st.title("Movie Recommendation System")
    st.write("Our Film Dataset!", data.title)
    # Input from user
    user_movie = st.text_input("Enter the film you just watched: (for example: Il Re Leone)")
    preference = st.radio("What kind of film do you want to watch next?", ( "You might like",  "You might try", "Expand your horizons" , "Something different"))

    # Display recommendation
    if st.button("Get Recommendation"):
            recommendation = get_recommendations(user_movie, preference)
            try:
                st.write("We recommend you to watch:", pd.Series(recommendation))
            except Exception as e:
                st.write("We recommend you to watch:", recommendation)
if __name__ == "__main__":
    main()