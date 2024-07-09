# Semantic Network- Based Movie Recommendation System

**Collaborators** : Valentina Brivio, Enrico Cipolla Cipolla, Pierluigi Mancinelli, Arianna Zottoli


### Introduction
The main goal of this project is to enhance movie recommendation systems by incorporating semantic analysis of movie plot synopses. Unlike traditional systems that rely on genre, actors, or user ratings, this approach focuses on the thematic and narrative elements of movies to uncover hidden connections and recommend films that might not be otherwise suggested.

### Data Collection
The primary data source is the IMDB Spoiler Dataset from Kaggle, consisting of 1572 films with variables such as duration, genres, summary, and synopsis. This dataset provides detailed descriptions of movie storylines, which are crucial for the semantic analysis employed in this project. Plot synopses are then used to compute semantic similarities between films, and a network of films is constructed, with weights given by this semantic similarity. The dataset is then pruned using network backboning techniques. 

For further details, refer to the full project report.


