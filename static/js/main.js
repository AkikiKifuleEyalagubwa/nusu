document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    const authModal = new bootstrap.Modal(document.getElementById('loginRegisterModal'));

    // Generic AJAX Handler
    async function handleAction(e, selector, urlBuilder, updateUI) {
        const target = e.target.closest(selector);
        if (!target) return;
        
        e.preventDefault();
        
        // Check authentication
        if (document.body.dataset.authenticated !== 'True') {
            authModal.show();
            return;
        }

        try {
            const response = await fetch(urlBuilder(target), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error('Request failed');
            }

            const data = await response.json();
            updateUI(target, data);
            showToast(data.message || 'Action completed', data.success ? 'success' : 'warning');
            return data;
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message || 'An error occurred. Please try again.', 'danger');
            throw error;
        }
    }

    // Add this to main.js
    document.addEventListener('click', (e) => {
        const profileLink = e.target.closest('a[href^="/users/user_profile/"]');
        if (profileLink && document.body.dataset.authenticated === 'False') {
            e.preventDefault();
            authModal.show();
        }
    });
    
    
    // Updated Like System
    document.addEventListener('click', async (e) => {
        const likeBtn = e.target.closest('.like-btn');
        if (likeBtn) {
            const tweetId = likeBtn.dataset.tweetId;
            const icon = likeBtn.querySelector('i');
            const countSpan = likeBtn.querySelector('.count');
            
            try {
                const response = await fetch(`/community/tweet/${tweetId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Accept': 'application/json'
                    }
                });
                
                const data = await response.json();
                if (data.success) {
                    icon.className = data.liked ? 
                        'bi bi-heart-fill text-dark' : 
                        'bi bi-heart';
                    countSpan.textContent = data.like_count;
                    
                }
            } catch (error) {
                console.error('Like error:', error);
            }
        }
    });

 
    // Update follow handler
    document.addEventListener('submit', async (e) => {
        if (e.target.matches('.follow-form')) {
            e.preventDefault();
            const form = e.target;
            const btn = form.querySelector('button');
            const followerCounts = document.querySelectorAll('.follower-count');
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    // Update button state
                    btn.innerHTML = data.is_following ?
                        '<i class="bi bi-person-dash me-2"></i>Following' :
                        '<i class="bi bi-person-plus me-2"></i>Follow';
                    
                    // Update button classes
                    btn.classList.toggle('btn-dark', data.is_following);
                    btn.classList.toggle('btn-outline-dark', !data.is_following);
                    
                    // Update follower counts
                    followerCounts.forEach(el => {
                        el.textContent = data.follower_count;
                    });
                    
                    showToast(data.message,'success');
                }
            } catch (error) {
                showToast('Action failed');
            }
        }
    });


    // Update retweet handler
    document.addEventListener('click', async (e) => {
        const retweetBtn = e.target.closest('.retweet-btn');
        if (retweetBtn) {
            const tweetId = retweetBtn.dataset.tweetId;
            const icon = retweetBtn.querySelector('i');
            const countSpan = retweetBtn.querySelector('.count');
            
            try {
                const response = await fetch(`/community/tweet/${tweetId}/retweet/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Accept': 'application/json'
                    }
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    // Keep the repeat icon, just change styling
                    icon.style.color = data.retweeted ? '#17bf63' : '#647788';
                    countSpan.textContent = data.retweet_count;
                    showToast(data.message);
                    
                    document.querySelectorAll(`[data-tweet-id="${tweetId}"] .retweet-count`)
                        .forEach(el => el.textContent = data.retweet_count);
                }
            } catch (error) {
                showToast('Retweet action failed');
            }
        }
    });
    // Add to main.js
    document.getElementById('media-input').addEventListener('change', function(e) {
        const files = e.target.files;
        const previewContainer = document.createElement('div');
        previewContainer.className = 'media-preview mt-3';
        
        Array.from(files).forEach(file => {
            const url = URL.createObjectURL(file);
            const element = file.type.startsWith('image') ? 
                `<img src="${url}" class="preview-item">` :
                `<video src="${url}" class="preview-item" controls></video>`;
            
            previewContainer.innerHTML += element;
        });
        
        this.parentNode.appendChild(previewContainer);
    });

    // Reply System
    document.body.addEventListener('click', async (e) => {
        const replyBtn = e.target.closest('.reply-btn');
        if (replyBtn) {
            e.preventDefault();
            
            if (document.body.dataset.authenticated === 'False') {
                authModal.show();
                return;
            }

            const tweetId = replyBtn.dataset.tweetId;
            if (tweetId) {
                window.location.href = `/community/tweet/${tweetId}/reply/`;
            } else {
                console.error('Tweet ID is undefined');
            }
        }
    });

    // Delete System
    document.addEventListener('DOMContentLoaded', function() {
        // Handle tweet deletion
        document.querySelectorAll('.delete-tweet-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (confirm('Are you sure you want to delete this tweet?')) {
                    fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            this.closest('.tweet-card').remove();
                        }
                    });
                }
            });
        });
    });

    // Add media click handler
    document.addEventListener('click', (e) => {
        const media = e.target.closest('.media-item');
        if (media) {
            const mediaType = media.tagName.toLowerCase();
            const mediaSrc = media.src || media.querySelector('source').src;
            
            const lightbox = document.createElement('div');
            lightbox.className = 'media-lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    ${mediaType === 'img' ? 
                        `<img src="${mediaSrc}" class="lightbox-media">` : 
                        `<video controls autoplay class="lightbox-media">
                            <source src="${mediaSrc}">
                        </video>`}
                    <button class="close-lightbox btn btn-dark">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            `;
            
            document.body.appendChild(lightbox);
            
            // Add close handler
            lightbox.querySelector('.close-lightbox').addEventListener('click', () => {
                lightbox.remove();
            });
        }
    });




    function showToast(message) {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer || !message) return;
    
        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-white bg-dark border-0';
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
    
        toastContainer.appendChild(toastEl);
        new bootstrap.Toast(toastEl).show();
        setTimeout(() => toastEl.remove(), 3000);
    }

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

    // Add hover effects to tweet cards
    document.querySelectorAll('.tweet-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
            card.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'none';
            card.style.boxShadow = 'none';
        });
    });

    // Profile picture hover effect
    document.querySelectorAll('.profile-pic-container').forEach(container => {
        container.addEventListener('mouseenter', () => {
            container.style.transform = 'scale(1.05)';
        });
        
        container.addEventListener('mouseleave', () => {
            container.style.transform = 'none';
        });
    });
});
// Theme Toggle Logic
function toggleTheme() {
  const body = document.body;
  const currentTheme = body.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  body.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Update toggle button icon
  const themeIcon = document.getElementById('theme-icon');
  themeIcon.className = newTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
}

