import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.scss'
import './assets/css/fonts.css'
import './assets/css/font-variables.css'
import './assets/css/app.min.css'
import './assets/css/custom.css'
import './assets/css/rtl.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
