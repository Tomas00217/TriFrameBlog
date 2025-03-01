var quill = new Quill('#editor', {
  theme: 'snow',
});

var existingContent = document.querySelector('#hidden-content').value;
if (existingContent) {
  quill.root.innerHTML = existingContent;
}

function updateContent() {
  document.querySelector('#hidden-content').value = quill.root.innerHTML;
}

function previewImage(event) {
  const input = event.target;
  const preview = document.getElementById('image-preview');
  const placeholderText = document.getElementById('placeholder-text');

  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.classList.remove('hidden');
      placeholderText.classList.add('hidden');
    };
    reader.readAsDataURL(input.files[0]);
  }
}
