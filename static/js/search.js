function handleSearchInput() {
    const searchInput = document.getElementById('searchInput');
    const autocompleteResults = document.getElementById('autocomplete-results');
    const query = searchInput.value.trim();

    if (!query) {
        autocompleteResults.style.display = 'none';
        autocompleteResults.innerHTML = '';
        return;
    }

    // Fetch HTML results from Django
    fetch(`/community/search/autocomplete/?q=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(html => {
            autocompleteResults.innerHTML = html;
            autocompleteResults.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching autocomplete results:', error);
            autocompleteResults.style.display = 'none';
        });
}

// Close autocomplete when clicking outside
document.addEventListener('click', function(e) {
    const autocompleteResults = document.getElementById('autocomplete-results');
    if (!e.target.closest('.search-container')) {
        autocompleteResults.style.display = 'none';
    }
});

// Clear input when clicking a result
document.getElementById('autocomplete-results')?.addEventListener('click', function(e) {
    if (e.target.closest('.autocomplete-item')) {
        document.getElementById('searchInput').value = '';
        this.style.display = 'none';
    }
});