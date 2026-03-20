import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
import ast
import gc

# ==========================================
# 1. LOAD DATA
# ==========================================
print("Content Filtering: Initializing...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to find steam_games.csv
possible_paths = [
    os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'),
    os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'),
    r'C:\Users\Praneet\project\dataset\steam_games.csv'
]
GAMES_PATH = next((p for p in possible_paths if os.path.exists(p)), None)

df_tags = None
game_df_original = None

if GAMES_PATH:
    try:
        # Load Games
        game_df_original = pd.read_csv(GAMES_PATH)
        
        # Normalize Columns
        cols = game_df_original.columns
        if 'AppID' in cols: game_df_original.rename(columns={'AppID': 'id', 'Tags': 'tags'}, inplace=True)
        elif 'app_id' in cols: game_df_original.rename(columns={'app_id': 'id', 'genres': 'tags'}, inplace=True)
        
        # Clean IDs
        game_df_original['id'] = game_df_original['id'].astype(str).str.replace('.0', '', regex=False)
        game_df_original = game_df_original.dropna(subset=['id', 'tags'])
        
        # Pre-compute Tag Matrix (One-Hot Encoding)
        # This is fast enough for 30k games
        print("Content Filtering: Building Tag Matrix...")
        
        def parse_tags(x):
            if isinstance(x, str):
                if x.startswith('['): return ast.literal_eval(x)
                return x.split(',')
            return []

        temp_df = game_df_original[['id', 'tags']].copy()
        temp_df['tags'] = temp_df['tags'].apply(parse_tags)
        temp_df = temp_df.explode('tags')
        
        # One Hot
        df_tags = pd.get_dummies(temp_df['tags']).groupby(temp_df['id']).sum()
        print(f"✅ Content Engine Ready ({len(df_tags)} games).")
        
    except Exception as e:
        print(f"❌ Content Load Error: {e}")
else:
    print("❌ steam_games.csv not found. Content filtering disabled.")

# ==========================================
# 2. RECOMMENDATION LOGIC
# ==========================================
def recommendation(user_id):
    """
    For a hybrid system, Content-Based is hard to do 'on-the-fly' without 
    loading the user's full history. 
    
    If you don't have the user's history loaded in RAM (which we don't, 
    to save memory), we return [] and let Collaborative Filtering handle it.
    """
    # NOTE: To make this work properly, you would need to pass the list of 
    # games the user has ALREADY played to this function. 
    # Since we can't easily fetch that from CSV efficiently, we skip this 
    # for now to prevent 'No Recommendations' errors or crashes.
    
    return [] 

    # If you later want to enable this, you must pass the 'played_games' list 
    # from the collaborative module or database.