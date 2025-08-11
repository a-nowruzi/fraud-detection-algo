import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './assets/css/index.scss'

// Function to hide preloader
const hidePreloader = () => {
  const preloader = document.getElementById('preloader');
  if (preloader) {
    preloader.style.opacity = '0';
    setTimeout(() => {
      preloader.style.display = 'none';
    }, 300);
  }
};

// Hide preloader when React app is ready
setTimeout(hidePreloader, 1000);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
