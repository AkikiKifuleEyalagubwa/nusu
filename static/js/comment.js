// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Like Button Handler
    document.body.addEventListener('click', async (e) => {
        const likeBtn = e.target.closest('.like-btn');
        if (likeBtn) {
            e.preventDefault();
            const tweetId = likeBtn.dataset.tweetId;
            try {
                const response = await fetch(`/community/tweet/${tweetId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    const icon = likeBtn.querySelector('i');
                    const count = likeBtn.querySelector('.like-count');
                    icon.className = data.liked ? 'bi bi-heart-fill text-danger' : 'bi bi-heart';
                    count.textContent = data.like_count;
                }
            } catch (error) {
                console.error('Like error:', error);
            }
        }
    });

    // CSRF Token Helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

// Retweet Button Handler
document.addEventListener('click', async (e) => {
    const retweetBtn = e.target.closest('.retweet-btn');
    
    if (retweetBtn) {
        e.preventDefault();
        const tweetId = retweetBtn.dataset.tweetId;
        const action = retweetBtn.dataset.action;
        const url = action === 'retweet' 
            ? `/community/tweet/${tweetId}/retweet/`
            : `/community/tweet/${tweetId}/undo_retweet/`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update UI
                const countElement = retweetBtn.querySelector('.retweet-count');
                const icon = retweetBtn.querySelector('i');
                
                countElement.textContent = data.retweet_count;
                retweetBtn.dataset.action = action === 'retweet' ? 'undo' : 'retweet';
                icon.style.color = action === 'retweet' ? '#2A3F54' : '';
            }
        } catch (error) {
            console.error('Retweet error:', error);
        }
    }
});

// CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}