import pandas as pd
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load dataset (Ensure "inter_data.xlsx" exists)
dataset_path = "inter_data.xlsx"

try:
    df = pd.read_excel(dataset_path)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Dataset file '{dataset_path}' not found. Please provide the correct file.")

# Ensure necessary columns exist
if "text" not in df.columns or "attribute" not in df.columns:
    raise ValueError("❌ Dataset must contain 'text' and 'attribute' columns.")

# Text preprocessing function
def clean_text(text):
    """Removes extra spaces, new lines, and unnecessary characters."""
    text = re.sub(r'\n+', ' ', text)  # Remove newlines
    text = re.sub(r'\s{2,}', ' ', text)  # Remove extra spaces
    return text.strip()

# Apply text cleaning
df["text"] = df["text"].astype(str).apply(clean_text)

# Splitting dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["attribute"], test_size=0.2, random_state=42
)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train ML Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_vec, y_train)

# Save the trained model and vectorizer
joblib.dump(model, "inter_classifier.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

# Evaluate Model
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained successfully with accuracy: {accuracy:.2f}")
