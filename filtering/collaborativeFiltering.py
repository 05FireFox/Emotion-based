import pandas as pd
import numpy as np
import sys
import math
import os
import gc

# ==========================================
# PART 1: LOAD DATASETS (MEMORY SAFE)
# ==========================================
print("Collaborative Filtering: Loading datasets...")

def clean_id_to_string(value):
    try:
        val_float = float(value)
        if math.isinf(val_float) or math.isnan(val_float):
            return "0"
        return str(int(val_float))
    except (ValueError, TypeError):
        return "0"

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    """Robust path finder"""
    paths = [
        os.path.join(BASE_DIR, 'dataset', filename),
        os.path.join(BASE_DIR, '..', 'dataset', filename),
        os.path.join(r'C:\Users\Praneet\project\dataset', filename)
    ]
    for p in paths:
        if os.path.exists(p): return p
    return None

# 1. Load Games (Metadata)
game_path = get_file_path('steam_games.csv')
if not game_path:
    # Try alternate name
    game_path = get_file_path('steam_games.csv.csv')

if not game_path:
    print("CRITICAL ERROR: Games file not found in Collaborative Filtering.")
    sys.exit(1)

try:
    game_df = pd.read_csv(game_path, dtype=str)
    # Standardize
    if 'AppID' in game_df.columns:
        game_df = game_df.rename(columns={'AppID': 'id', 'Name': 'app_name'})
    elif 'app_id' in game_df.columns:
        game_df = game_df.rename(columns={'app_id': 'id', 'title': 'app_name'})
    
    game_df['id'] = game_df['id'].apply(clean_id_to_string)
    game_df = game_df[['id', 'app_name']].dropna()
    valid_game_ids = set(game_df['id'])
except Exception as e:
    print(f"Error loading games: {e}")
    sys.exit(1)

# 2. Load Reviews (CHUNKED)
review_path = get_file_path('recommendations.csv')
if not review_path:
    review_path = get_file_path('recommendations.csv.csv')

if not review_path:
    print("CRITICAL ERROR: Recommendations file not found.")
    sys.exit(1)

print("Collaborative Filtering: Sampling Reviews...")

chunk_size = 500000
chunks = []
total_rows = 0
MAX_ROWS = 150000 # Hard limit for RAM safety

try:
    # Only read columns we need
    # Adjust column names based on your CSV (user_id, app_id, is_recommended)
    # Assuming columns: 'app_id', 'helpful', 'funny', 'date', 'is_recommended', 'hours', 'user_id', 'review_id'
    use_cols = ['app_id', 'is_recommended', 'user_id']
    
    for chunk in pd.read_csv(review_path, chunksize=chunk_size, usecols=lambda c: c in use_cols):
        # Renaming for consistency
        if 'app_id' in chunk.columns: chunk = chunk.rename(columns={'app_id': 'product_id'})
        if 'is_recommended' in chunk.columns: chunk = chunk.rename(columns={'is_recommended': 'recommended'})
        
        # Clean IDs
        chunk['product_id'] = chunk['product_id'].apply(clean_id_to_string)
        chunk['user_id'] = chunk['user_id'].apply(clean_id_to_string)
        
        # Convert recommended to int (True->1, False->0)
        chunk['recommended'] = chunk['recommended'].astype(int)
        
        # Filter: Only keep games we know
        chunk = chunk[chunk['product_id'].isin(valid_game_ids)]
        
        if not chunk.empty:
            chunks.append(chunk)
            total_rows += len(chunk)
            
        if total_rows >= MAX_ROWS:
            break
            
    if chunks:
        review_df = pd.concat(chunks, axis=0)
    else:
        review_df = pd.DataFrame(columns=['user_id', 'product_id', 'recommended'])
        
    del chunks
    gc.collect()

except Exception as e:
    print(f"Error loading reviews: {e}")
    review_df = pd.DataFrame()

# ==========================================
# PART 2: MATRIX PREPARATION
# ==========================================

if not review_df.empty:
    print(f"Collaborative Filtering: Processing {len(review_df)} reviews...")
    # Deduplicate
    review_df = review_df.drop_duplicates(subset=['user_id', 'product_id'])
    
    # Pivot
    print("Collaborative Filtering: Creating Pivot Table...")
    user_game_df = pd.pivot_table(review_df, index='user_id', columns='product_id', values='recommended', fill_value=0)
else:
    user_game_df = pd.DataFrame()

print("Collaborative Filtering: Ready.")

# ==========================================
# PART 3: RECOMMENDATION LOGIC
# ==========================================

def recommendation(user_id):
    user_id = str(user_id)

    if user_game_df.empty or user_id not in user_game_df.index:
        return []

    # Get target user vector
    target_user_vector = user_game_df.loc[user_id]
    games_played = target_user_vector[target_user_vector > 0].index.tolist()
    
    if not games_played:
        return []

    # 1. Find similar users
    # Filter matrix to only users who played the same games (optimization)
    relevant_users = user_game_df[games_played].sum(axis=1)
    relevant_users = relevant_users[relevant_users > 0].index
    
    subset_df = user_game_df.loc[relevant_users]
    
    # Cap subset size for speed
    if len(subset_df) > 500:
        subset_df = subset_df.sample(500, random_state=42)
    
    if user_id not in subset_df.index:
        # Should not happen given logic above, but safe guard
        return []

    # Transpose for User-User Correlation
    corr_matrix = subset_df.T.corr(method='pearson') 
    
    # Get correlations
    user_correlations = corr_matrix[user_id].sort_values(ascending=False)
    user_correlations = user_correlations.drop(user_id, errors='ignore')
    top_users = user_correlations[user_correlations > 0].head(50) # Top 50 similar users
    
    if top_users.empty:
        return []

    # 2. Weighted Rating Prediction
    similar_users_ratings = user_game_df.loc[top_users.index]
    
    weighted_scores = pd.Series(0.0, index=similar_users_ratings.columns)
    total_similarity = 0
    
    for other_user, score in top_users.items():
        user_ratings = similar_users_ratings.loc[other_user]
        weighted_scores += user_ratings * score
        total_similarity += score
        
    if total_similarity > 0:
        weighted_scores /= total_similarity
        
    # 3. Filter and Sort
    weighted_scores = weighted_scores.drop(games_played, errors='ignore')
    recommendations = weighted_scores[weighted_scores > 0].sort_values(ascending=False).head(10)
    
    # 4. Join with Names
    reco_df = pd.DataFrame({'id': recommendations.index, 'weighted_score': recommendations.values})
    
    final_output = reco_df.merge(game_df, on='id', how='inner')
    
    # Return List of Lists for compatibility with hybridReco
    return final_output[['id', 'weighted_score']].values.tolist()