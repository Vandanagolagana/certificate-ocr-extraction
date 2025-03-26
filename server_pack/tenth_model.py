import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Load the dataset from an Excel file
file_path = "tenth_data.xlsx"  # Ensure this file exists in your project directory
df = pd.read_excel(file_path, engine="openpyxl")

# Check if required columns exist
if "text" not in df.columns or "attribute" not in df.columns:
    raise KeyError("The dataset must contain 'text' and 'attribute' columns.")

# Preprocess text: Remove extra spaces and special characters
def clean_text(text):
    return re.sub(r'\W+', ' ', str(text)).strip().lower()

df["text"] = df["text"].astype(str).apply(clean_text)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["attribute"], test_size=0.2, random_state=42)

# Convert text to numerical format using TF-IDF
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train the Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# Predict and calculate accuracy
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the model and vectorizer
joblib.dump(model, "tenth_classifier.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
print("Model and vectorizer saved successfully!")
