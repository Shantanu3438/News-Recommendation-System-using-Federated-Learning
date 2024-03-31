import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import json

def createModel():

    # Define your model
    def create_model(input_shape):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(52, activation='relu', input_shape=input_shape),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        return model
    
    model = create_model((52,))
    
    # Check if weights file exists
    weights_file = "/home/shantanu/Projects/News_Recommendation_System/NewsRecommendation/RecommendationModel/model.weights.h5"
    if os.path.exists(weights_file):
        # Load the weights if file exists
        model.load_weights(weights_file)
    else:
        # Initialize the model with random weights
        for layer in model.layers:
            if hasattr(layer, 'kernel_initializer') and callable(layer.kernel_initializer):
                layer.kernel_initializer = tf.keras.initializers.RandomNormal(mean=0.0, stddev=0.05, seed=42)
        
        # Save the initialized weights (optional)
        model.save_weights(weights_file)
    
    return model

global_model = createModel()

def set_global_model(local_weights):
    """
    Update the global model with weights from local models.

    Args:
    - global_model: The global model to be updated.
    - local_weights: List of weights from local models.

    Returns:
    - Updated global model.
    """
    # Use the initial weights of the global model
    global_weights = global_model.get_weights()
    print(np.array(global_weights[4]).shape)
    averaged_weights = [tf.identity(w) for w in global_weights]

    # Average the weights from local models
    for i, local_weight in enumerate(local_weights):
            local_weight_np = np.array(local_weight)
            if i == 4:
                local_weight_np = local_weight_np.reshape((32, 1))
            global_weights[i] = (global_weights[i] + local_weight_np) / 2.0

    # Set the averaged weights to the global model
    global_model.set_weights(averaged_weights)


def extract_global_weight():
    global_weights = global_model.get_weights()
    # Convert the weights to a JSON-serializable format
    serializable_weights = []
    for weight in global_weights:
        serializable_weights.append(weight.tolist())
    return json.dumps(serializable_weights)

def get_recommendation(user_id, article_features):
    # Generate synthetic interaction data for the given user_id
    num_articles = len(article_features)
    user_interaction_data = np.zeros(num_articles)  # No actual interaction data used
    
    # Repeat user_id for all articles
    user_ids = np.array([user_id] * num_articles)

    # Preprocess data (normalize article features)
    scaler = StandardScaler()
    article_features_normalized = scaler.fit_transform(article_features)

    # Concatenate input data
    X = np.concatenate([user_interaction_data.reshape(-1, 1), article_features_normalized, user_ids.reshape(-1, 1)], axis=1)

    # Predict likelihood of interaction for each article
    interaction_probabilities = global_model.predict(X).flatten()

    # Recommend articles based on predicted probabilities
    recommended_articles_indices = np.argsort(interaction_probabilities)[::-1]  # Sort in descending order
    recommended_articles = recommended_articles_indices  # Recommend top 3 articles
    return recommended_articles