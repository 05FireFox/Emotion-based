import json
import requests as rq
import pandas as pd
import os
import random
import pickle
import sys

# =========================================
# 1. CONFIGURATION & PATHS
# =========================================
BASE_DIR = r"C:\Users\Praneet\project\filtering"
DATASET_DIR = r"C:\Users\Praneet\project\dataset"

MATRIX_PATH = os.path.join(BASE_DIR, 'user_game_matrix.pkl')
NAMES_PATH = os.path.join(BASE_DIR, 'game_names.pkl')
CSV_PATH = os.path.join(DATASET_DIR, 'steam_games.csv')

EMOTION_URL = 'http://localhost:8081/emotion'

EMOTION_TAG_MAP = {
    "happy": ["Adventure", "Casual", "Indie", "Racing", "Sports", "Open World", "Platformer"],
    "sad": ["Atmospheric", "Story Rich", "RPG", "Drama", "Singleplayer", "Visual Novel"],
    "angry": ["Action", "FPS", "Fighting", "Shooter", "Survival", "Hack and Slash", "War"],
    "neutral": ["Strategy", "Puzzle", "Simulation", "City Builder", "Management", "Card Game"],
    "surprise": ["Sci-fi", "Mystery", "Cyberpunk", "Space", "Futuristic"],
    "fear": ["Horror", "Survival Horror", "Psychological Horror", "Zombies", "Dark"],
    "disgust": ["Gore", "Horror", "Dark"]
}

# =========================================
# 2. LOAD DATA (Matrix + Tags)
# =========================================
print("--- INITIALIZING ENGINE ---")

user_game_df = None
id_to_name = {}
id_to_tags = {} # We need this to filter recommendations by emotion
fallback_games = []

# A. Load Pickle Files (The Brain)
try:
    print(f"Loading Matrix from {MATRIX_PATH}...", end=" ")
    with open(MATRIX_PATH, 'rb') as f:
        user_game_df = pickle.load(f)
    print("✅ Done.")

    print(f"Loading Names from {NAMES_PATH}...", end=" ")
    with open(NAMES_PATH, 'rb') as f:
        id_to_name = pickle.load(f)
    print("✅ Done.")

except Exception as e:
    print(f"\n❌ CRITICAL: Pickle load failed: {e}")

# B. Load CSV (For Tags & Fallback)
try:
    print("Loading Tags from CSV...", end=" ")
    # We only need ID, Name, and Tags
    df = pd.read_csv(CSV_PATH, usecols=lambda c: c in ['AppID', 'app_id', 'id', 'Name', 'title', 'Tags', 'tags', 'genres'])
    
    # Standardize Columns
    df.columns = df.columns.str.lower()
    if 'appid' in df.columns: df.rename(columns={'appid': 'id'}, inplace=True)
    if 'app_id' in df.columns: df.rename(columns={'app_id': 'id'}, inplace=True)
    if 'name' in df.columns: df.rename(columns={'name': 'title'}, inplace=True)
    if 'genres' in df.columns: df.rename(columns={'genres': 'tags'}, inplace=True)
    
    # Clean Data
    df['id'] = pd.to_numeric(df['id'], errors='coerce')
    df = df.dropna(subset=['id', 'title'])
    df['id'] = df['id'].astype(int)
    df['tags'] = df['tags'].astype(str).fillna("")

    # Create Helper Maps
    # 1. Map ID -> Tags (for filtering)
    id_to_tags = pd.Series(df['tags'].values, index=df['id']).to_dict()
    
    # 2. Fallback List (Top 1000 games to save RAM)
    fallback_games = df.head(1000).to_dict(orient='records')
    
    print(f"✅ Loaded {len(id_to_tags)} tag mappings.")

except Exception as e:
    print(f"\n❌ CSV Load Warning: {e}")



# =========================================
# 3. HELPER FUNCTIONS
# =========================================
def get_emotion(request_json):
    try:
        response = rq.post(EMOTION_URL, json=request_json, timeout=2) # 2s timeout is enough usually
        if response.status_code == 200:
            raw_emotion = response.json().get('emotion')
            return raw_emotion.lower() if raw_emotion else "neutral"
    except:
        pass
    return "neutral"

def check_tags_match(game_tags_str, target_tags):
    # Checks if any of the target emotion tags exist in the game's tags
    if not isinstance(game_tags_str, str): return False
    clean_str = game_tags_str.lower()
    for tag in target_tags:
        if tag.lower() in clean_str:
            return True
    return False

# =========================================
# 4. CORE RECOMMENDATION LOGIC
# =========================================
def get_recommendations(request_json, identifier, is_user=True):
    """
    1. Detect Emotion.
    2. Generate candidates using Collaborative Filtering (Pickle Matrix).
    3. Filter candidates based on Emotion Tags (CSV Data).
    """
    # 1. Detect Emotion
    emotion = get_emotion(request_json)
    print(f"DEBUG: User {identifier} | Emotion: {emotion}")
    
    target_tags = EMOTION_TAG_MAP.get(emotion, EMOTION_TAG_MAP["neutral"])
    recommendations = []
    
    # 2. Collaborative Filtering (The Matrix)
    try:
        user_id = int(identifier)
        if user_game_df is not None and user_id in user_game_df.index:
            
            # --- MATRIX MATH START ---
            target_vec = user_game_df.loc[user_id]
            played_games = target_vec[target_vec > 0].index.tolist()
            
            # Find Peers
            overlap = user_game_df.dot(target_vec)
            potential_peers = overlap[overlap > 0].sort_values(ascending=False).head(500).index
            
            # Calculate Scores
            peers_matrix = user_game_df.loc[potential_peers]
            corr = peers_matrix.T.corrwith(target_vec).sort_values(ascending=False)
            top_peers = corr[corr > 0.05].head(50)
            
            if not top_peers.empty:
                weighted_ratings = peers_matrix.loc[top_peers.index].mul(top_peers, axis=0).sum(axis=0)
                final_scores = weighted_ratings / (top_peers.sum() + 1e-9)
                
                # Sort by Score
                candidates = final_scores.sort_values(ascending=False).items()
                
                # --- EMOTION FILTERING ---
                for pid, score in candidates:
                    if pid not in played_games and score > 0.15:
                        
                        # Get Game Details
                        title = id_to_name.get(pid, f"Game {pid}")
                        tags = id_to_tags.get(pid, "")
                        
                        # EMOTION CHECK:
                        # If tags match emotion, we add it. 
                        # If emotion is "neutral", we add everything.
                        if emotion == "neutral" or check_tags_match(tags, target_tags):
                            recommendations.append({
                                "product_id": int(pid),
                                "title": title,
                                "tags": tags,
                                "score": round(score, 2)
                            })
                            
                        if len(recommendations) >= 10:
                            break
            # --- MATRIX MATH END ---

    except Exception as e:
        print(f"Error in Matrix Logic: {e}")

    # 3. Fallback (If Matrix returned nothing or User is new)
    if not recommendations:
        print("DEBUG: Using Fallback (Popularity + Emotion)")
        
        # Filter fallback list by emotion
        filtered_fallback = [
            g for g in fallback_games 
            if check_tags_match(g.get('tags', ''), target_tags)
        ]
        
        # Pick random 5 from filtered, or just top 5
        selection = random.sample(filtered_fallback, min(5, len(filtered_fallback)))
        recommendations = selection

    # 4. Final Return Format
    return {
        'games': recommendations,
        'emotion': emotion
    }