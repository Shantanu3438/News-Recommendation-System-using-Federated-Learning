// import trainModel from 'mlmodel';

// Function to check if user is logged in
function checkLogin() {
    const token = localStorage.getItem("access_token");
    if (!token) {
      window.location.href = "login.html"; // Redirect to login page if not logged in
    }
  }

  // Check login status when the page loads
  window.onload = function() {
    checkLogin();
  };

function fetchArticles() {
    user_id = localStorage.getItem('user_id');
  fetch('http://localhost:8000/recommended-articles/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({user_id})
  })
      .then(response => response.json())
      .then(data => {
        localStorage.setItem('articlesData', JSON.stringify(data));
        console.log('Articles fetched !')
      })
      .catch(error => {
          console.error('Error fetching articles:', error);
      });
}

fetchArticles();

newsData = localStorage.getItem('articlesData')
newsData = JSON.parse(newsData)

  // Function to display news cards based on category
  function displayNews(category) {
    const newsContainer = document.getElementById("news-container");
    newsContainer.innerHTML = ""; // Clear previous content
    
    let filteredNews;

    if (category === "Recommended for You") {
        filteredNews = newsData.slice(0, 10);
    }
    else {
    // Filter news based on category
    filteredNews = newsData.slice(10, newsData.length).filter(news => news.category === category);
    }

    // Display news cards
    filteredNews.forEach(news => {
        const card = document.createElement("div");
        card.classList.add("news-card");
        card.innerHTML = `
        <div class="article--card">
        <img class="article--image" src="${news.image_url}" alt="${news.title}">
        <h2>${news.title}</h2>
        <p>Author: ${news.author}</p>
        <p>Description: ${news.description}</p>
        <p>Publish Date: ${news.publish_date}</p>
        </div>
        <button class="like-btn" data-id="${news.id}">Like</button>
        <button class="dislike-btn" data-id="${news.id}">Dislike</button>
      `;

    // Add event listeners for like and dislike buttons
    card.querySelector(".like-btn").addEventListener("click", () => {
        togglePreference(news.id, "like", card);
      });
  
      card.querySelector(".dislike-btn").addEventListener("click", () => {
        togglePreference(news.id, "dislike", card);
      });
  
      const articleCard = card.querySelector(".article--card").addEventListener("click", () =>{
        createDataPoint(news.id)
        window.open(news.url, "_blank")
      });
    //   card.onclick = function() {
    //     window.open(news.url, "_blank");
    //   };

      newsContainer.appendChild(card);
    });
  }
  
  
  // Event listeners for navbar links
  document.getElementById("recommended").addEventListener("click", () => displayNews("Recommended for You"));
  document.getElementById("trending").addEventListener("click", () => displayNews("Top Headlines"));
  document.getElementById("sports").addEventListener("click", () => displayNews("Sports"));
  document.getElementById("technology").addEventListener("click", () => displayNews("Technology"));
  document.getElementById("business").addEventListener("click", () => displayNews("Business"));
  document.getElementById("science").addEventListener("click", () => displayNews("Science"));
  
  
  function displayUserInfo() {
      const userInfoContainer = document.getElementById("user-info");
      const user = getUserFromLocalStorage(); // Function to retrieve user information from localStorage
    
      if (user) {
          userInfoContainer.innerHTML = `
          <p>Welcome, ${user}!</p>
          <button id="logout-btn">Logout</button>
          `;
          
          // Add logout functionality
          document.getElementById("logout-btn").addEventListener("click", () => {
              logoutUser();
            });
        } else {
      userInfoContainer.innerHTML = ""; // Clear user information if not authenticated
    }
}
  
// Function to retrieve user information from localStorage
function getUserFromLocalStorage() {
    const user = localStorage.getItem("username");
    return user ? user : null;
}

// Function to logout user (clear localStorage and token)
function logoutUser() {
    localStorage.removeItem("username");
    localStorage.removeItem("access_token"); // Remove token
    localStorage.removeItem("user_interaction_data");
    localStorage.removeItem("user_interaction_data");
    localStorage.removeItem("user_id");
    localStorage.removeItem("data_point");
    localStorage.removeItem("articlesData");
    window.location.href = "login.html";
}


// Function to handle toggling of like/dislike buttons
function togglePreference(id, preference, card) {
    const likeBtn = card.querySelector(".like-btn");
    const dislikeBtn = card.querySelector(".dislike-btn");
  
    if (preference === "like") {
      if (!likeBtn.classList.contains("active")) {
        localStorage.setItem(`liked_${id}`, true);
        localStorage.removeItem(`disliked_${id}`);
        likeBtn.classList.add("active");
        likeBtn.textContent = "Liked"
        dislikeBtn.classList.remove("active");
      } else {
        localStorage.removeItem(`liked_${id}`);
        likeBtn.classList.remove("active");
        likeBtn.textContent = "like"
      }
    } else if (preference === "dislike") {
      if (!dislikeBtn.classList.contains("active")) {
        localStorage.setItem(`disliked_${id}`, true);
        localStorage.removeItem(`liked_${id}`);
        dislikeBtn.classList.add("active");
        dislikeBtn.textContent = "Disliked"
        likeBtn.classList.remove("active");
      } else {
        localStorage.removeItem(`disliked_${id}`);
        dislikeBtn.classList.remove("active");
        dislikeBtn.textContent = "dislike"
      }
    }
  }

// Function to mark clicked article and update user_interaction_data
function createDataPoint(articleId) {
    const user_id = localStorage.getItem('user_id');
    const interaction_data = [1];
    const selectedArticle = newsData.filter(news => news.id === articleId);
    const feature_vector = JSON.parse(selectedArticle[0].feature_vector);
    inputData = {
        user_id : user_id,
        interaction_data : interaction_data,
        feature_vector : feature_vector[0],
    }
    trainModel(inputData).then((history) => {
        console.log('Training Completed !');
        updateGlobalModel()
    }).catch((error) => {
        console.log('Error during training:', error);
    });
}  

// Display user information
displayUserInfo();

// Initial display of news (Recommended for You)
displayNews("Recommended for You");