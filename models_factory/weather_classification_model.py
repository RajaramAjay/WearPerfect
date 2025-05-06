import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import json

# Load the dataset
df = pd.read_csv('weather_classification_data.csv')

# Separate features (X) and target variable (y)
X = df.drop('Weather Type', axis=1)
y = df['Weather Type']

# Identify numerical and categorical columns
numerical = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical = X.select_dtypes(include=['object']).columns.tolist()

# Pipeline for numerical data transformation
numerical_transformer = Pipeline(steps=[
    ('imputer', KNNImputer()),
    ('scaler', RobustScaler())
])

# Pipeline for categorical data transformation
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformations using ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical),
        ('cat', categorical_transformer, categorical)
    ]
)

# Initialize the model
model = RandomForestClassifier()

# Create a full pipeline integrating preprocessing and model training
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', model)
])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
pipeline.fit(X_train, y_train)

# Save the model to a pickle file
with open('weather_classifier_model.pkl', 'wb') as file:
    pickle.dump(pipeline, file)

# Save column information for future reference
model_info = {
    'numerical_columns': numerical,
    'categorical_columns': categorical,
    'target_column': 'Weather Type'
}

with open('weather_classifier_info.json', 'w') as file:
    json.dump(model_info, file)

print("Model trained and saved as 'weather_classifier_model.pkl'")
print("Model information saved as 'weather_classifier_info.json'")