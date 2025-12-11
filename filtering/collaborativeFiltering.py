import pandas as pd
import os
import pickle
import sys

# ==========================================
# 1. LOAD PRE-CALCULATED MATRIX
# ==========================================
print("Collaborative Filtering: Initializing...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamic paths to find your pickle file
MATRIX_PATH = os.path.join(BASE_DIR, 'user_game_matrix.pkl')
NAMES_PATH  = os.path.join(BASE_DIR, 'game_names.pkl')

user_game_df = None
game_names = {}

try:
    if os.path.exists(MATRIX_PATH):
        print(f"Loading Matrix from {MATRIX_PATH}...", end=" ")
        with open(MATRIX_PATH, 'rb') as f:
            user_game_df = pickle.load(f)
        print("✅ Done.")
    else:
        print(f"❌ CRITICAL: user_game_matrix.pkl not found at {MATRIX_PATH}")
        
    if os.path.exists(NAMES_PATH):
        with open(NAMES_PATH, 'rb') as f:
            game_names = pickle.load(f)
except Exception as e:
    print(f"❌ Error loading Pickles: {e}")

# ==========================================
# 2. RECOMMENDATION LOGIC
# ==========================================
def recommendation(user_id):
    """
    Returns: List of [game_id (str), score (float)]
    """
    user_id = str(user_id) # Ensure ID is string to match Pickle index

    # Safety checks
    if user_game_df is None: 
        return []
    
    if user_id not in user_game_df.index:
        # User not in the matrix (New User or ID Mismatch)
        print(f"Collaborative: User {user_id} not found in matrix.")
        return []

    try:
        # 1. Get User Vector
        target_user_vec = user_game_df.loc[user_id]
        played_games = target_user_vec[target_user_vec > 0].index.tolist()

        # 2. Find Similar Users (Pearson Correlation)
        # We limit to top 1000 users with overlap to save time
        overlap = user_game_df.dot(target_user_vec)
        potential_peers = overlap[overlap > 0].sort_values(ascending=False).head(1000).index
        
        if potential_peers.empty:
            return []

        peers_matrix = user_game_df.loc[potential_peers]
        
        # Correlate
        corr_scores = peers_matrix.T.corrwith(target_user_vec).sort_values(ascending=False)
        
        # Keep positive correlations only
        top_peers = corr_scores[corr_scores > 0.1].head(50)
        
        if top_peers.empty:
            return []

        # 3. Predict Ratings (Weighted Average)
        # (Peer_Ratings * Peer_Similarity) / Sum(Peer_Similarity)
        peer_ratings = peers_matrix.loc[top_peers.index]
        weighted_sum = peer_ratings.mul(top_peers, axis=0).sum(axis=0)
        sim_sum = top_peers.sum()
        
        predicted_scores = weighted_sum / (sim_sum + 1e-9)
        
        # 4. Filter Already Played & Format
        recommendations = predicted_scores.drop(index=played_games, errors='ignore')
        recommendations = recommendations.sort_values(ascending=False).head(20)

        results = []
        for game_id, score in recommendations.items():
            # Ensure game_id is string
            g_id_str = str(game_id)
            results.append([g_id_str, float(score)])

        return results

    except Exception as e:
        print(f"Collaborative Error: {e}")
        return []