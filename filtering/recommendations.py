import json
import requests as rq
import pandas as pd
import os
import pickle
import traceback
import numpy as np

# =========================================
# 1. CONFIGURATION & PATHS
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DYNAMIC PATHS
MATRIX_PATH = os.path.join(BASE_DIR, 'user_game_matrix.pkl')
NAMES_PATH  = os.path.join(BASE_DIR, 'game_names.pkl')
USER_MAP_PATH = os.path.join(BASE_DIR, 'user_list.csv')

# Find the Dataset
possible_csv_paths = [
    os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'),       
    os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'), 
    os.path.join(BASE_DIR, 'steam_games.csv'),
    r'C:\Users\Praneet\project\dataset\steam_games.csv' 
]
CSV_PATH = next((p for p in possible_csv_paths if os.path.exists(p)), None)

# Emotion Service URL
EMOTION_URL = os.environ.get('EMOTION_SERVICE_URL', 'http://localhost:8081/emotion')

EMOTION_TAG_MAP = {
    "happy": ["Adventure", "Casual", "Indie", "Racing", "Sports", "Open World"],
    "sad": ["Atmospheric", "Story Rich", "RPG", "Drama", "Visual Novel"],
    "angry": ["Action", "FPS", "Fighting", "Shooter", "Survival", "War"],
    "neutral": ["Strategy", "Puzzle", "Simulation", "City Builder", "Card Game"],
    "surprise": ["Sci-fi", "Mystery", "Cyberpunk", "Space", "Futuristic"],
    "fear": ["Horror", "Survival Horror", "Psychological Horror", "Zombies"],
    "disgust": ["Gore", "Horror", "Dark"]
}

# =========================================
# 2. LOAD DATA
# =========================================
print("\n--- INITIALIZING CORE ENGINE ---")

user_game_df = None
id_to_name = {}
id_to_tags = {}
id_to_date = {} # New: Store Release Dates
internal_to_steam = {} 
steam_to_internal = {}

# A. Load Pickle Matrix
try:
    if os.path.exists(MATRIX_PATH):
        print(f"Loading Matrix...", end=" ")
        with open(MATRIX_PATH, 'rb') as f:
            user_game_df = pickle.load(f)
        print(f"✅ Done. Matrix Shape: {user_game_df.shape}")
        
        if not user_game_df.empty:
            valid_ids = user_game_df.index.tolist()
            print(f"   💡 VALID USER IDs IN MATRIX (Try these): {valid_ids[:10]} ...")
    else:
        print(f"❌ CRITICAL: Matrix not found at {MATRIX_PATH}")
except Exception as e:
    print(f"❌ Matrix Load Error: {e}")

# B. Load Game Names
try:
    if os.path.exists(NAMES_PATH):
        print(f"Loading Names...", end=" ")
        with open(NAMES_PATH, 'rb') as f:
            id_to_name = pickle.load(f)
        print("✅ Done.")
except Exception as e:
    print(f"⚠️ Names Load Error: {e}")

# C. Load User Map
try:
    if os.path.exists(USER_MAP_PATH):
        print("Loading User Map...", end=" ")
        u_df = pd.read_csv(USER_MAP_PATH, header=None, names=['internal_id', 'steam_id'], dtype=str)
        u_df = u_df.dropna(how='any') 
        
        for _, row in u_df.iterrows():
            try:
                s_id = str(row['steam_id']).split('.')[0].strip()
                i_id = int(float(row['internal_id']))
                internal_to_steam[i_id] = s_id
                steam_to_internal[s_id] = i_id
            except: continue
        print(f"✅ Loaded {len(internal_to_steam)} users.")
    else:
        print("⚠️ User Map not found.")
except Exception as e:
    print(f"⚠️ User Map Error: {e}")

# D. Load CSV (Tags & Release Date)
try:
    if CSV_PATH:
        print(f"Loading CSV from {CSV_PATH}...", end=" ")
        df = pd.read_csv(CSV_PATH, dtype=str)
        
        # Normalize and Rename
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        rename_map = {
            'appid': 'id', 'app_id': 'id', 
            'name': 'title', 
            'genres': 'tags', 
            'release_date': 'date', 'releasedate': 'date'
        }
        df = df.rename(columns=rename_map)
        df = df.loc[:, ~df.columns.duplicated()] # Remove duplicates

        if 'id' in df.columns:
            df = df.dropna(subset=['id'])
            
            # Fill Missing
            if 'tags' not in df.columns: df['tags'] = ""
            if 'date' not in df.columns: df['date'] = "Unknown"
            
            df['tags'] = df['tags'].fillna("")
            df['date'] = df['date'].fillna("Unknown")
            
            def safe_id(x):
                try: return int(float(str(x)))
                except: return 0
                
            # Create Lookup Dictionaries
            id_to_tags = pd.Series(df['tags'].values, index=df['id'].apply(safe_id)).to_dict()
            id_to_date = pd.Series(df['date'].values, index=df['id'].apply(safe_id)).to_dict()
            
            print(f"✅ Loaded Data for {len(id_to_tags)} games.")
        else:
            print("❌ 'id' column missing in CSV.")
