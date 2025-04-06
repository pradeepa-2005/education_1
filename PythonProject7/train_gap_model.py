import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

db_path = 'education.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_activity';")
if not cursor.fetchone():
    print("❌ student_activity table does not exist.")
    exit()

df = pd.read_sql_query("SELECT * FROM student_activity", conn)
conn.close()

if df.empty:
    print("❌ No data found in student_activity table.")
    exit()

if df['difficulty'].dtype != 'object':
    df['difficulty'] = df['difficulty'].astype(str)

difficulty_encoder = LabelEncoder()
df['difficulty_encoded'] = difficulty_encoder.fit_transform(df['difficulty'])

df['learning_gap'] = df['score'].apply(lambda x: 1 if x == 0 else 0)

X = df[['score', 'time_spent', 'attempts', 'correct_attempts', 'difficulty_encoded']]
y = df['learning_gap']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("✅ Model trained successfully!")
print("🔍 Classification Report:\n", classification_report(y_test, y_pred))
print("🎯 Accuracy Score:", accuracy_score(y_test, y_pred))

joblib.dump(model, 'learning_gap_model.pkl')
joblib.dump(difficulty_encoder, 'difficulty_encoder.pkl')
print("💾 Model and encoder saved as learning_gap_model.pkl and difficulty_encoder.pkl")