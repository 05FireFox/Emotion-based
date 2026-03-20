import ast
import pandas as pd

# Reading all the recommended games result
finalResults = pd.read_csv('finalResults.csv')

# Reading the detected emotion predicted by DeepFace
wordFile = open('detectedEmotion.txt', 'r')
emotion = wordFile.read()
wordFile.close()

# Mapping of the topic to the emotions
emotionToTopic = {
    'neutral': 0,
    'happy': 5,
    'fear': 2,
    'angry': 6,
    'sad': 3,
    'disgust': 4,
    'surprise': 1
}

# Mapping of the topic to different genres
topicToGenre = {
    0: 'Simulation/Strategy',
    1: 'Casual/Family',
    2: 'Horror/Action',
    3: 'Visual Novel/Adventure',
    4: 'Strategy/Turn-Based',
    5: 'Platformer/Puzzle',
    6: 'Action/Shooter'
}

# Function to check if the list contains a value
def contains_value(lst, value):
    return value in lst

# Getting the topic linked to the emotion
desiredTopic = emotionToTopic[emotion]

# Check if the list contains the value and return the row
finalResults['topics'] = finalResults['topics'].apply(ast.literal_eval)
filteredResult = finalResults['topics'].apply(lambda x: contains_value(x, desiredTopic))

# Filtering the emotion based games
recommendation = finalResults[filteredResult]

print(f"The {topicToGenre[desiredTopic]} genre recommended games based on the {emotion} emotion is:\n")
print(recommendation[:10]['title'].to_string(index=False, header=False))