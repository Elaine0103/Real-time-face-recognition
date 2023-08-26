// GetNumber.js
import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

function GetNumber(props) {
  const navigate = useNavigate(); // Get the navigation function using useNavigate hook
  const location = useLocation(); // Get the current location using useLocation hook
  const [countdown, setCountdown] = useState(3);

  const formatPhoneNumber = (phoneNumber) => {
    if (phoneNumber && phoneNumber.length === 10) {
      return `${phoneNumber.substring(0, 4)}***${phoneNumber.substring(7)}`;
    }
    return phoneNumber;
  };

  useEffect(() => {
    const id = setTimeout (()=> {
        console.log('test');
        navigate('/') // Navigate to '/external' after a delay of 5000ms (5 seconds)  
    }, 3000);


    // Update the countdown every second
    const countdownId = setInterval(() => {
      setCountdown(prevCountdown => prevCountdown - 1);
    }, 1000);

    // const formatPhoneNumber = (phoneNumber) => {
    //   if (phoneNumber && phoneNumber.length === 10) {
    //     return `${phoneNumber.substring(0, 4)}***${phoneNumber.substring(7)}`;
    //   }
    //   return phoneNumber;
    // };

    return () => {
      clearTimeout(id); // Clear the timeout when the component unmounts or changes
      clearInterval(countdownId); // Clear the countdown interval
    }
  },[navigate]); // The empty dependency array ensures the effect runs only once

  return (
    <div className="centered-content">
      <div>
        <h1>號碼牌取號</h1>
        {/* <button onClick={assignNumber}>Assign Number</button> */}
        {location.state ? (
          <div>
            <p>顧客號碼牌: {location.state.number_plate_id}</p>
            <p>顧客姓名: {location.state.client_name}</p>
            {/* <p>顧客電話: {location.state.client_phone}</p> */}
            <p>顧客電話: {formatPhoneNumber(location.state.client_phone)}</p>
            <p className="countdown-container"> 倒數計時: {countdown} 秒</p>
            {location.state.base64_data && (
              <img
                src={`data:image/webp;base64,${location.state.base64_data}`}
                alt="Client"
              />
            )}
          </div>
        ) : (
          <p>No number assigned yet</p>
        )}
        <Link to="/external">Back to Home</Link>
      </div>
    </div>
  );
}

export default GetNumber;
