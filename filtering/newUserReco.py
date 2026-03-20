import pandas as pd
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.corpora import Dictionary
import pickle
import ast
import os
import math

# ==========================================
# 1. ROBUST DATA LOADING
# ==========================================

def clean_id_to_string(value):
    """Safely converts IDs to string."""
    try:
        val_float = float(value)
        if math.isinf(val_float) or math.isnan(val_float):
            return "0"
        return str(int(val_float))
    except (ValueError, TypeError):
        return "0"

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_games_dataset():
    """Finds the steam_games file dynamically"""
    paths_to_try = [
        os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'),
        os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'),
        r'C:\Users\Praneet\project\dataset\steam_games.csv'
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
            
    print("WARNING: steam_games.csv not found in newUserReco.")
    return None

game_path = load_games_dataset()

if game_path:
    # Load minimal columns to save memory
    try:
        game_df_original = pd.read_csv(game_path, dtype=str)
        
        # Standardize Columns
        if 'AppID' in game_df_original.columns:
            game_df_original = game_df_original.rename(columns={'AppID': 'id', 'Name': 'title', 'Tags': 'tags'})
        elif 'app_id' in game_df_original.columns:
            game_df_original = game_df_original.rename(columns={'app_id': 'id', 'title': 'title', 'genres': 'tags'})
            
        # Clean IDs
        game_df_original['id'] = game_df_original['id'].apply(clean_id_to_string)
        
    except Exception as e:
        print(f"Error loading games: {e}")
        game_df_original = pd.DataFrame(columns=['id', 'title', 'tags'])
else:
    game_df_original = pd.DataFrame(columns=['id', 'title', 'tags'])

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

# LDA Loading (Optional - handled safely)
dictionary = Dictionary()
lda_model = None
try:
    dict_path = os.path.join(BASE_DIR, 'lda_dict.dict')
    model_path = os.path.join(BASE_DIR, 'lda_model.pkl')
    if os.path.exists(dict_path) and os.path.exists(model_path):
        dictionary = Dictionary.load(dict_path)
        with open(model_path, "rb") as f:
            lda_model = pickle.load(f)
except:
    pass

def map_tags_to_topics(unseen_game_tag):
    if lda_model is None: return []
    try:
        # Simple text processing for topics
        tokens = str(unseen_game_tag).lower().split()
        bow_vector = dictionary.doc2bow(tokens)
        topics_list = []
        if hasattr(lda_model, 'getitem'):
            for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
                topics_list.append(index)
        return topics_list
    except:
        return []

# ==========================================
# 3. RECOMMENDATION LOGIC (MEMORY SAFE)
# ==========================================

def recommendation(steam_id):
    steam_id = str(steam_id)
    
    # 1. Prepare Data
    if game_df_original.empty:
        return pd.DataFrame()
        
    # Check if ID exists in our DB
    if steam_id not in game_df_original['id'].values:
        # Crucial: If user sends a User ID (7656...) here by mistake, we return empty
        # instead of trying to calculate similarity and crashing.
        print(f"Game ID {steam_id} not found in database.")
        return pd.DataFrame()

    # Work with a copy
    game_df = game_df_original[['tags', 'id']].dropna().copy()
    
    # 2. Clean Tags
    def clean_tags(tag_str):
        try:
            if tag_str.startswith('['):
                return ast.literal_eval(tag_str)
            return [t.strip() for t in tag_str.split(',')]
        except:
            return []

    game_df['tags_list'] = game_df['tags'].apply(clean_tags)
    
    # 3. MEMORY FIX: Limit to Top N Tags
    # We explode to count all tags
    all_tags = game_df.explode('tags_list')
    top_tags = all_tags['tags_list'].value_counts().head(100).index.tolist() # Keep only top 100
    
    # Filter dataset to only these tags
    game_df_exploded = all_tags[all_tags['tags_list'].isin(top_tags)]
    
    # 4. Create Matrix (One-Hot)
    # This matrix will now be (Games x 100) instead of (Games x 67000)
    one_hot = pd.get_dummies(game_df_exploded['tags_list'])
    
    # Group back by ID
    # This creates a vector for each game
    game_vectors = one_hot.groupby(game_df_exploded['id']).sum()
    
    # 5. Calculate Similarity
    if steam_id not in game_vectors.index:
        return pd.DataFrame()
        
    target_vec = game_vectors.loc[[steam_id]] # Double brackets to keep DataFrame shape
    
    # Cosine Similarity
    sim_scores = cosine_similarity(target_vec, game_vectors)
    
    # Create Result DF
    sim_df = pd.DataFrame(sim_scores.T, index=game_vectors.index, columns=['similarity'])
    
    # Remove self
    sim_df = sim_df[sim_df.index != steam_id]
    
    # Sort
    sim_df = sim_df.sort_values(by='similarity', ascending=False).head(10)
    
    # 6. Formatting
    final_results = sim_df.merge(game_df_original, left_index=True, right_on='id')
    final_results = final_results.rename(columns={'id': 'product_id', 'similarity': 'weighted_avg'})
    
    # Add Topics
    final_results['topics'] = final_results['tags'].apply(map_tags_to_topics)
    
    cols = ['product_id', 'weighted_avg', 'title', 'tags', 'topics']
    return final_results[cols]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(recommendation(sys.argv[1]))