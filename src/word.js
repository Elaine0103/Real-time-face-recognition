import React, { useEffect } from 'react';
import './App.css';

const Word = () => {
  useEffect(() => {
    // 創建 <script> 元素
    const script = document.createElement('script');

    // 指定 client.js 的 URL
    script.src = 'http://localhost:3000/client.js'; // 請將 "path/to/client.js" 替換為您的 client.js 文件的路徑

    // 將 <script> 元素添加到文檔的 <head> 元素中
    document.head.appendChild(script);

    // 在組件卸載時，移除 <script> 元素，避免重複加載
    return () => {
      document.head.removeChild(script);
    };
  }, []);

  return (
    <div>
      <h1>WebRTC with React</h1>
      {/* 在此添加其他 React 元素和內容 */}
    </div>
  );
};

export default Word;
