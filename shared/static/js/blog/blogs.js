let debounceTimer;

document.getElementById('search').addEventListener('input', function () {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    updateSearchURL();
  }, 500);
});

function updateSearchURL() {
  const search = document.getElementById('search').value;
  const urlParams = new URLSearchParams(window.location.search);

  if (search) {
    urlParams.set('search', search);
  } else {
    urlParams.delete('search');
  }

  window.location.search = urlParams.toString();
}

function toggleTag(tag) {
  const urlParams = new URLSearchParams(window.location.search);
  let tags = urlParams.get('tag') ? urlParams.get('tag').split(',') : [];

  if (tags.includes(tag)) {
    tags = tags.filter((t) => t !== tag);
  } else {
    tags.push(tag);
  }

  if (tags.length > 0) {
    urlParams.set('tag', tags.join(','));
  } else {
    urlParams.delete('tag');
  }

  window.location.search = urlParams.toString();
}
