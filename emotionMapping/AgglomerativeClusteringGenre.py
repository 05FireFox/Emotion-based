from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import pandas as pd

games_df = pd.read_json('games.jl', lines=True)

games_df_sm = games_df.drop(columns=['metascore','n_reviews','sentiment','discount_price','description','publisher'])

# explode the genres column into individual rows
exploded_df_12 = games_df_sm.explode('genres')

# find the unique values in the genres column
unique_genres = exploded_df_12['genres'].unique()

unique_genres = [s for s in unique_genres if isinstance(s, str)]

# create a TfidfVectorizer to convert the genres into numerical features
vectorizer = TfidfVectorizer()

# convert the genres column into a sparse matrix of numerical features
X = vectorizer.fit_transform(unique_genres)

# use Agglomerative clustering to cluster the genres into 7 clusters
agg_clustering = AgglomerativeClustering(n_clusters=7)
labels = agg_clustering.fit_predict(X.toarray())

# create a dictionary to store the genres in each cluster
genre_clusters = {i: [] for i in range(7)}

# assign each genre to a cluster based on the cluster label
for i, genre in enumerate(unique_genres):
    genre_clusters[labels[i]].append(genre)

print(genre_clusters)
