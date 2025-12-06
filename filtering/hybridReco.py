import pandas as pd
import gensim
import sys
import os
import ast
import math
import numpy as np
import pickle

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.corpora import Dictionary
import nltk
from nltk.stem import WordNetLemmatizer, SnowballStemmer

# Import your other modules
try:
    from contentBasedFiltering import recommendation as content
    from collaborativeFiltering import recommendation as colloborative
except ImportError:
    print("CRITICAL WARNING: Filtering modules not found. Ensure contentBasedFiltering.py and collaborativeFiltering.py exist.")
    def content(id): return []
    def colloborative(id): return []

# Initialize NLTK
np.random.seed(2018)
try:
    nltk.download('omw-1.4', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

# Get current script directory to use relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# PART 1: LOAD DATASETS (FIXED PATHS)
# ==========================================

def clean_id_to_string(value):
    """Ensures IDs are clean strings (removes .0 from floats)"""
    try:
        if pd.isna(value): return "0"
        str_val = str(value)
        if str_val.endswith('.0'):
            return str_val[:-2]
        return str_val
    except:
        return "0"

def load_games_dataset():
    """Finds the steam_games file dynamically with robust path checking"""
    print("DEBUG: hybridReco is looking for steam_games.csv...")
    
    # 1. KNOWN ABSOLUTE PATH (From your logs)
    abs_path = r'C:\Users\Praneet\project\dataset\steam_games.csv'
    
    # 2. List of paths to try
    paths_to_try = [
        abs_path,                                     # Absolute path
        os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'), # Inside current folder/dataset
        os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'), # One level up
        'dataset/steam_games.csv'                     # Simple relative
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            print(f"DEBUG: Found games file at: {path}")
            return path, path.endswith('.jl')
            
    print("CRITICAL ERROR: steam_games.csv NOT FOUND in hybridReco!")
    return None, False

game_path, is_json = load_games_dataset()

if game_path:
    if is_json:
        games = pd.read_json(game_path, lines=True, encoding='utf-8')
    else:
        # Load all columns as strings initially to be safe
        games = pd.read_csv(game_path, dtype=str)
        
    # Standardize Column Names
    cols = games.columns
    if 'AppID' in cols: games = games.rename(columns={'AppID': 'id', 'Name': 'title', 'Tags': 'tags'})
    elif 'app_id' in cols: games = games.rename(columns={'app_id': 'id', 'title': 'title', 'genres': 'tags'})
    
    # Standardize IDs to String immediately
    if 'id' in games.columns:
        games['id'] = games['id'].apply(clean_id_to_string)
else:
    # Create empty dataframe if file missing to prevent immediate crash (though logic will fail later)
    games = pd.DataFrame(columns=['id', 'title', 'tags'])

# ==========================================
# PART 1.5: ID MAPPING HELPER
# ==========================================

def get_steam_id_from_map(input_id):
    """
    Maps Internal ID (0, 1) -> Steam ID (7656...)
    """
    input_str = clean_id_to_string(input_id)
    
    # Try finding user_list.csv in common locations
    possible_map_paths = [
        os.path.join(BASE_DIR, 'filtering', 'user_list.csv'),
        os.path.join(BASE_DIR, 'user_list.csv'),
        r'C:\Users\Praneet\project\filtering\user_list.csv'
    ]
    
    map_path = None
    for path in possible_map_paths:
        if os.path.exists(path):
            map_path = path
            break

    if not map_path:
        print("Warning: user_list.csv not found. Using ID as-is.")
        return input_str

    try:
        # Load as STRING
        user_map = pd.read_csv(map_path, header=None, names=['internal_id', 'steam_id'], dtype=str)
        
        user_map['internal_id'] = user_map['internal_id'].apply(clean_id_to_string)
        user_map['steam_id'] = user_map['steam_id'].apply(clean_id_to_string)
        
        # 1. Check if input is an Internal ID
        match_internal = user_map[user_map['internal_id'] == input_str]
        if not match_internal.empty:
            found = match_internal.iloc[0]['steam_id']
            print(f"DEBUG: Mapped Internal ID {input_str} -> Steam ID {found}")
            return found
            
        # 2. Check if input is ALREADY a Steam ID
        match_steam = user_map[user_map['steam_id'] == input_str]
        if not match_steam.empty:
            print(f"DEBUG: ID {input_str} recognized as valid Steam ID.")
            return input_str

        print(f"DEBUG: User {input_str} not found in map. Passing as-is.")
        return input_str
            
    except Exception as e:
        print(f"Mapping Error: {e}")
        return input_str

# ==========================================
# PART 2: HYBRID LOGIC
# ==========================================

def hybrid_weight(colla_list, content_list):
    """
    Merges results from Content and Collaborative filtering.
    """
    df_colla = pd.DataFrame(colla_list, columns=['product_id', 'similarity']) if colla_list else pd.DataFrame()
    df_content = pd.DataFrame(content_list, columns=['product_id', 'similarity']) if content_list else pd.DataFrame()

    # Ensure IDs are strings
    if not df_colla.empty: df_colla['product_id'] = df_colla['product_id'].astype(str)
    if not df_content.empty: df_content['product_id'] = df_content['product_id'].astype(str)

    if not df_colla.empty and not df_content.empty:
        # Merge
        joined_results = df_colla.merge(df_content, on='product_id', how='inner')
        # Weighted Average Formula (80% Content, 20% Collab)
        joined_results['weighted_avg'] = (joined_results['similarity_x'] * 0.2) + (joined_results['similarity_y'] * 0.8)
        joined_results = joined_results[['product_id', 'weighted_avg']]
        
    elif not df_colla.empty:
        joined_results = df_colla.copy()
        joined_results['weighted_avg'] = joined_results['similarity'] 
        
    elif not df_content.empty:
        joined_results = df_content.copy()
        joined_results['weighted_avg'] = joined_results['similarity'] 
        
    else:
        joined_results = pd.DataFrame(columns=['product_id', 'weighted_avg'])

    return joined_results

# ==========================================
# PART 3: NLP & TOPIC MODELING HELPERS
# ==========================================

def lemmatize_and_stem(word):
    stemmer = SnowballStemmer(language='english')
    return stemmer.stem(WordNetLemmatizer().lemmatize(word, pos='v'))

def preprocess_text(text):
    try:
        if isinstance(text, str) and text.startswith('['):
            try:
                text = ast.literal_eval(text)
                text = ' '.join(text)
            except: pass 
        
        if isinstance(text, list):
            text = ' '.join(text)

        result_tag = []
        for token in gensim.utils.simple_preprocess(str(text)):
            if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
                result_tag.append(lemmatize_and_stem(token))
        return result_tag 
    except ValueError:
        return []

# Load LDA Model Safely
dictionary = Dictionary()
lda_model = None

dict_path = os.path.join(BASE_DIR, 'lda_dict.dict')
model_path = os.path.join(BASE_DIR, 'lda_model.pkl')

try:
    if os.path.exists(dict_path) and os.path.exists(model_path):
        dictionary = Dictionary.load(dict_path)
        with open(model_path, "rb") as f:
            lda_model = pickle.load(f)
except Exception as e:
    print(f"Warning: LDA model could not be loaded ({e}). Topics will be skipped.")

def map_tags_to_topics(unseen_game_tag):
    if lda_model is None or pd.isna(unseen_game_tag):
        return []
        
    try:
        bow_vector = dictionary.doc2bow(preprocess_text(unseen_game_tag))
        topics_list = list()
        for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
            topics_list.append(index)
        return topics_list
    except:
        return []

# ==========================================
# PART 4: MAIN FUNCTION
# ==========================================

def recommendation(user_id):
    # 1. Normalize ID and Map
    mapped_user_id = get_steam_id_from_map(user_id)
    
    # 2. Get Recommendations
    content_list = content(mapped_user_id) 
    colla_list = colloborative(mapped_user_id)

    # 3. Hybrid Merge
    final_results = hybrid_weight(colla_list, content_list)
    
    if final_results.empty:
        return pd.DataFrame()

    if 'weighted_avg' not in final_results.columns:
         final_results.rename(columns={'similarity': 'weighted_avg'}, inplace=True)

    # 4. Sort
    final_results = final_results.sort_values(by='weighted_avg', ascending=False)[['product_id', 'weighted_avg']]
    
    # Force String ID for final metadata merge
    final_results['product_id'] = final_results['product_id'].astype(str)
    
    # 5. Attach Game Details (Title, Tags)
    # This was the step failing before! Now that 'games' is loaded, this will work.
    if not games.empty:
        final_results = final_results.merge(games, left_on='product_id', right_on='id', how='inner')
    
    cols = ['product_id', 'weighted_avg', 'title']
    if 'tags' in final_results.columns:
        cols.append('tags')
    
    # Ensure columns exist before filtering
    existing_cols = [c for c in cols if c in final_results.columns]
    final_results = final_results[existing_cols]

    # 6. Add LDA Topics (Optional)
    if 'tags' in final_results.columns and lda_model is not None:
        final_results['topics'] = final_results.apply(lambda x: map_tags_to_topics(x.get('tags', '')), axis=1)
    else:
        final_results['topics'] = [[] for _ in range(len(final_results))]

    return final_results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        random_user = sys.argv[1]
        result = recommendation(random_user)
        print(result)