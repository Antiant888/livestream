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
  IconButton
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  LiveTv as LiveTvIcon,
  SentimentSatisfied as SentimentSatisfiedIcon
} from '@mui/icons-material'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js'
import ChartjsAdapterDateFns from 'chartjs-adapter-date-fns'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

interface RealTimeStats {
  timestamp: string
  recent_content_count: number
  recent_hashtag_count: number
  active_trends: number
  top_trends: Array<{
    name: string
    score: number
    confidence: number
  }>
}

interface HashtagData {
  hashtag: string
  frequency: number
  velocity: number
  stream_count: number
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<RealTimeStats | null>(null)
  const [hashtagData, setHashtagData] = useState<HashtagData[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch real-time stats
      const statsResponse = await fetch('/api/stats/realtime')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Fetch hashtag frequency data
      const hashtagResponse = await fetch('/api/hashtags/frequency?limit=20')
      if (hashtagResponse.ok) {
        const hashtagData = await hashtagResponse.json()
        setHashtagData(hashtagData.hashtags || [])
      }
    } catch (err) {
      setError('Failed to fetch data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const chartData = {
    labels: hashtagData.map(h => h.hashtag),
    datasets: [
      {
        label: 'Frequency',
        data: hashtagData.map(h => h.frequency),
        borderColor: 'rgb(33, 150, 243)',
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Velocity',
        data: hashtagData.map(h => h.velocity),
        borderColor: 'rgb(76, 175, 80)',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        tension: 0.4,
      }
    ],
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Hashtag Frequency and Velocity',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          实时数据概览
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

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    最近内容数
                  </Typography>
                  <Typography variant="h4">
                    {stats?.recent_content_count || 0}
                  </Typography>
                </Box>
                <LiveTvIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    最近话题数
                  </Typography>
                  <Typography variant="h4">
                    {stats?.recent_hashtag_count || 0}
                  </Typography>
                </Box>
                <TrendingUpIcon color="secondary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    活跃趋势
                  </Typography>
                  <Typography variant="h4">
                    {stats?.active_trends || 0}
                  </Typography>
                </Box>
                <SentimentSatisfiedIcon sx={{ fontSize: 40, color: '#ffc107' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                最后更新
              </Typography>
              <Typography variant="h6">
                {stats?.timestamp 
                  ? new Date(stats.timestamp).toLocaleString('zh-CN')
                  : 'N/A'
                }
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                热门趋势
              </Typography>
              {stats?.top_trends && stats.top_trends.length > 0 ? (
                stats.top_trends.map((trend, index) => (
                  <Box key={index} display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                    <Chip 
                      label={trend.name} 
                      color="primary" 
                      variant="outlined"
                    />
                    <Box textAlign="right">
                      <Typography variant="body2" color="textSecondary">
                        信心: {(trend.confidence * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2">
                        分数: {trend.score.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                ))
              ) : (
                <Typography color="textSecondary">暂无数据</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Hashtag Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Line data={chartData} options={chartOptions} />
            </CardContent>
          </Card>
        </Grid>

        {/* Hashtag List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                话题频率分析
              </Typography>
              <Grid container spacing={2}>
                {hashtagData.map((hashtag, index) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" color="primary">
                          #{hashtag.hashtag}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          频率: {hashtag.frequency}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          速度: {hashtag.velocity.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          流数: {hashtag.stream_count}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}