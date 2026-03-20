import json
import requests as rq
import pandas as pd
import os
import pickle
import traceback
import numpy as np
import random

# =========================================
# 1. CONFIGURATION & PATHS
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MATRIX_PATH = os.path.join(BASE_DIR, 'user_game_matrix.pkl')
NAMES_PATH  = os.path.join(BASE_DIR, 'game_names.pkl')
USER_MAP_PATH = os.path.join(BASE_DIR, 'user_list.csv')

possible_csv_paths = [
    os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'),       
    os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'), 
    os.path.join(BASE_DIR, 'steam_games.csv'),
    r'C:\Users\Praneet\project\dataset\steam_games.csv' 
]
CSV_PATH = next((p for p in possible_csv_paths if os.path.exists(p)), None)

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
# EMERGENCY BACKUP GAMES (STRICT FALLBACK)
# =========================================
EMERGENCY_BACKUP_GAMES = {
    "happy": [{"title": "Stardew Valley", "release_date": "2016", "product_id": "413150"}, {"title": "Fall Guys", "release_date": "2020", "product_id": "1097150"}, {"title": "Slime Rancher", "release_date": "2017", "product_id": "433340"}, {"title": "Portal 2", "release_date": "2011", "product_id": "620"}, {"title": "Rocket League", "release_date": "2015", "product_id": "252950"}, {"title": "A Short Hike", "release_date": "2019", "product_id": "1055540"}, {"title": "Planet Coaster", "release_date": "2016", "product_id": "493340"}, {"title": "Animal Crossing", "release_date": "2020", "product_id": "00001"}],
    "sad": [{"title": "To the Moon", "release_date": "2011", "product_id": "206440"}, {"title": "What Remains of Edith Finch", "release_date": "2017", "product_id": "501300"}, {"title": "Life is Strange", "release_date": "2015", "product_id": "319630"}, {"title": "Journey", "release_date": "2020", "product_id": "1208260"}, {"title": "Gris", "release_date": "2018", "product_id": "683320"}, {"title": "Spiritfarer", "release_date": "2020", "product_id": "972660"}, {"title": "Firewatch", "release_date": "2016", "product_id": "383870"}, {"title": "That Dragon, Cancer", "release_date": "2016", "product_id": "419460"}],
    "angry": [{"title": "DOOM Eternal", "release_date": "2020", "product_id": "782330"}, {"title": "Sekiro: Shadows Die Twice", "release_date": "2019", "product_id": "814380"}, {"title": "Mortal Kombat 11", "release_date": "2019", "product_id": "976310"}, {"title": "Hades", "release_date": "2020", "product_id": "1145360"}, {"title": "God of War", "release_date": "2022", "product_id": "1593500"}, {"title": "Hotline Miami", "release_date": "2012", "product_id": "219150"}, {"title": "Devil May Cry 5", "release_date": "2019", "product_id": "601150"}, {"title": "Left 4 Dead 2", "release_date": "2009", "product_id": "550"}],
    "neutral": [{"title": "Civilization VI", "release_date": "2016", "product_id": "289070"}, {"title": "Cities: Skylines", "release_date": "2015", "product_id": "255710"}, {"title": "Factorio", "release_date": "2020", "product_id": "427520"}, {"title": "Slay the Spire", "release_date": "2019", "product_id": "646570"}, {"title": "The Sims 4", "release_date": "2014", "product_id": "1222670"}, {"title": "Mini Metro", "release_date": "2015", "product_id": "287980"}, {"title": "RimWorld", "release_date": "2018", "product_id": "294100"}, {"title": "Dorfromantik", "release_date": "2022", "product_id": "1455840"}],
    "surprise": [{"title": "Outer Wilds", "release_date": "2020", "product_id": "753640"}, {"title": "Portal", "release_date": "2007", "product_id": "400"}, {"title": "Subnautica", "release_date": "2018", "product_id": "264710"}, {"title": "Cyberpunk 2077", "release_date": "2020", "product_id": "1091500"}, {"title": "Control", "release_date": "2020", "product_id": "870780"}, {"title": "The Stanley Parable", "release_date": "2013", "product_id": "221910"}, {"title": "Inscryption", "release_date": "2021", "product_id": "1092790"}, {"title": "No Man's Sky", "release_date": "2016", "product_id": "275850"}],
    "fear": [{"title": "Resident Evil 7", "release_date": "2017", "product_id": "418370"}, {"title": "Outlast", "release_date": "2013", "product_id": "238320"}, {"title": "Amnesia: The Dark Descent", "release_date": "2010", "product_id": "57300"}, {"title": "Phasmophobia", "release_date": "2020", "product_id": "739630"}, {"title": "Alien: Isolation", "release_date": "2014", "product_id": "214490"}, {"title": "Dead Space", "release_date": "2008", "product_id": "17470"}, {"title": "The Forest", "release_date": "2018", "product_id": "242760"}, {"title": "SOMA", "release_date": "2015", "product_id": "282140"}],
    "disgust": [{"title": "Scorn", "release_date": "2022", "product_id": "698670"}, {"title": "The Binding of Isaac", "release_date": "2011", "product_id": "113200"}, {"title": "DOOM", "release_date": "2016", "product_id": "379720"}, {"title": "Inside", "release_date": "2016", "product_id": "304430"}, {"title": "Agony", "release_date": "2018", "product_id": "487720"}, {"title": "Left 4 Dead 2", "release_date": "2009", "product_id": "550"}, {"title": "Darkest Dungeon", "release_date": "2016", "product_id": "262060"}, {"title": "Dead by Daylight", "release_date": "2016", "product_id": "381210"}]
}

