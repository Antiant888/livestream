import React, { useState, useEffect } from 'react'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Alert,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material'
import { Refresh as RefreshIcon } from '@mui/icons-material'

interface LiveStream {
  stream_id: string
  title: string
  status: string
  viewer_count: number
  platform_source: string
  thumbnail_url: string
  channel_name: string
  start_time: string
  end_time: string
}

export const LiveStreams: React.FC = () => {
  const [streams, setStreams] = useState<LiveStream[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/streams')
      if (response.ok) {
        const data = await response.json()
        setStreams(data.streams || [])
      } else {
        throw new Error('Failed to fetch streams')
      }
    } catch (err) {
      setError('Failed to fetch live streams')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    
    // Refresh data every 60 seconds
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  const filteredStreams = streams.filter(stream => {
    if (filter === 'live') return stream.status === 'live'
    if (filter === 'scheduled') return stream.status === 'scheduled'
    return true
  })

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          直播流管理
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchData}
          disabled={loading}
        >
          刷新数据
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      <Box mb={3}>
        <FormControl fullWidth>
          <InputLabel>筛选</InputLabel>
          <Select
            value={filter}
            label="筛选"
            onChange={(e) => setFilter(e.target.value)}
          >
            <MenuItem value="all">全部</MenuItem>
            <MenuItem value="live">直播中</MenuItem>
            <MenuItem value="scheduled">已预定</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {filteredStreams.map((stream) => (
          <Grid item xs={12} md={6} lg={4} key={stream.stream_id}>
            <Card>
              {stream.thumbnail_url && (
                <Box
                  component="img"
                  src={stream.thumbnail_url}
                  alt={stream.title}
                  sx={{ width: '100%', height: 200, objectFit: 'cover' }}
                />
              )}
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                  <Chip 
                    label={stream.status} 
                    color={stream.status === 'live' ? 'error' : 'default'}
                    size="small"
                  />
                  <Typography variant="caption" color="textSecondary">
                    {stream.platform_source}
                  </Typography>
                </Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {stream.title}
                </Typography>
                {stream.channel_name && (
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    主播: {stream.channel_name}
                  </Typography>
                )}
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">
                    观众: {stream.viewer_count.toLocaleString()}
                  </Typography>
                  {stream.start_time && (
                    <Typography variant="body2" color="textSecondary">
                      开始: {new Date(stream.start_time).toLocaleString('zh-CN')}
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredStreams.length === 0 && !loading && (
        <Box textAlign="center" py={5}>
          <Typography color="textSecondary">
            暂无 {filter === 'live' ? '直播中' : filter === 'scheduled' ? '已预定' : '可用'} 的直播流
          </Typography>
        </Box>
      )}
    </Box>
  )
}