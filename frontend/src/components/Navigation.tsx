import React from 'react'
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Box, Toolbar } from '@mui/material'
import { Dashboard as DashboardIcon, LiveTv, TrendingUp, BarChart } from '@mui/icons-material'
import { Link } from 'react-router-dom'

const drawerWidth = 240

export const Navigation: React.FC = () => {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          <ListItem button component={Link} to="/">
            <ListItemIcon><DashboardIcon /></ListItemIcon>
            <ListItemText primary="仪表板" />
          </ListItem>
          
          <ListItem button component={Link} to="/live-streams">
            <ListItemIcon><LiveTv /></ListItemIcon>
            <ListItemText primary="直播流" />
          </ListItem>
          
          <ListItem button component={Link} to="/hashtag-analysis">
            <ListItemIcon><BarChart /></ListItemIcon>
            <ListItemText primary="话题分析" />
          </ListItem>
          
          <ListItem button component={Link} to="/trending-topics">
            <ListItemIcon><TrendingUp /></ListItemIcon>
            <ListItemText primary="热门话题" />
          </ListItem>
        </List>
      </Box>
    </Drawer>
  )
}