# =========================================
# 2. LOAD DATA
# =========================================
print("\n--- INITIALIZING CORE ENGINE ---")

user_game_df = None
id_to_name = {}
id_to_tags = {}
id_to_date = {} 
internal_to_steam = {} 
steam_to_internal = {}

try:
    if os.path.exists(MATRIX_PATH):
        with open(MATRIX_PATH, 'rb') as f:
            user_game_df = pickle.load(f)
        print(f"✅ Matrix Loaded. Shape: {user_game_df.shape}")
except Exception as e: 
    print(f"❌ Matrix Load Error: {e}")

try:
    if os.path.exists(NAMES_PATH):
        with open(NAMES_PATH, 'rb') as f:
            id_to_name = pickle.load(f)
except Exception as e: pass

try:
    if os.path.exists(USER_MAP_PATH):
        u_df = pd.read_csv(USER_MAP_PATH, header=None, names=['internal_id', 'steam_id'], dtype=str)
        u_df = u_df.dropna(how='any') 
        for _, row in u_df.iterrows():
            try:
                s_id = str(row['steam_id']).split('.')[0].strip()
                i_id = int(float(row['internal_id']))
                internal_to_steam[i_id] = s_id
                steam_to_internal[s_id] = i_id
            except: continue
except Exception as e: pass

try:
    if CSV_PATH:
        df = pd.read_csv(CSV_PATH, dtype=str)
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        rename_map = {'appid': 'id', 'app_id': 'id', 'name': 'title', 'genres': 'tags', 'release_date': 'date', 'releasedate': 'date'}
        df = df.rename(columns=rename_map)
        df = df.loc[:, ~df.columns.duplicated()]
        if 'id' in df.columns:
            df = df.dropna(subset=['id'])
            if 'tags' not in df.columns: df['tags'] = ""
            if 'date' not in df.columns: df['date'] = "Unknown"
            df['tags'] = df['tags'].fillna("")
            df['date'] = df['date'].fillna("Unknown")
            def safe_id(x):
                try: return int(float(str(x)))
                except: return 0
            id_to_tags = pd.Series(df['tags'].values, index=df['id'].apply(safe_id)).to_dict()
            id_to_date = pd.Series(df['date'].values, index=df['id'].apply(safe_id)).to_dict()
except Exception as e: pass

# =========================================
# 3. HELPER FUNCTIONS
# =========================================
def get_emotion(request_json):
    try:
        response = rq.post(EMOTION_URL, json=request_json, timeout=2)
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

