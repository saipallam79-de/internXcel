const envApiBase = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'https://internxcel.onrender.com';

window.API_BASE_URL = window.API_BASE_URL_OVERRIDE || envApiBase;

window.clearInternXcelSession = function clearInternXcelSession() {
  localStorage.removeItem('internxcel_token');
  sessionStorage.clear();
  const persistentKeys = Object.keys(localStorage).filter((key) => key.startsWith('internxcel_'));
  persistentKeys.forEach((key) => localStorage.removeItem(key));
};
