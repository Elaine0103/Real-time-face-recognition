// MyExternalPage.js
import React from 'react';
import { useEffect, useState , useRef} from 'react';
import './App.css'
import io from 'socket.io-client';
import { useNavigate } from 'react-router-dom';
import {start, stop} from './Client'

const MyExternalPage = () => {
    const navigate = useNavigate(); // Get the navigation function using useNavigate hook
    const [data, setData] = useState(null); // State to store data from socket
    
    useEffect(() => {
        const socket = io("http://localhost:443"); // Connect to socket.io server
  
        // Listen for 'number_assigned' event from the socket
        socket.on('number_assigned', (data) => {
            console.log('Number assigned:', data);
            setData(data); // Update state with received data

            // stop(); // Stop the current page 
            
            navigate(`/getnumber`, {
                state: {
                    number_plate_id: data.number_plate_id,
                    client_name: data.client_name,
                    client_phone: data.client_phone,
                    base64_data: data.base64_data
                }
            });
            
            console.log('Navigating to /getnumber...');
        }); 
        
        // Listen for 'number_assignment_failed' event from the socket
        socket.on('number_assignment_failed', (data) => {
            console.log('Number assignment failed:', data.message);
        });

        return () => {
            socket.disconnect(); // Disconnect from socket when component unmounts
        };
    }, []);

    // useEffect(() => {
    //     const socket = io("http://localhost:443"); // Connect to socket.io server
        
    //     socket.on('number_assigned', (data) => {
    //         console.log('Number assigned:', data);

    //         const targetUrl = `/getnumber?number_plate_id=${data.number_plate_id}&client_name=${data.client_name}&client_phone=${data.client_phone}&base64_data=${data.base64_data}`;
    //         window.location.href = targetUrl;
    //         console.log('Navigating to /getnumber...');

    //     });

    //     // Listen for 'number_assignment_failed' event from the socket
    //     socket.on('number_assignment_failed', (data) => {
    //         console.log('Number assignment failed:', data.message);
    //     });

    //     return () => {
    //         socket.disconnect(); // Disconnect from socket when component unmounts
    //     };
    // }, []);


    // Initialize function
    const init =() => {
        //console.log(window)
        //window.start();
        setTimeout(() => {
            start();
        }, 1000);
        
        // document.addEventListener('DOMContentLoaded', () => {
            
        // })
    }

    useEffect(() => {
        // const script = document.createElement('script'); // Create a <script> element to load an external JavaScript file
        // script.src = 'http://localhost:3000/client.js'; // Replace with the actual path to your client.js file
        // document.head.appendChild(script); // Append the <script> element to the <head> of the document
        init(); // init function
        
        return () => {
        //   document.head.removeChild(script); // Remove the <script> element when component unmounts
        };
      }, []);


    return (
        <div>    
            <div className="option" style={{display: 'none'}}>
                <input id="use-datachannel" defaultChecked type="checkbox" />
                <label htmlFor="use-datachannel">Use datachannel</label>
                <select id="datachannel-parameters">
                    <option value='{"ordered": true}'>Ordered, reliable</option>
                    <option value='{"ordered": false, "maxRetransmits": 0}'>Unordered, no retransmissions</option>
                    <option value='{"ordered": false, "maxPacketLifetime": 500}'>Unordered, 500ms lifetime</option>
                </select>
            </div>
            <div className="option" style={{display: 'none'}}>
                <input id="use-audio" defaultChecked type="checkbox" />
                <label htmlFor="use-audio">Use audio</label>
                <select id="audio-codec"></select>
                   

                
            </div>
            <div className="option" style={{display: 'none'}}>
                <input id="use-video" defaultChecked type="checkbox" />
                <label htmlFor="use-video">Use video</label>
                <select id="video-resolution"></select>
                <select id="video-transform"></select>
                <select id="video-codec"></select>
            </div>
            <div className="option" style={{display: 'none'}}>
                <input id="use-stun" defaultChecked type="checkbox" />
                <label htmlFor="use-stun">Use STUN server</label>
            </div>

            {/* <button id="start" className="orange-button" onClick={() => window.start()}>點擊開始辨識</button> */}
            <button id="stop" style={{display: 'none'}} onClick={() => window.stop()}>Stop</button>

           
            <p className="extra-con">
                ICE gathering state: <span id="ice-gathering-state"></span>
            </p>
            <p className="extra-con">
                ICE connection state: <span id="ice-connection-state"></span>
            </p>
            <p className="extra-con">
                Signaling state: <span id="signaling-state"></span>
            </p>

            <div id="media"  className='media-con' >
                <h2 ></h2>

                <audio id="audio" autoPlay={true}></audio>
                <video className='height-con' id="video" autoPlay={true} playsInline={true}></video>
                

            </div>

            <pre id="data-channel" style={{height: 200}} className="extra-con"></pre>
            
            <pre id="offer-sdp" className="extra-con"></pre>
          
            <pre id="answer-sdp" className="extra-con"></pre>
          
        </div>
    );
};

export default MyExternalPage;