# NEW: Fetch a valid ID from the matrix
def get_valid_matrix_id():
    try:
        if user_game_df is not None and not user_game_df.empty:
            valid_ids = user_game_df.index.tolist()
            chosen_id = random.choice(valid_ids)
            print(f"🔑 Generated New User ID from Matrix: {chosen_id}")
            return str(chosen_id)
    except Exception as e:
        print(f"Warning grabbing valid ID: {e}")
        pass
    # Fallback if matrix fails to load
    return str(random.randint(10000, 99999))

# =========================================
# 4. CORE COLLABORATIVE LOGIC
# =========================================
def get_recommendations(request_json, identifier, is_user=True):
    emotion = get_emotion(request_json)
    print(f"\n--- REQUEST: User={identifier} | Emotion={emotion} ---")
    
    target_tags = EMOTION_TAG_MAP.get(emotion, EMOTION_TAG_MAP["neutral"])
    recommendations = []
    
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

    # =========================================
    # NEW USER LOGIC (Fallback)
    # =========================================
    if matrix_id is None:
        print(f"DEBUG: User '{identifier}' is NEW. Falling back to Emotion-based general recommendations.")
        for pid, g_name in id_to_name.items():
            g_tags = id_to_tags.get(pid, "")
            g_date = id_to_date.get(pid, "Unknown Date")
            if check_tags_match(g_tags, target_tags) or emotion == "neutral":
                recommendations.append({"title": g_name, "release_date": g_date, "product_id": pid})
            if len(recommendations) >= 8: break
                
        if len(recommendations) == 0:
            print(f"⚠️ Warning: Dataset empty. Injecting Emergency Fallback Games for '{emotion}'!")
            recommendations = EMERGENCY_BACKUP_GAMES.get(emotion, EMERGENCY_BACKUP_GAMES["neutral"])
        return {'games': recommendations, 'status': f"New user {identifier} accepted.", 'emotion': emotion}

    # =========================================
    # EXISTING USER LOGIC (Matrix Factorization)
    # =========================================
    print(f"✅ SUCCESS: User '{identifier}' FOUND in Matrix! Running Collaborative Filtering...")
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
                
                candidates = list(final_scores.sort_values(ascending=False).items())
                
                for pid, score in candidates:
                    if pid not in played_games:
                        pid_int = int(pid)
                        g_name = id_to_name.get(pid_int, f"Unknown Game ({pid})")
                        g_tags = id_to_tags.get(pid_int, "")
                        g_date = id_to_date.get(pid_int, "Unknown Date")
                        
                        is_match = False
                        
                        # THE FIX: We NO LONGER allow blank tags to pass unless emotion is neutral! 
                        if emotion == "neutral": 
                            is_match = True 
                        elif g_tags and check_tags_match(g_tags, target_tags): 
                            is_match = True
                        
                        if is_match:
                            # Verify we are not adding duplicates
                            if not any(r['product_id'] == pid for r in recommendations):
                                recommendations.append({"title": g_name, "release_date": g_date, "product_id": pid})
                                
                        if len(recommendations) >= 8: break
                        
    except Exception as e:
        print(f"❌ Matrix Calc Error: {e}")
        traceback.print_exc()

    # ========================================================
    # ABSOLUTE FAILSAFE: NEVER RETURN AN EMPTY TABLE
    # ========================================================
    if len(recommendations) < 8:
        print(f"⚠️ Only found {len(recommendations)} matches. Filling rest with Emergency Fallback Games for '{emotion}'!")
        backup = EMERGENCY_BACKUP_GAMES.get(emotion, EMERGENCY_BACKUP_GAMES["neutral"])
        
        # Add backup games until we have 8
        for bg in backup:
            if len(recommendations) >= 8: break
            # Ensure we don't add duplicates
            if not any(r['title'] == bg['title'] for r in recommendations):
                recommendations.append(bg)
                
    return {
        'games': recommendations,
        'emotion': emotion,
        'status': "Success"
    }