except Exception as e:
    print(f"❌ CSV Load Error: {e}")

# =========================================
# 3. HELPER FUNCTIONS
# =========================================
def get_emotion(request_json):
    try:
        response = rq.post(EMOTION_URL, json=request_json, timeout=1)
        if response.status_code == 200:
            return response.json().get('emotion', 'neutral').lower()
    except: pass
    return "neutral"

def check_tags_match(game_tags_str, target_tags):
    if not isinstance(game_tags_str, str) or not game_tags_str: return False
    clean_str = game_tags_str.lower()
    for tag in target_tags:
        if tag.lower() in clean_str: return True
    return False

# =========================================
# 4. CORE COLLABORATIVE LOGIC
# =========================================
def get_recommendations(request_json, identifier, is_user=True):
    emotion = get_emotion(request_json)
    print(f"\n--- REQUEST: User={identifier} | Emotion={emotion} ---")
    
    target_tags = EMOTION_TAG_MAP.get(emotion, EMOTION_TAG_MAP["neutral"])
    recommendations = []
    
    # 1. RESOLVE MATRIX ID
    matrix_id = None
    clean_input = str(identifier).split('.')[0].strip()
    
    if clean_input.isdigit():
        input_int = int(clean_input)
        if user_game_df is not None and input_int in user_game_df.index:
            matrix_id = input_int
        elif input_int in steam_to_internal:
            possible_id = steam_to_internal[input_int]
            if possible_id in user_game_df.index:
                matrix_id = possible_id

    if matrix_id is None:
        if user_game_df is not None and clean_input in user_game_df.index:
            matrix_id = clean_input

    print(f"DEBUG: Input '{identifier}' resolved to Matrix Key: '{matrix_id}'")

    if matrix_id is None:
        return {'games': [], 'status': f"User {identifier} not found in database.", 'emotion': emotion}

    # 2. RUN MATRIX FACTORIZATION
    try:
        target_vec = user_game_df.loc[matrix_id]
        played_games = target_vec[target_vec > 0].index.tolist()
        
        overlap = user_game_df.dot(target_vec)
        potential_peers = overlap[overlap > 0].sort_values(ascending=False).head(200).index
        
        if not potential_peers.empty:
            peers_matrix = user_game_df.loc[potential_peers]
            corr = peers_matrix.T.corrwith(target_vec).sort_values(ascending=False)
            top_peers = corr[corr > 0.01].head(50) 
            
            if not top_peers.empty:
                weighted_ratings = peers_matrix.loc[top_peers.index].mul(top_peers, axis=0).sum(axis=0)
                final_scores = weighted_ratings / (top_peers.sum() + 1e-9)
                
                # --- FIX: LIST CAST TO PREVENT ZIP ERROR ---
                candidates = list(final_scores.sort_values(ascending=False).items())
                # -------------------------------------------
                
                print(f"DEBUG: Matrix found {len(candidates)} candidates.")
                
                for pid, score in candidates:
                    if pid not in played_games:
                        pid_int = int(pid)
                        g_name = id_to_name.get(pid_int, f"Unknown Game ({pid})")
                        g_tags = id_to_tags.get(pid_int, "")
                        g_date = id_to_date.get(pid_int, "Unknown Date") # Get Release Date
                        
                        # EMOTION FILTERING
                        is_match = False
                        
                        if emotion == "neutral":
                            is_match = True
                        elif g_tags == "":
                            is_match = True # Allow if missing tags (Safety)
                        elif check_tags_match(g_tags, target_tags):
                            is_match = True
                        
                        if is_match:
                            recommendations.append({
                                "title": g_name,
                                "release_date": g_date,
                                "product_id": pid  # <--- FIXED: Added product_id for frontend
                            })
                            
                    if len(recommendations) >= 8: break
            else:
                print("DEBUG: No peers correlated enough.")
                
    except Exception as e:
        print(f"❌ Matrix Calc Error: {e}")
        traceback.print_exc()

    if not recommendations:
        print("⚠️ Core Technique finished but found 0 matching games.")
        
    return {
        'games': recommendations,
        'emotion': emotion,
        'status': "Success"
    }