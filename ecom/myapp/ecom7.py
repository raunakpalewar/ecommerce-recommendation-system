import numpy as np
import pandas as pd
import seaborn as snb
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
import json

csv_file_path = os.path.join(os.path.dirname(__file__), '../flipkart1.csv')
df = pd.read_csv(csv_file_path)

numerical_columns = ['average_rating', 'selling_price']
categorical_columns = ['brand', 'category', 'discount', 'seller', 'sub_category', 'title']

# Create a numerical transformer
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),  # You can change the imputation strategy as needed
    ('scaler', StandardScaler())
])

# Create a categorical transformer
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),  # You can change the imputation strategy as needed
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers using ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_columns),
        ('cat', categorical_transformer, categorical_columns),
    ]
)



# def get_recommendations(item_id):
#     idx = df[df['pid'] == item_id].index[0]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:11]
#     item_indices = [i[0] for i in sim_scores]
#     recommended_items = df.iloc[item_indices]
#     return recommended_items

# Fit and transform the data with the pipeline


def get_recommendations(item_id):
    # Check if the item_id exists in the dataframe
    if df[df['pid'] == item_id].empty:
        return pd.DataFrame()  # Return an empty DataFrame

    # Get the index of the item_id
    idx = df[df['pid'] == item_id].index[0]
  

    # Compute the cosine similarity matrix for the sample

    # Get item-based recommendations based on the index
    # sim_scores = list(enumerate([idx]))
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # sim_scores = sim_scores[1:11]
    # item_indices = [i[0] for i in sim_scores]
    # recommended_items = df.iloc[item_indices]
    item = df[df['pid'] == item_id].iloc[0]

    filtered_df = df[df['pid'] != item_id]

    similarity_scores = filtered_df.apply(lambda x: np.sum(x == item), axis=1)

    # Get indices of top similar items
    top_indices = similarity_scores.sort_values(ascending=False).head(2).index

    # Get the recommended items from the DataFrame
    recommended_items = df.iloc[top_indices]

    return recommended_items


# # Example: Get recommendations for an item with pid 'example_pid'
# example_pid = 'TKPFCZ9EHFCY5Z4Y'  # Replace with a valid item ID
# recommendations = get_recommendations(example_pid)
# print(recommendations)


def get_recommendations_by_inputs(rating=None, brand=None, category=None, discount=None, seller=None, selling_price=None, subcategory=None):
    global df
    # Convert relevant columns to float type
    numeric_columns = ['average_rating', 'selling_price']
    df[numeric_columns] = df[numeric_columns].astype(float)

    # Filter the DataFrame based on input values
    filtered_df = df.copy()
    if rating is not None:
        filtered_df = filtered_df[filtered_df['average_rating'] >= float(rating)]
    if brand is not None:
        filtered_df = filtered_df[filtered_df['brand'] == brand]
    if category is not None:
        filtered_df = filtered_df[filtered_df['category'] == category]
    if discount is not None:
        filtered_df = filtered_df[filtered_df['discount'] == discount]
    if seller is not None:
        filtered_df = filtered_df[filtered_df['seller'] == seller]
    if selling_price is not None:
        filtered_df = filtered_df[filtered_df['selling_price'] <= float(selling_price)]
    if subcategory is not None:
        filtered_df = filtered_df[filtered_df['sub_category'] == subcategory]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame

    # Reset the index of the filtered DataFrame
    filtered_df = filtered_df.reset_index(drop=True)

    # Define numerical columns
    numerical_columns = ['average_rating', 'selling_price']

    # Filter out non-numeric columns
    filtered_columns = numerical_columns + ['brand', 'category', 'discount', 'seller', 'sub_category', 'title']

    # Remove columns that are not in the DataFrame
    filtered_columns = [col for col in filtered_columns if col in filtered_df.columns]

    # Combine transformers using ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_columns),
            ('cat', categorical_transformer, filtered_columns),
        ]
    )

    # Fit and transform the data with the pipeline
    X_filtered = preprocessor.fit_transform(filtered_df[filtered_columns])

    # Compute the cosine similarity matrix for the sample
    cosine_sim_sample = cosine_similarity(X_filtered, X_filtered)

    # Generate recommendations based on the cosine similarity matrix
    idx = 0  # Using index 0 assuming filtered_df is not empty
    sim_scores = list(enumerate(cosine_sim_sample[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    item_indices = [i[0] for i in sim_scores]
    recommendations = filtered_df.iloc[item_indices]
    


    return recommendations
