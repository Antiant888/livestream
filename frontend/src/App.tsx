import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Container, Box, Typography, AppBar, Toolbar } from '@mui/material'
import { Dashboard } from './components/Dashboard'
import { LiveStreams } from './components/LiveStreams'
import { HashtagAnalysis } from './components/HashtagAnalysis'
import { TrendingTopics } from './components/TrendingTopics'
import { Navigation } from './components/Navigation'

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            格隆汇 Live Streaming Analysis
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Navigation />
      
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Container maxWidth="xl">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live-streams" element={<LiveStreams />} />
            <Route path="/hashtag-analysis" element={<HashtagAnalysis />} />
            <Route path="/trending-topics" element={<TrendingTopics />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}

export default App