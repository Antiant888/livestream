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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField
} from '@mui/material'
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon, SentimentSatisfied as SentimentSatisfiedIcon } from '@mui/icons-material'

interface TrendingTopic {
  topic_name: string
  score: number
  frequency: number
  velocity: number
  stream_count: number
  first_seen: string
  last_seen: string
  topic_type: string
  confidence: number
}

interface SentimentAnalysis {
  [key: string]: {
    average_sentiment: number
    sentiment_volatility: number
    positive_count: number
    negative_count: number
    neutral_count: number
    total_mentions: number
    sentiment_trend: string
  }
}

export const TrendingTopics: React.FC = () => {
  const [trends, setTrends] = useState<TrendingTopic[]>([])
  const [sentimentAnalysis, setSentimentAnalysis] = useState<SentimentAnalysis>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [timeWindow, setTimeWindow] = useState(24)
  const [minFrequency, setMinFrequency] = useState(5)
  const [minVelocity, setMinVelocity] = useState(0.5)
  const [selectedHashtag, setSelectedHashtag] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch trending topics
      const trendsResponse = await fetch(`/api/trends?time_window=${timeWindow}&min_frequency=${minFrequency}&min_velocity=${minVelocity}`)
      if (trendsResponse.ok) {
        const trendsData = await trendsResponse.json()
        setTrends(trendsData.trends || [])
      }

      // Fetch sentiment analysis
      const sentimentResponse = await fetch(`/api/trends/sentiment?time_window=${timeWindow}&hashtag=${selectedHashtag}`)
      if (sentimentResponse.ok) {
        const sentimentData = await sentimentResponse.json()
        setSentimentAnalysis(sentimentData.sentiment_analysis || {})
      }
    } catch (err) {
      setError('Failed to fetch trending topics')
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
  }, [timeWindow, minFrequency, minVelocity, selectedHashtag])

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'success'
    if (score < -0.1) return 'error'
    return 'default'
  }

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return '😊'
    if (score < -0.1) return '😢'
    return '😐'
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          热门话题
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

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>时间窗口 (小时)</InputLabel>
            <Select
              value={timeWindow}
              label="时间窗口 (小时)"
              onChange={(e) => setTimeWindow(Number(e.target.value))}
            >
              <MenuItem value={6}>6 小时</MenuItem>
              <MenuItem value={12}>12 小时</MenuItem>
              <MenuItem value={24}>24 小时</MenuItem>
              <MenuItem value={48}>48 小时</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="最小频率"
            type="number"
            value={minFrequency}
            onChange={(e) => setMinFrequency(Number(e.target.value))}
            InputProps={{ inputProps: { min: 1, max: 100 } }}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="最小速度"
            type="number"
            value={minVelocity}
            onChange={(e) => setMinVelocity(Number(e.target.value))}
            InputProps={{ inputProps: { min: 0, max: 10, step: 0.1 } }}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                热门话题列表
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>话题</TableCell>
                      <TableCell align="right">分数</TableCell>
                      <TableCell align="right">频率</TableCell>
                      <TableCell align="right">速度</TableCell>
                      <TableCell align="right">信心</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {trends.map((topic, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip 
                            label={topic.topic_name} 
                            color={getSentimentColor(topic.score)} 
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">{topic.score.toFixed(2)}</TableCell>
                        <TableCell align="right">{topic.frequency}</TableCell>
                        <TableCell align="right">{topic.velocity.toFixed(2)}</TableCell>
                        <TableCell align="right">{(topic.confidence * 100).toFixed(0)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                情感分析
              </Typography>
              <TextField
                fullWidth
                label="选择话题查看情感分析"
                select
                value={selectedHashtag}
                onChange={(e) => setSelectedHashtag(e.target.value)}
                sx={{ mb: 2 }}
              >
                <MenuItem value="">全部</MenuItem>
                {trends.map((topic, index) => (
                  <MenuItem key={index} value={topic.topic_name}>
                    {topic.topic_name}
                  </MenuItem>
                ))}
              </TextField>
              
              {Object.keys(sentimentAnalysis).length > 0 ? (
                Object.entries(sentimentAnalysis).map(([hashtag, analysis]) => (
                  <Card key={hashtag} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Typography variant="subtitle1" color="primary">
                          #{hashtag}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2" color="textSecondary">
                            {getSentimentIcon(analysis.average_sentiment)}
                          </Typography>
                          <Chip 
                            label={analysis.sentiment_trend} 
                            color={getSentimentColor(analysis.average_sentiment)}
                            size="small"
                          />
                        </Box>
                      </Box>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            平均情感: {analysis.average_sentiment.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            波动性: {analysis.sentiment_volatility.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2" color="success.main">
                            正面: {analysis.positive_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2" color="error.main">
                            负面: {analysis.negative_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2" color="textSecondary">
                            中性: {analysis.neutral_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="textSecondary">
                            总提及: {analysis.total_mentions}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Typography color="textSecondary">暂无情感分析数据</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                话题详情
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>话题</TableCell>
                      <TableCell>分数</TableCell>
                      <TableCell>频率</TableCell>
                      <TableCell>速度</TableCell>
                      <TableCell>流数</TableCell>
                      <TableCell>类型</TableCell>
                      <TableCell>信心</TableCell>
                      <TableCell>首次出现</TableCell>
                      <TableCell>最后出现</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {trends.map((topic, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip 
                            label={topic.topic_name} 
                            color={getSentimentColor(topic.score)}
                          />
                        </TableCell>
                        <TableCell>{topic.score.toFixed(2)}</TableCell>
                        <TableCell>{topic.frequency}</TableCell>
                        <TableCell>{topic.velocity.toFixed(2)}</TableCell>
                        <TableCell>{topic.stream_count}</TableCell>
                        <TableCell>{topic.topic_type}</TableCell>
                        <TableCell>{(topic.confidence * 100).toFixed(0)}%</TableCell>
                        <TableCell>
                          {topic.first_seen ? new Date(topic.first_seen).toLocaleString('zh-CN') : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {topic.last_seen ? new Date(topic.last_seen).toLocaleString('zh-CN') : 'N/A'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}