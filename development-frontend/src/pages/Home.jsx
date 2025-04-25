import React from 'react';
import { Box, Paper } from '@mui/material';
import HomeArticle from '../components/HomeArticle';
import espaLogo from "../assets/visual_id_ESPA.jpg";
import dotsoftLogo from '../assets/dotsoft_logo.png';
import imetLogo from '../assets/IMETlogo.png';

const drawerWidth = 240;

const Home = () => {
    const isAdmin = localStorage.getItem("userRole") === "ΔΙΑΧΕΙΡΙΣΤΗΣ";

    return (
        <Box sx={{ width: '100%', position: 'relative' }}>
            {/* Main content - HomeArticle.jsx */}
            <Paper elevation={3} sx={{ p: 2 }}>
                <HomeArticle isAdmin={isAdmin} />
            </Paper>

            {/* LEFT bottom: IMET + DOTSOFT logos */}
            <Box
                sx={{
                    position: "fixed",
                    bottom: 5,
                    left: `${drawerWidth + 30}px`,
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    zIndex: (theme) => theme.zIndex.tooltip, // float above most elements
                }}
            >
                <img
                    src={dotsoftLogo}
                    alt="Dotsoft Logo"
                    style={{ width: 130, height: "auto" }}
                />
                <img
                    src={imetLogo}
                    alt="IMET Logo"
                    style={{ width: 50, height: "auto" }}
                />
            </Box>

            {/* RIGHT bottom: ESPA logo */}
            <Box
                sx={{
                    position: "fixed",
                    bottom: 5,
                    right: 30,
                    zIndex: (theme) => theme.zIndex.tooltip,
                }}
            >
                <img
                    src={espaLogo}
                    alt="ESPA EU Funding"
                    style={{ width: 400, height: "auto" }}
                />
            </Box>
        </Box>
    );
};

export default Home;
