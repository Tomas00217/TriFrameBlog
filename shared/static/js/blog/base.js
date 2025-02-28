document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    document.querySelectorAll('.toast-message').forEach((el) => el.remove());
  }, 3000);
});
