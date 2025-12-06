# DataScientistS3

## Problem Statement and Objectives

The objective of this project is to develop a hybrid filtering method that can provide personalized game recommendations to players based on their current mood. Traditional filtering methods, such as content-based and collaborative-based filtering, are commonly used for game recommendations. However, these methods do not take into account the player's mood, which can greatly influence their gaming preferences. <br />
Therefore, the research aims to investigate the use of mood-based filtering, in addition to the existing methods to form a hybrid model, to provide more personalized game recommendations. This will require the development of a mood-based filtering algorithm that can accurately identify a player's current mood and match it with the most suitable game recommendations. <br />
The study will also evaluate the effectiveness of the hybrid system by comparing its performance with the traditional content-based and collaborative-based filtering methods. The evaluation will be conducted using real game data scraped from Steam, and the results will be used to determine the accuracy and effectiveness of the hybrid system. <br />
In addition, we will analyze the dataset on how popular genres, pricing, recommended and most reviewed games can be utilized for personalized game recommendations. This analysis will help to identify the key factors that influence a player's game selection and preferences, and how these can be incorporated to better decision-making. Overall, the main objective of this research is to develop a more accurate and effective game recommendation system that can provide personalized recommendations to players based on their current mood and other key factors.

<br />

## How To Run Game Recommendation Application
### Local Deployment
#### Pre-requisites
1. Download and install [Python](https://www.python.org/downloads/) (>=3.9)
2. Download and install [Docker](https://www.docker.com/products/docker-desktop/)
3. Download and install [Node.js](https://nodejs.org/en/download) (used for NPM for deploying react application)
4. Download the datasets required for the project
	```sh
	mkdir -p dataset
	curl -L https://storage.googleapis.com/733_dataset/games.jl -o dataset/games.jl
	curl -L https://storage.googleapis.com/733_dataset/reviews.jl -o dataset/reviews.jl
	```
5. Create a python virtual environment and install required dependencies
	```sh
	# Create a virtual environment (we are naming it 'virtual_env')
	python3 -m venv virtual_env

	# Active the created virtual environment
	source virtual_env/bin/activate

	# Install the required dependencies
	pip install -r filtering/requirements.txt
	```

#### Steps
1. Deploy and run the emotion Detection Web API in docker container. This is exposed via a docker as the library used (deepfake) might not work in some workstations.
	```sh
	# build a docker image 
	docker build -t emotion emotionDetection

	# run the built docker image
	docker run -dp 8081:8080 emotion
	```

2. Now run the recommendation web API
	```sh
	# Get into the filtering codebase
	cd filtering

	# Run the flask application with host as 'localhost' and port as '8082'
	flask run -h localhost -p 8082
	```
	> Note: If you change either the host or port, please change the URL in frontend/src/Main.js (at line 42)

3. Run the frontend web application
	```sh
	# Open another terimanl in the project parent directory
	# Get into the frontend codebase
	cd frontend

	# Run the Node server
	npm start
	```

4. Open the application by accessing the URL http://localhost:3000 

### Cloud Deployment
#### Pre-requisites
1. Download and install [Python](https://www.python.org/downloads/) (>=3.9)
2. Download and install [Docker](https://www.docker.com/products/docker-desktop/)
3. Download and install [Node.js](https://nodejs.org/en/download) (used for NPM for deploying react application)
4. Download the datasets required for the project
	```sh
	mkdir -p dataset
	curl -L https://storage.googleapis.com/733_dataset/games.jl -o dataset/games.jl
	curl -L https://storage.googleapis.com/733_dataset/reviews.jl -o dataset/reviews.jl
	```
5. Download and install [gcloud CLI](https://cloud.google.com/sdk/docs/install)
6. Create a repository in Artifact Registry for docker images in GCP (can be either be done via cnsole or CLI) - [docs](https://cloud.google.com/artifact-registry/docs/repositories/create-repos#docker)

#### Steps

0. Step zero
	1. Make sure you are authenticated to use gcloud CLI with either your user or IAM user (with required permission).
	2. checkout to _'main-cloud'_ branch (The cloud deployment has few code changes to adapt to the docker environment)
1. Build and push docker image of the recommendation web API
	```sh
	gcloud builds submit \
	--tag <region_name>-docker.pkg.dev/<project_name>/<artifactory_repo_name>/recommendation filtering/
	```
2. Deploy the recommendation via [Google Cloud Run](https://cloud.google.com/run/) via CLI using the below command on in [console UI](https://cloud.google.com/run/docs/deploying#console)
	```sh
	gcloud run deploy recommendation --image <region_name>-docker.pkg.dev/<project_name>/<artifactory_repo_name>/recommendation
	```
	> Note: Recommend using Console UI to deploy with _'8 GB RAM'_ and _'2 vCPU'_. Also sepcify 1 minimum instance to avoid cold starts.
3. Update the web API URL (from the Google Cloud Run console) in the frontend code at frontend/src/Main.js (at line 42)
4. Build and push docker image of the frontend web application
	```sh
	gcloud builds submit \
	--tag <region_name>-docker.pkg.dev/<project_name>/<artifactory_repo_name>/frontend frontend/
	```
5. Deploy the recommendation via [Google Cloud Run](https://cloud.google.com/run/) via CLI using the below command on in [console UI](https://cloud.google.com/run/docs/deploying#console)
	```sh
	gcloud run deploy recommendation --image <region_name>-docker.pkg.dev/<project_name>/<artifactory_repo_name>/frontend
	```
6. Open the URL provided in the Google Cloud Run console to access the webpage.

> Note: The first request would involve major delay due to 2 reason: <br />
	1. Google Cloud Run is a serverless architecture and will not have server always running and so required around half a minute for server bootup and initalization. <br />
	2. The web API code (recommendation) involves downloading few datasets from library as part of first time initialization. And also as the cloud run does not contain GPU, it will also lead to delay<br />
	**The processing time will speed up from consecutive requests.**

<br />

## How to test the filtering models (ROC Graphs)

1. Move inside testing directory
2. Run collaborativeTesting.ipynb
3. Run contentBasedTesting.ipynb
    > Note: Do run this code on a GPU intensive system as it takes more time to generate sensitivity and 1-specificity values. The correctness of the system can be tested by changing list_of_users to list_of_users[:100] in cell 3
4. Run hybridTesting.ipynb
5. Run combinedPlotting.ipynb for getting the combined graphs
6. The users in user_list.csv file can be used for testing
    > Note: For content-based filtering: Some users might return empty dataframe for recommendations as we are filtering games based on the criteria of the number of reviews.
    For collaborative filtering: Some users might return empty dataframe for recommendations as given user may not be positively correlated with other users

## Folders and Files:

1. dataAnalysis :
	- analysis.ipynb : Exploratory Data Analysis of the games and review dataset

2. emotionDetection :
	- emotionDeeepFace.py : Web API which when a image is provided returns the emotion from the image.

3. emotionMapping :
	- AgglomerativeClusteringGenre.py : Forming 7 clusters for differnt game genres to map them to 7 different emotions using agglomerative clustering 
	- AgglomerativeClusteringTags.py : Forming 7 clusters for differnt game tags to map them to 7 different emotions using agglomerative clustering 
	- KMeansClusteringTags.py : Forming 7 clusters for differnt game tags to map them to 7 different emotions using k means clustering
    > Note: Different types of clusterings were explored but finally, topic modeling is used in the application

4. filtering :
	- app.py : Web API for exposing existing user hybrid recommendation and new user content based recommendation
	- collaborativeFiltering.py : Collaborative filtering recommendations based on a user_id
	- contentBasedFiltering.py : Content-based recommendations based on a user_id
	- emotion_to_genre.json : ..
	- emotion_to_topic.json : ..
	- hybridReco.py : Hybrid recommedation for a given user_id combining collaborative filtering and content-based filtering
	- lda_dict.dict : LDA dictionary obtained from topic model
	- lda_model.pkl : Saved LDA model
	- newUserReco.py : New user to get recommendations based on the steam id of the game entered
	- recommendations.py : File used to divert path and call between hybrid recommendation for existing user and new user recommendation with steam game id
	- user_list.csv : List of users to be used for 
	testing

5. finalResults :
	- finalResults.py : Reading the detecting emotion and filtering out the hybrid recommendation based on the tags to emotion mapping

6. frontend : The application UI code written in React

7. steam_scraping : Reused code obtained from [github](https://github.com/prncc/steam-scraper).
The code has been modified as per our requirements

8. testing : Testing the filtering models by plotting their ROC graphs

9. topic_modeling :
	- topicModelingLDA.ipynb : Run topicModelingLDA.ipynb to save the LDA dictionary (lda_dict) and LDA model (lda_model). 
    > Note: These files are saved in this directory and not to be used by the current recommender system as new genre-tags clusters 
are generated every time which changes the genre-emotion mapping