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
  Paper
} from '@mui/material'
import { Refresh as RefreshIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material'

interface HashtagAnalysis {
  hashtag: string
  frequency: number
  velocity: number
  stream_count: number
  first_seen: string
  last_seen: string
}

export const HashtagAnalysis: React.FC = () => {
  const [analysis, setAnalysis] = useState<HashtagAnalysis[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [timeWindow, setTimeWindow] = useState(24)
  const [limit, setLimit] = useState(100)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/hashtags/frequency?time_window=${timeWindow}&limit=${limit}`)
      if (response.ok) {
        const data = await response.json()
        setAnalysis(data.hashtags || [])
      } else {
        throw new Error('Failed to fetch hashtag analysis')
      }
    } catch (err) {
      setError('Failed to fetch hashtag analysis')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [timeWindow, limit])

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          话题分析
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
        <Grid item xs={12} md={6}>
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
              <MenuItem value={72}>72 小时</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="显示数量"
            type="number"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            InputProps={{ inputProps: { min: 10, max: 1000 } }}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                话题频率排行
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>话题</TableCell>
                      <TableCell align="right">频率</TableCell>
                      <TableCell align="right">速度</TableCell>
                      <TableCell align="right">流数</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analysis.slice(0, 20).map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip label={`#${item.hashtag}`} color="primary" size="small" />
                        </TableCell>
                        <TableCell align="right">{item.frequency}</TableCell>
                        <TableCell align="right">{item.velocity.toFixed(2)}</TableCell>
                        <TableCell align="right">{item.stream_count}</TableCell>
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
                详细统计
              </Typography>
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  总话题数: {analysis.length}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  平均频率: {analysis.length > 0 ? (analysis.reduce((sum, item) => sum + item.frequency, 0) / analysis.length).toFixed(2) : '0'}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  平均速度: {analysis.length > 0 ? (analysis.reduce((sum, item) => sum + item.velocity, 0) / analysis.length).toFixed(2) : '0'}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  最高频率: {analysis.length > 0 ? Math.max(...analysis.map(item => item.frequency)) : '0'}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  最高速度: {analysis.length > 0 ? Math.max(...analysis.map(item => item.velocity)) : '0'}
                </Typography>
              </Box>
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
                      <TableCell>频率</TableCell>
                      <TableCell>速度</TableCell>
                      <TableCell>流数</TableCell>
                      <TableCell>首次出现</TableCell>
                      <TableCell>最后出现</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analysis.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip label={`#${item.hashtag}`} color="primary" />
                        </TableCell>
                        <TableCell>{item.frequency}</TableCell>
                        <TableCell>{item.velocity.toFixed(2)}</TableCell>
                        <TableCell>{item.stream_count}</TableCell>
                        <TableCell>
                          {item.first_seen ? new Date(item.first_seen).toLocaleString('zh-CN') : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {item.last_seen ? new Date(item.last_seen).toLocaleString('zh-CN') : 'N/A'}
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