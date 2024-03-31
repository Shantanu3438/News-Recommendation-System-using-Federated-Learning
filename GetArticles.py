import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsRecommendation.settings')
django.setup()
from Users.models import articles
from django.db import IntegrityError
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

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

def addArticles(fetched_articles, category):
    articlesAdded = 0
    for article in fetched_articles:
        if article['content'] is not None and article['description'] is not None:
            article_feature = create_article_features(article['title'], article['description'])
            feature_vector_json = json.dumps(article_feature.tolist())
            try:
                articles.objects.create(
                    source = article['source'],
                    title = article['title'],
                    author = article['author'],
                    description = article['description'],
                    url = article['url'],
                    image_url = article['urlToImage'],
                    publish_date = article['publishedAt'],
                    content = article['content'],
                    category = category,
                    feature_vector = feature_vector_json,
                )
                articlesAdded += 1
            except IntegrityError as e:
                pass
    print(f'Articles added in {category}: {articlesAdded}')
def getArticles():
    top_headlines = requests.get('https://newsapi.org/v2/top-headlines?country=in&apiKey=d6788e6c0822434ea06f652e0706156c')
    top_headlines = top_headlines.json()
    top_headlines = top_headlines['articles']
    addArticles(top_headlines, 'Top Headlines')

    top_technology = requests.get('https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=d6788e6c0822434ea06f652e0706156c')
    top_technology  = top_technology.json()
    top_technology = top_technology['articles']
    addArticles(top_technology, 'Technology')

    top_science = requests.get('https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=d6788e6c0822434ea06f652e0706156c')
    top_science  = top_science.json()
    top_science = top_science['articles']
    addArticles(top_science, 'Science')

    top_sports = requests.get('https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=d6788e6c0822434ea06f652e0706156c')
    top_sports  = top_sports.json()
    top_sports = top_sports['articles']
    addArticles(top_sports, 'Sports')

    top_business = requests.get('https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=d6788e6c0822434ea06f652e0706156c')
    top_business  = top_business.json()
    top_business = top_business['articles']
    addArticles(top_business, 'Business')

if __name__ == '__main__':
    getArticles()   