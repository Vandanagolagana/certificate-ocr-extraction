import pandas as pd
import joblib
import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Expanded dataset with more variations
data = [
    ("John Doe S/O Richard", "name"),
    ("Jane Smith S/O Michael", "name"),
    ("Robert Brown S/O David", "name"),
    ("S/O Richard 221B Baker Street, London", "address"),
    ("S/O Michael 7th Avenue, New York", "address"),
    ("Lives at 5th Street, California, USA", "address"),
    ("DOB: 15/08/1998", "dob"),
    ("DOB: 21/05/1995", "dob"),
    ("Date of Birth: 30-12-2000", "dob"),
    ("Gender: Male", "gender"),
    ("Female", "gender"),
    ("Male", "gender"),
    ("1234 5678 9101", "aadhar number"),
    ("5678 9101 1234", "aadhar number"),
    ("9876 5432 1001", "aadhar number"),
]

# Duplicate and shuffle to increase dataset size
data = data * 10  # Increase data by duplicating
random.shuffle(data)

# Convert to DataFrame
df = pd.DataFrame(data, columns=["text", "label"])

# Stratified train-test split
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42)

# Feature extraction
vectorizer = TfidfVectorizer()

# Train Random Forest Model
model = make_pipeline(vectorizer, RandomForestClassifier(n_estimators=200, random_state=42))
model.fit(X_train, y_train)

# Evaluate accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2f}")

# Save trained model
joblib.dump(model, "attribute_classifier.pkl")
print("🎉 Model saved as 'attribute_classifier.pkl'")
