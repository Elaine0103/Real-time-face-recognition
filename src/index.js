import React from 'react';
// import ReactDOM from 'react-dom/client';
import ReactDOM from "react-dom";
import './index.css';
import App from './App';
import Word from './word'

import reportWebVitals from './reportWebVitals';
import { BrowserRouter } from 'react-router-dom';


ReactDOM.render(
  <BrowserRouter>
  <React.StrictMode>
  <App />
  </React.StrictMode>
  </BrowserRouter>, 
  document.getElementById("root"));

reportWebVitals();
// 17.02