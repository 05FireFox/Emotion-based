🎮 Emotion Sense: Game Recommender<div align="center">An intelligent web application that suggests video games based on your real-time facial emotion and gaming history.View Demo • Report Bug • Request Feature</div>📖 OverviewEmotion Sense is a full-stack recommendation engine that bridges Computer Vision and Collaborative Filtering. Unlike standard recommenders that only look at past history, this system analyzes the user's current emotional state via a live webcam feed to suggest games that fit their mood (e.g., suggesting high-energy action games for "Neutral" moods or calming atmospheric games for "Sad" moods).This project demonstrates proficiency in Full Stack Development, Data Science, and interactive UI design.✨ Key Features😐 Real-Time Emotion Detection: Captures user facial expressions via webcam and classifies emotions (Happy, Sad, Angry, Neutral, etc.).🤖 Hybrid Recommendation Engine: Combines User-Item Matrix Factorization (Collaborative Filtering) with emotion-based tag filtering.🎨 Glassmorphism UI: A modern, dark-themed interface built with Material UI and Framer Motion for smooth transitions.🌌 3D Interactive Backgrounds: Implements Three.js (@react-three/fiber) for immersive particle and starfield effects.📸 Smart Capture Interface: Includes a visual face-guide overlay to ensure optimal image capture for the ML model.🛠️ Tech StackDomainTechnologies UsedFrontendReact.js, Material UI (MUI), Framer Motion, React Webcam, Three.js (Fiber/Drei)BackendPython, Flask (API), Pandas, NumPyMachine LearningScikit-learn (Matrix Factorization), OpenCV (Face Detection), Pickle (Model Serialization)DataSteam Games Dataset, TMDB (Conceptually similar to my Movie Recommender project)🚀 Installation & SetupFollow these steps to run the project locally.PrerequisitesNode.js (v14+)Python (v3.8+)1. Clone the RepositoryBashgit clone https://github.com/YourUsername/emotion-sense.git
cd emotion-sense
2. Backend SetupNavigate to the server directory and install Python dependencies.Bashcd backend
pip install -r requirements.txt
python app.py
The backend server typically runs on http://localhost:5000 (or similar).3. Frontend SetupNavigate to the root directory (where package.json is located).Bashnpm install
npm start
The React app will launch on http://localhost:3000.🧠 How It WorksInput: The user enters their unique User ID or Steam ID.Capture: The user takes a photo using the integrated webcam interface.Processing:The image is sent to the Python backend.The Emotion Recognition Model detects the facial expression.The Recommendation Engine (recommendation.py) looks up the user's history in the user_game_matrix.pkl.Filtering: The engine finds similar users (Collaborative Filtering) but filters the results to match game genres mapped to the detected emotion (e.g., Happy → Adventure/Racing).Output: A curated list of games is displayed with Title, Release Date, and Store IDs.📂 Project StructureBashemotion-sense/
├── public/
├── src/
│   ├── components/
│   │   ├── AfterCapture.js       # Image review & retake logic
│   │   ├── Background3D.js       # Three.js particle system
│   │   ├── BeforeCapture.js      # Webcam feed with face guide overlay
│   │   ├── EmotionCard.js        # Displays detected emotion
│   │   ├── IdentifierInput.js    # User ID input form
│   │   └── TableGames.js         # Results table
│   ├── App.js                    # Main routing and theme setup
│   ├── Main.js                   # Dashboard layout
│   └── recommendation.py         # ML Logic (Matrix Factorization)
└── README.md
👨‍💻 AuthorVankara Jishnu Kali PraneetRole: B.Tech Computer Science Student (2026)Focus: AI/ML, Data Structures, Full Stack DevelopmentResume Highlights: * Foundations of AI Internship (Microsoft Initiative | Edunet)Movie Recommender System Project (Streamlit + Scikit-learn)