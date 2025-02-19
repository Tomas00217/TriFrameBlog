/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './django_blog/**/*.html',
    './flask_blog/**/*.html',
    './fastapi_blog/**/*.html',
    './shared/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
