import pandas as pd
import sys
import os
import numpy as np

# Import specific modules
try:
    from contentBasedFiltering import recommendation as content
    from collaborativeFiltering import recommendation as collaborative
except ImportError:
    print("Warning: Filtering modules not found.")
    def content(id): return []
    def collaborative(id): return []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. LOAD GAME METADATA (For Titles)
games_df = pd.DataFrame()
try:
    # Use the same path logic as other files
    possible_paths = [
        os.path.join(BASE_DIR, 'dataset', 'steam_games.csv'),
        os.path.join(BASE_DIR, '..', 'dataset', 'steam_games.csv'),
        r'C:\Users\Praneet\project\dataset\steam_games.csv'
    ]
    path = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if path:
        games_df = pd.read_csv(path, dtype=str)
        if 'AppID' in games_df.columns: 
            games_df = games_df.rename(columns={'AppID': 'id', 'Name': 'title', 'Tags': 'tags'})
        elif 'app_id' in games_df.columns:
            games_df = games_df.rename(columns={'app_id': 'id', 'title': 'title', 'genres': 'tags'})
        
        games_df['id'] = games_df['id'].str.replace('.0', '', regex=False)
except:
    pass

# 2. USER MAPPING
def get_steam_id(user_input):
    """Maps Internal ID -> Steam ID using user_list.csv"""
    user_input = str(user_input).split('.')[0]
    
    map_path = os.path.join(BASE_DIR, 'user_list.csv')
    if os.path.exists(map_path):
        try:
            # Load user map: internal_id, steam_id
            df_map = pd.read_csv(map_path, header=None, dtype=str)
            
            # If input is '0', '1' (Internal)
            if user_input.isdigit() and len(user_input) < 10:
                row = df_map[df_map[0] == user_input]
                if not row.empty:
                    return row.iloc[0][1] # Return Steam ID
            
            # If input is already '7656...' (Steam ID)
            # Just verify it exists
            if len(user_input) > 10:
                return user_input
                
        except Exception as e:
            print(f"Map Error: {e}")
            
    return user_input

# 3. HYBRID LOGIC
def recommendation(user_id):
    # Map ID
    steam_id = get_steam_id(user_id)
    print(f"Hybrid: Processing for User {user_id} -> {steam_id}")
    
    # Get Results
    collab_results = collaborative(steam_id) # Returns [[id, score], ...]
    content_results = content(steam_id)      # Returns [[id, score], ...]
    
    # Convert to DataFrames
    df_c = pd.DataFrame(collab_results, columns=['id', 'score']) if collab_results else pd.DataFrame()
    df_t = pd.DataFrame(content_results, columns=['id', 'score']) if content_results else pd.DataFrame()
    
    final_df = pd.DataFrame()

    # Merge Logic
    if not df_c.empty and not df_t.empty:
        merged = pd.merge(df_c, df_t, on='id', how='outer', suffixes=('_c', '_t')).fillna(0)
        # Weighted Avg: 80% Collaborative, 20% Content (Since Collab is usually smarter)
        merged['final_score'] = (merged['score_c'] * 0.8) + (merged['score_t'] * 0.2)
        final_df = merged[['id', 'final_score']]
    elif not df_c.empty:
        final_df = df_c.rename(columns={'score': 'final_score'})
    elif not df_t.empty:
        final_df = df_t.rename(columns={'score': 'final_score'})
        
    if final_df.empty:
        return []

    # Sort & Top 10
    final_df = final_df.sort_values(by='final_score', ascending=False).head(10)
    
    # Attach Titles
    if not games_df.empty:
        final_df = final_df.merge(games_df[['id', 'title', 'tags']], on='id', how='left')
        final_df['title'] = final_df['title'].fillna(final_df['id'])
    else:
        final_df['title'] = final_df['id']
        
    return final_df.to_dict('records')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(recommendation(sys.argv[1]))