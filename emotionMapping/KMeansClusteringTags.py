from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd


games_df = pd.read_json('games.jl', lines=True)

games_df_sm = games_df.drop(columns=['metascore','n_reviews','sentiment','discount_price','description','publisher'])

# explode the tags column into individual rows
exploded_df_12 = games_df_sm.explode('tags')

# find the unique values in the tags column
unique_tags = exploded_df_12['tags'].unique()

unique_tags = [s for s in unique_tags if isinstance(s, str)]

# create a TfidfVectorizer to convert the tags into numerical features
vectorizer = TfidfVectorizer()

# convert the tags column into a sparse matrix of numerical features
X = vectorizer.fit_transform(unique_tags)

# use K-Means clustering to cluster the tags into 7 clusters
kmeans = KMeans(n_clusters=7)
labels = kmeans.fit_predict(X.toarray())

# create a dictionary to store the tags in each cluster
tag_clusters = {i: [] for i in range(7)}
tag_clusters
# assign each tag to a cluster based on the cluster label
for i, tag in enumerate(unique_tags):
    tag_clusters[labels[i]].append(tag)

print(tag_clusters)