import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import math
import os
import ast
import gc  # Added for garbage collection

# ==========================================
# PART 1: LOAD DATASETS & HELPERS
# ==========================================
print("Content Filtering: Loading datasets...")

dataset_folder = 'dataset'

# Robust Loader
def load_csv_robust(filename):
    # Try relative path first
    path = os.path.join(dataset_folder, filename)
    if os.path.exists(path): return path # Return PATH, not dataframe (for chunking)
    if os.path.exists(path + ".csv"): return path + ".csv"
    
    # Try absolute path
    abs_path = fr'C:\Users\Praneet\project\dataset\{filename}'
    if os.path.exists(abs_path): return abs_path
    if os.path.exists(abs_path + ".csv"): return abs_path + ".csv"
    
    return None

# Locate files
games_path = load_csv_robust('steam_games.csv')
reviews_path = load_csv_robust('recommendations.csv')

if not games_path or not reviews_path:
    print("CRITICAL ERROR: distinct CSV files not found.")
    sys.exit(1)

# 1. LOAD GAMES (This is usually small enough to load fully)
game_df_original = pd.read_csv(games_path)
game_df_original = game_df_original.rename(columns={'AppID': 'id', 'Tags': 'tags', 'Name': 'app_name'})

# ==========================================
# PART 2: DATA CLEANING (GAMES)
# ==========================================
print("Content Filtering: Cleaning Games data...")

def clean_id_to_string(value):
    try:
        val_float = float(value)
        if math.isinf(val_float) or math.isnan(val_float): return "0"
        return str(int(val_float))
    except (ValueError, TypeError):
        return "0"

# Clean Game IDs
game_df_original = game_df_original.replace([np.inf, -np.inf], np.nan).dropna(subset=['id'])
game_df_original['id'] = game_df_original['id'].apply(clean_id_to_string)

# Create tags dataframe
game_df = game_df_original[['tags', 'id']].copy()

# Handle different tag formats
def parse_tags(tag_str):
    if pd.isna(tag_str): return []
    tag_str = str(tag_str)
    if tag_str.startswith('['):
        try:
            return ast.literal_eval(tag_str)
        except: pass
    return tag_str.split(',')

game_df['tags'] = game_df['tags'].apply(parse_tags)
game_df = game_df.explode('tags')
game_df['tags'] = game_df['tags'].str.strip()

print("Content Filtering: Processing Tags...")

one_hot_df = pd.get_dummies(game_df['tags'], prefix='tags')
result_df = pd.concat([game_df['id'], one_hot_df], axis=1)

df_tags = result_df.groupby('id').sum()
df_tags.fillna(0, inplace=True)

# Get set of valid game IDs for filtering reviews later
valid_game_ids = set(df_tags.index)
print(f"Content Filtering: Valid Games: {len(valid_game_ids)}")

# ==========================================
# PART 3: LOAD & CLEAN REVIEWS (CHUNKED TO PREVENT CRASH)
# ==========================================
print("Content Filtering: Loading Reviews in Chunks (Memory Safe)...")

chunk_size = 500000  # Process 500k rows at a time
chunks = []

# Define types to save memory
# assuming user_id and app_id can be read as standard columns
dtypes = {
    'is_recommended': 'bool', 
    'user_id': 'str',
    'app_id': 'str' # Load as string initially to match logic, or int if possible
}

# Only load columns we actually use
use_cols = ['app_id', 'is_recommended', 'user_id']

try:
    for chunk in pd.read_csv(reviews_path, chunksize=chunk_size, usecols=use_cols):
        
        # Rename immediately
        chunk = chunk.rename(columns={'app_id': 'product_id', 'is_recommended': 'recommended'})
        
        # Drop NaNs
        chunk = chunk.dropna(subset=['product_id'])
        
        # Ensure ID format matches Games
        chunk['product_id'] = chunk['product_id'].apply(clean_id_to_string)
        
        # FILTER 1: Only keep reviews for games that actually exist in our tags DB
        # This drastically reduces the size before we merge chunks
        chunk = chunk[chunk['product_id'].isin(valid_game_ids)]
        
        if not chunk.empty:
            chunks.append(chunk)
            
    # Combine all cleaned chunks
    if chunks:
        review_df = pd.concat(chunks, axis=0, ignore_index=True)
        del chunks # Free memory
        gc.collect() # Force garbage collection
    else:
        review_df = pd.DataFrame(columns=['product_id', 'recommended', 'user_id'])

except Exception as e:
    print(f"Error during chunk loading: {e}")
    sys.exit(1)

# Convert boolean recommended to 1/0
review_df['recommended'] = review_df['recommended'].apply(lambda x: 1 if x else 0)

print(f"Content Filtering: Reviews Loaded. Count: {len(review_df)}")

# User Frequency Filtering
user_review_count = review_df.groupby('user_id')['product_id'].count()
user_review_index = user_review_count[user_review_count >= 1].index
review_df_min15 = review_df[(review_df["user_id"].isin(user_review_index))]

# Sampling
if not review_df_min15.empty:
    # Cap at 100k rows to keep system fast
    sample_n = min(len(review_df_min15), 100000)
    review_df_min15 = review_df_min15.sample(sample_n, random_state=50)

print("Content Filtering: Ready.")

# ==========================================
# PART 4: RECOMMENDATION LOGIC
# ==========================================

def recommendation(user_id):
    user_id = str(user_id) 
    
    # Ensure types match
    review_df_min15['user_id'] = review_df_min15['user_id'].astype(str)
    
    random_user_vec = review_df_min15[review_df_min15['user_id'] == user_id][['product_id', 'recommended']]

    if random_user_vec.empty:
        return []

    random_user_vec.set_index('product_id', inplace=True)
    random_user_vec.fillna(0, inplace=True)
    
    positive_vec = random_user_vec[random_user_vec['recommended'] > 0]
    
    if len(positive_vec) == 0:
        return []
        
    random_user_vec = random_user_vec.squeeze()
    
    # Ensure indices intersect correctly
    valid_games = df_tags.index.intersection(random_user_vec.index)
    if len(valid_games) == 0:
        return []

    game_tag_pivot = df_tags.loc[valid_games].mul(random_user_vec.loc[valid_games], axis=0)
    game_tag_pivot.fillna(0, inplace=True)
    user_profile = game_tag_pivot.sum() / len(positive_vec)

    played_games = random_user_vec.index

    user_profile_reshaped = user_profile.values.reshape(1, -1)
    
    # Compute Similarity
    cos_sim = cosine_similarity(user_profile_reshaped, df_tags)
    
    cos_sim_df = pd.DataFrame({'cosine_similarity': cos_sim[0], 'ind': df_tags.index})

    reco_games = cos_sim_df[~(cos_sim_df.ind.isin(played_games))].sort_values(
        by='cosine_similarity', ascending=False)[['ind', 'cosine_similarity']]

    # Take top 20 to prevent huge returns
    reco_games = reco_games.head(20)
    
    final_game_suggestions = game_df_original[game_df_original.id.isin(reco_games['ind'])][['id']]
    final_game_suggestions = final_game_suggestions.merge(
        reco_games, left_on='id', right_on='ind')[['id', 'cosine_similarity']]
        
    final_game_suggestions = final_game_suggestions.values.tolist()
    return final_game_suggestions

def ROC(list_of_users, threshold):
    return {}, {}