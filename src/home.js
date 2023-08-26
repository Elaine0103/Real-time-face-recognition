import React from 'react';
import {BrowserRouter, Routes, Route, Link} from 'react-router-dom';
import GetNumber from './GetNumber';
import Ask from './Ask';
// import Client from './Client'

export default function Home() {
 
 
    return (  
    
    <BrowserRouter>
      
      <Link to="/" >首頁</Link>
      <Link to="/ask" >是否註冊</Link>

      <Routes>s
            <Route path="/getnumber"  element={<GetNumber/>}  />
            <Route path="/ask"  element={<Ask/>}  />

        {/* <Route path="/face" element={<Face/>}/> */}
             
      </Routes>
    </BrowserRouter>
    )
}


