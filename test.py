import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsRecommendation.settings')
django.setup()

from Users.models import articles
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from RecommendationModel.model import get_recommendation

def create_article_features(title, description, max_features=50):
    # Concatenate title, description, and content into a single text
    article_text = title + " " + description
    
    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()
    
    # Fit on the concatenated text to build vocabulary
    tfidf_vectorizer.fit([article_text])
    
    # Transform the concatenated text to a TF-IDF feature vector
    tfidf_features = tfidf_vectorizer.transform([article_text]).toarray()
    
    # Determine the actual number of features
    num_features = tfidf_features.shape[1]
    
    # Truncate or pad TF-IDF feature vector to achieve the desired dimensionality
    if num_features < max_features:
        # Pad with zeros if the number of features is lower than max_features
        padded_features = np.pad(tfidf_features, ((0, 0), (0, max_features - num_features)), mode='constant')
    else:
        # Truncate if the number of features is higher than max_features
        padded_features = tfidf_features[:, :max_features]
    
    return padded_features

user_id = 1

# all_articles = articles.objects.filter(category='Top Headlines')
import ast

# article_features = [ast.literal_eval(article.feature_vector)[0] for article in all_articles]

# # for article in all_articles:
# #     article_feature = create_article_features(article.title, article.description)
# #     article_features.append(article_feature[0])

# recommended_articles = get_recommendation(1, article_features)

# recommended_articles = [all_articles[int(article)] for article in recommended_articles]

# print(recommended_articles[0].title)
# print(recommended_articles[0].description)
all_articles = articles.objects.all().order_by('-publish_date')
all_articles_feature_vector = [ast.literal_eval(article.feature_vector)[0] for article in all_articles]
recommended_articles = get_recommendation(user_id, all_articles_feature_vector)
all_articles_sorted = [all_articles[int(index)] for index in recommended_articles]


