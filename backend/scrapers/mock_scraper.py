import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from loguru import logger

from .base_scraper import BaseScraper

class MockScraper(BaseScraper):
    """模拟数据生成器，用于测试和演示"""
    
    def __init__(self, delay_range: tuple = (1, 2)):
        super().__init__("https://mock-gelonghui.com", delay_range)
        
        # 模拟数据池
        self.chinese_topics = [
            "股市", "财经", "科技", "人工智能", "新能源", "房地产", 
            "金融", "投资", "区块链", "数字货币", "5G", "芯片",
            "医药", "教育", "消费", "汽车", "互联网", "大数据"
        ]
        
        self.english_topics = [
            "stock", "finance", "tech", "AI", "energy", "real estate",
            "investment", "crypto", "blockchain", "5G", "semiconductor",
            "healthcare", "education", "consumer", "automotive", "internet"
        ]
        
        self.positive_words = ["好", "棒", "赞", "喜欢", "支持", "成功", "上涨", "利好", "增长", "突破"]
        self.negative_words = ["差", "坏", "失望", "下跌", "利空", "问题", "风险", "亏损", "困难", "挑战"]
        self.neutral_words = ["看", "说", "认为", "觉得", "分析", "讨论", "关注", "了解", "学习", "研究"]
        
        self.user_names = [
            "财经小达人", "投资小白", "股市老手", "科技爱好者", "AI研究员",
            "金融分析师", "区块链专家", "新能源观察员", "房地产评论员",
            "消费趋势", "教育专家", "医药研究员", "汽车评论员"
        ]
    
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """生成模拟数据"""
        logger.info("Generating mock data for testing...")
        
        results = []
        
        # 生成直播流数据
        live_streams = self.generate_mock_streams()
        results.extend(live_streams)
        
        # 为每个直播流生成内容
        for stream in live_streams:
            if stream.get('status') == 'live':
                content = self.generate_mock_content(stream['stream_id'])
                results.extend(content)
                
        logger.info(f"Generated {len(results)} mock data items")
        return results
    
    def generate_mock_streams(self) -> List[Dict[str, Any]]:
        """生成模拟直播流数据"""
        streams = []
        base_time = datetime.utcnow()
        
        for i in range(random.randint(5, 15)):
            stream_id = f"stream_{i:03d}"
            is_live = random.choice([True, True, False])  # 2/3 概率为直播中
            
            # 生成随机标题
            topics = random.sample(self.chinese_topics, random.randint(1, 3))
            title = f"{'/'.join(topics)} 市场分析与投资策略"
            
            # 生成随机观众数
            viewer_count = random.randint(100, 10000)
            
            # 生成时间
            start_time = base_time - timedelta(hours=random.randint(1, 6))
            end_time = start_time + timedelta(hours=random.randint(1, 4)) if not is_live else None
            
            stream_data = {
                'stream_id': stream_id,
                'title': title,
                'viewer_count': viewer_count,
                'status': 'live' if is_live else 'scheduled',
                'platform_source': 'gelonghui',
                'thumbnail_url': f"https://mock-gelonghui.com/thumbnails/{stream_id}.jpg",
                'channel_id': f"channel_{random.randint(1, 10)}",
                'channel_name': random.choice(self.user_names),
                'start_time': start_time,
                'end_time': end_time,
                'scraped_at': datetime.utcnow()
            }
            
            streams.append(stream_data)
        
        return streams
    
    def generate_mock_content(self, stream_id: str) -> List[Dict[str, Any]]:
        """为直播流生成模拟内容"""
        content = []
        base_time = datetime.utcnow()
        
        # 生成聊天消息
        for i in range(random.randint(20, 100)):
            # 生成随机时间（最近1小时内）
            message_time = base_time - timedelta(minutes=random.randint(0, 60))
            
            # 生成随机消息
            message = self.generate_random_message()
            
            # 提取话题标签
            hashtags = self.extract_hashtags_from_message(message)
            
            # 提取用户提及
            mentions = self.extract_mentions_from_message(message)
            
            # 情感分析
            sentiment = self.analyze_sentiment_mock(message)
            
            content_item = {
                'stream_id': stream_id,
                'timestamp': message_time,
                'content_type': 'chat',
                'text_content': message,
                'hashtags': hashtags,
                'mentions': mentions,
                'sentiment_score': sentiment,
                'user_id': f"user_{random.randint(1000, 9999)}",
                'username': random.choice(self.user_names),
                'message_type': 'text',
                'scraped_at': datetime.utcnow()
            }
            
            content.append(content_item)
        
        # 生成描述信息
        description = self.generate_stream_description()
        hashtags_desc = self.extract_hashtags_from_message(description)
        sentiment_desc = self.analyze_sentiment_mock(description)
        
        content.append({
            'stream_id': stream_id,
            'timestamp': base_time,
            'content_type': 'description',
            'text_content': description,
            'hashtags': hashtags_desc,
            'mentions': [],
            'sentiment_score': sentiment_desc,
            'scraped_at': datetime.utcnow()
        })
        
        return content
    
    def generate_random_message(self) -> str:
        """生成随机聊天消息"""
        message_types = [
            self.generate_topic_discussion,
            self.generate_question,
            self.generate_opinion,
            self.generate_reaction
        ]
        
        message_type = random.choice(message_types)
        return message_type()
    
    def generate_topic_discussion(self) -> str:
        """生成话题讨论消息"""
        topics = random.sample(self.chinese_topics, random.randint(1, 2))
        sentiment_word = random.choice(self.positive_words + self.negative_words + self.neutral_words)
        
        templates = [
            f"关于{topics[0]}的看法，我觉得{sentiment_word}，大家怎么看？",
            f"{topics[0]}最近走势不错，{sentiment_word}，有没有人一起讨论？",
            f"关注{topics[0]}的朋友举个手，{sentiment_word}的来聊聊",
            f"刚看了{topics[0]}的新闻，{sentiment_word}，求大神分析"
        ]
        
        return random.choice(templates)
    
    def generate_question(self) -> str:
        """生成问题消息"""
        topics = random.sample(self.chinese_topics, random.randint(1, 2))
        
        templates = [
            f"有谁知道{topics[0]}最近的政策变化吗？",
            f"{topics[0]}这个板块还能追吗？",
            f"请教一下，{topics[0]}和{topics[1]}哪个更有潜力？",
            f"新手求问，{topics[0]}应该怎么入手？"
        ]
        
        return random.choice(templates)
    
    def generate_opinion(self) -> str:
        """生成观点消息"""
        topics = random.sample(self.chinese_topics, random.randint(1, 2))
        sentiment = random.choice(self.positive_words + self.negative_words)
        
        templates = [
            f"我觉得{topics[0]}很有潜力，{sentiment}！",
            f"{topics[0]}这个方向我长期看好，{sentiment}！",
            f"说实话，{topics[0]}现在有点危险，{sentiment}！",
            f"个人观点：{topics[0]}短期回调是机会，{sentiment}！"
        ]
        
        return random.choice(templates)
    
    def generate_reaction(self) -> str:
        """生成反应消息"""
        reactions = [
            "👍", "👏", "🎉", "🔥", "💯", "🤔", "😅", "😂", "😮", "😱"
        ]
        
        templates = [
            f"{random.choice(reactions)} {random.choice(self.chinese_topics)}",
            f"{random.choice(reactions)} {random.choice(self.english_topics)}",
            f"{random.choice(reactions)} 说得好！",
            f"{random.choice(reactions)} 学到了！"
        ]
        
        return random.choice(templates)
    
    def generate_stream_description(self) -> str:
        """生成直播描述"""
        topics = random.sample(self.chinese_topics, random.randint(2, 4))
        sentiment = random.choice(self.positive_words)
        
        templates = [
            f"本期直播将深入分析{', '.join(topics)}等热门话题，{sentiment}！",
            f"欢迎来到直播间，今天我们聊{', '.join(topics)}，{sentiment}！",
            f"实时解读{', '.join(topics)}市场动态，{sentiment}！",
            f"专业分析{', '.join(topics)}投资机会，{sentiment}！"
        ]
        
        return random.choice(templates)
    
    def extract_hashtags_from_message(self, message: str) -> List[str]:
        """从消息中提取话题标签"""
        hashtags = []
        
        # 从中文话题中匹配
        for topic in self.chinese_topics:
            if topic in message:
                hashtags.append(topic)
        
        # 从英文话题中匹配
        for topic in self.english_topics:
            if topic.lower() in message.lower():
                hashtags.append(topic)
        
        # 随机添加一些额外的话题
        if random.random() > 0.5:
            extra_topics = random.sample(self.chinese_topics, random.randint(0, 2))
            hashtags.extend(extra_topics)
        
        return list(set(hashtags))  # 去重
    
    def extract_mentions_from_message(self, message: str) -> List[str]:
        """从消息中提取用户提及"""
        mentions = []
        
        # 随机决定是否包含提及
        if random.random() > 0.7:
            mention_user = random.choice(self.user_names)
            mentions.append(mention_user)
        
        return mentions
    
    def analyze_sentiment_mock(self, message: str) -> float:
        """模拟情感分析"""
        positive_count = sum(1 for word in self.positive_words if word in message)
        negative_count = sum(1 for word in self.negative_words if word in message)
        
        if positive_count > negative_count:
            return round(random.uniform(0.2, 1.0), 2)
        elif negative_count > positive_count:
            return round(random.uniform(-1.0, -0.2), 2)
        else:
            return round(random.uniform(-0.2, 0.2), 2)