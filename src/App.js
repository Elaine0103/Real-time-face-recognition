// import './App.css';
import './App.css';
import {BrowserRouter, Routes, Route, Link} from 'react-router-dom';
// import React from 'react'

import GetNumber from './GetNumber';
import WaitingList from './WaitingList';
import Ask from './Ask';
import { useEffect } from 'react';


import Home from './home';
import React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import AdbIcon from '@mui/icons-material/Adb';
import FiveGIcon from '@mui/icons-material/FiveG';
import MyExternalPage from './MyExternalPage';

const pages = ["首頁", ];
const settings = ['Profile', 'Account', 'Dashboard', 'Logout'];

function ResponsiveAppBar() {
  const [anchorElNav, setAnchorElNav] = React.useState(null);
  const [anchorElUser, setAnchorElUser] = React.useState(null);

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

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget);
  };
  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  return (
    
    <div>
    <AppBar position="static" style={{ background: '#f28500' }}>
      
      
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <FiveGIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }} />
          <Typography
            variant="h5"
            noWrap
            component="a"
            href="/"
            sx={{
              mr: 2,
              display: { xs: 'none', md: 'flex' },
              fontFamily: 'monospace',
              fontWeight: 700,
              letterSpacing: '.3rem',
              color: 'white',
              textDecoration: 'none',
            }}
          >
            台灣大哥大  
          </Typography>

          <Box  sx={{   
             flexGrow: 1, display: { xs: 'flex', md: 'none',},  }}>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleOpenNavMenu}
              color="secondary"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorElNav}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              open={Boolean(anchorElNav)}
              onClose={handleCloseNavMenu}
              sx={{
                display: { xs: 'block', md: 'none' },
              }}
            >
              {pages.map((page) => (
                <MenuItem key={page} onClick={handleCloseNavMenu}>
                  <Typography textAlign="center">{page}</Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>
          <FiveGIcon sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }} />
          <Typography
            variant="h5"
            noWrap
            component="a"
            href=""
            sx={{
              mr: 2,
              display: { xs: 'flex', md: 'none' },
              flexGrow: 1,
              fontFamily: 'monospace',
              fontWeight: 700,
              letterSpacing: '.3rem',
              color: 'orange',
              textDecoration: 'none',
            }}
          >

            LOGO
          </Typography>
          <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
            {pages.map((page) => (
              
              
              <Button href="/register"
                key={page}
                onClick={handleCloseNavMenu}
                sx={{ my: 2 , color: 'white', display: 'block' }}
              >
                {"註冊"}
              </Button>
            ))}
          </Box>
          
          <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar alt="Remy Sharp" src="/static/images/avatar/2.jpg" />
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
            >
              {settings.map((setting) => (
                <MenuItem key={setting} onClick={handleCloseUserMenu}>
                  <Typography textAlign="center">{setting}</Typography>
                </MenuItem>
              ))}

            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>


        <Routes>
              
              <Route path="/getnumber"  element={<GetNumber/>}  />
              <Route path="/ask"  element={<Ask/>}  />
              <Route path="/waitinglist" element={<WaitingList />} /> 
              {/* <Route exact path="/external" element={<MyExternalPage/>} /> */}
              <Route exact path="/" element={<MyExternalPage/>} />
    
        
        </Routes>      
     </div>
       );
}       
  

export default ResponsiveAppBar;





