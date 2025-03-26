import pandas as pd
import joblib
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

# Logging setup
logging.basicConfig(
    filename="ml_training.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load dataset from an Excel file
try:
    data = pd.read_excel("aadhar_data.xlsx")  # Ensure the file exists
except FileNotFoundError:
    logging.error("Training data file not found.")
    raise SystemExit("Error: training_data.xlsx not found.")

# Ensure the required columns exist
required_columns = {"text", "label"}
if not required_columns.issubset(data.columns):
    logging.error("Missing required columns in the dataset.")
    raise ValueError("Error: Dataset must contain 'text' and 'label' columns.")

# Convert all text inputs to strings (Fix for datetime issue)
data["text"] = data["text"].astype(str)  # ✅ Convert to string
data["label"] = data["label"].astype(str)  # (Optional: Ensure labels are strings)

# Drop missing values
data.dropna(inplace=True)

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data["text"], data["label"], test_size=0.2, random_state=42)

# Create a text classification pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),   # Convert text into numerical form
    ('clf', MultinomialNB())        # Train a Naïve Bayes model
])

# Train the model
pipeline.fit(X_train, y_train)

# ✅ Compute accuracy
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2%}")  # Prints accuracy in percentage format

# Save the trained model
joblib.dump(pipeline, "aadhar_classifier.pkl")
print("✅ Model training complete. Saved as 'aadhar_classifier.pkl'.")
