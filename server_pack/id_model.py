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
    filename="ml_model.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load dataset from an Excel file
try:
    data = pd.read_excel("id_data.xlsx")  # Ensure the file exists in the working directory
    logging.info("Dataset loaded successfully.")
except FileNotFoundError:
    logging.error("Training data file not found.")
    raise SystemExit("Error: 'id_data.xlsx' not found.")

# Check if required columns exist
required_columns = {"text", "attribute"}
if not required_columns.issubset(data.columns):
    logging.error("Missing required columns in the dataset.")
    raise ValueError("Error: Dataset must contain 'text' and 'attribute' columns.")

# Drop missing values
data.dropna(inplace=True)

# Ensure all text data is converted to string format
data["text"] = data["text"].astype(str)

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data["text"], data["attribute"], test_size=0.2, random_state=42)

# Create a text classification pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),   # Convert text into numerical form
    ('clf', MultinomialNB())        # Train a Naïve Bayes model
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate the model
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100  # Convert to percentage

# Print and log accuracy
print(f"Model Accuracy: {accuracy:.2f}%")
logging.info(f"Model Accuracy: {accuracy:.2f}%")

# Save the model
joblib.dump(pipeline, "id_classifier.pkl")
print("Model training complete and saved as 'id_classifier.pkl'.")
logging.info("Model training complete and saved as 'id_classifier.pkl'.")
