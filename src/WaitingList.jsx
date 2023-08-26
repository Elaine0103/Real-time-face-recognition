import React, { useState, useEffect } from 'react';
import axios from 'axios';



function WaitingList() {
  const [waitingList, setWaitingList] = useState([]);
  const [currentNumber, setCurrentNumber] = useState(0);

  // useEffect(() => {
  //   fetchWaitingList();
  // }, []);

  useEffect(() => {
    fetchWaitingList();
    // 定時每隔 5 秒重新獲取等待清單資料
    const interval = setInterval(fetchWaitingList, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (waitingList.length > 0) {
      setCurrentNumber(waitingList[0].id);
    }
  }, [waitingList]);

  const fetchWaitingList = async () => {
    try {
      const response = await axios.get('http://localhost:443/api/waiting_list'); 
      setWaitingList(response.data);
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const formatPhoneNumber = (phoneNumber) => {
    if (phoneNumber && phoneNumber.length === 10) {
      return `${phoneNumber.substring(0, 4)}***${phoneNumber.substring(7)}`;
    }
    return phoneNumber;
  };

  const handleNextNumber = async () => {
    try {
      await axios.post('http://localhost:443/api/next_number');
      check_waiting_list();
    } catch (error) {
      console.error(error);
    }
  };   

  const check_waiting_list = async () => {
    try {
      const response = await axios.get('http://localhost:443/api/waiting_list');
  
      if (response.status === 200) {
        setWaitingList(response.data); 
      }
    } catch (error) {
      console.error('check_waiting_list error: ',error);
    }
  };
  
  return (
    <div style={{ textAlign: 'center', margin: 'auto', width: '60%' }}>
      <h1>Waiting List</h1>
      <div style={{ marginBottom: '20px' }}>
        {currentNumber && (
          <p>目前等候號碼: {currentNumber}</p>
        )}
        <p>目前等候人數: {waitingList.length}</p>
        <button onClick={handleNextNumber}>下一號</button>
      </div>
      
      <table style={{ borderCollapse: 'collapse', width: '100%', margin: 'auto' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid black', padding: '8px' }}>等候號碼</th>
            <th style={{ border: '1px solid black', padding: '8px' }}>顧客姓名</th>
            <th style={{ border: '1px solid black', padding: '8px' }}>顧客電話</th>
          </tr>
        </thead>
        <tbody>
          {waitingList.map((item) => (
            <tr key={item.id}>
              <td style={{ border: '1px solid black', padding: '8px' }}>{item.id}</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>{item.client_name}</td>
              <td style={{ border: '1px solid black', padding: '8px' }}>{formatPhoneNumber(item.client_phone)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


export default WaitingList;

