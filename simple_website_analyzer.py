#!/usr/bin/env python3
"""
Simple Website Analysis Tool for 格隆汇 Live Streaming Platform
Focuses on core website structure and real-time mechanisms without heavy dependencies
"""

import requests
import json
import re
import time
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleWebsiteAnalyzer:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def analyze_basic_structure(self):
        """Analyze basic website structure and technology stack"""
        logger.info(f"Analyzing basic structure of {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            analysis = {
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type', 'Unknown'),
                'server': response.headers.get('Server', 'Unknown'),
                'content_length': len(response.content),
                'charset': response.encoding,
                'html_content': response.text[:5000],  # First 5000 chars for analysis
                'security_headers': self._check_security_headers(response.headers)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing basic structure: {e}")
            return None
    
    def _check_security_headers(self, headers):
        """Check for security headers"""
        security_headers = {
            'X-Frame-Options': headers.get('X-Frame-Options', 'Missing'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Missing'),
            'X-XSS-Protection': headers.get('X-XSS-Protection', 'Missing'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Missing'),
            'Content-Security-Policy': headers.get('Content-Security-Policy', 'Missing'),
            'Referrer-Policy': headers.get('Referrer-Policy', 'Missing')
        }
        
        return security_headers
    
    def analyze_javascript_frameworks(self, content):
        """Detect JavaScript frameworks from HTML content"""
        frameworks = []
        
        framework_patterns = {
            'React': [r'react', r'jsx', r'virtual-dom', r'__NEXT_DATA__'],
            'Vue.js': [r'vue', r'v-bind', r'v-model', r'vue-router'],
            'Angular': [r'angular', r'ng-app', r'ng-model', r'@angular'],
            'jQuery': [r'jquery', r'\$\(', r'\.ajax', r'\.ready'],
            'Svelte': [r'svelte', r'\$:', r'\$bindable', r'svelte:'],
            'Next.js': [r'next', r'getStaticProps', r'getServerSideProps', r'next/router'],
            'Nuxt.js': [r'nuxt', r'asyncData', r'fetch', r'nuxtServerInit'],
            'Webpack': [r'webpack', r'__webpack_require__', r'webpackChunkName'],
            'Vite': [r'vite', r'import\.meta', r'vite-plugin'],
            'TypeScript': [r'typescript', r'\.ts$', r'\.tsx$', r'type ']
        }
        
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    frameworks.append(framework)
                    break
        
        return list(set(frameworks))
    
    def analyze_network_requests(self, content):
        """Analyze network requests and API endpoints from HTML content"""
        analysis = {
            'external_scripts': [],
            'api_endpoints': [],
            'websocket_connections': [],
            'cdn_usage': [],
            'tracking_scripts': [],
            'form_actions': []
        }
        
        # Extract script sources
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\']'
        scripts = re.findall(script_pattern, content, re.IGNORECASE)
        
        for src in scripts:
            full_url = urljoin(self.base_url, src)
            analysis['external_scripts'].append(full_url)
            
            # Check for API endpoints in script URLs
            if '/api/' in full_url or '/v1/' in full_url or '/v2/' in full_url:
                analysis['api_endpoints'].append(full_url)
            
            # Check for WebSocket connections
            if 'ws://' in full_url or 'wss://' in full_url:
                analysis['websocket_connections'].append(full_url)
            
            # Check for CDN usage
            if any(cdn in full_url for cdn in ['cdn.', 'static.', 'assets.', 'cloudfront']):
                analysis['cdn_usage'].append(full_url)
            
            # Check for tracking scripts
            if any(tracker in full_url.lower() for tracker in ['google-analytics', 'facebook', 'twitter', 'linkedin', 'gtag', 'analytics']):
                analysis['tracking_scripts'].append(full_url)
        
        # Extract form actions
        form_pattern = r'<form[^>]*action=["\']([^"\']+)["\']'
        forms = re.findall(form_pattern, content, re.IGNORECASE)
        
        for action in forms:
            full_url = urljoin(self.base_url, action)
            analysis['form_actions'].append(full_url)
            if '/api/' in full_url or '/v1/' in full_url or '/v2/' in full_url:
                analysis['api_endpoints'].append(full_url)
        
        # Extract links that might be API endpoints
        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, content, re.IGNORECASE)
        
        for href in links:
            if '/api/' in href or '/v1/' in href or '/v2/' in href:
                full_url = urljoin(self.base_url, href)
                analysis['api_endpoints'].append(full_url)
        
        # Remove duplicates
        analysis['api_endpoints'] = list(set(analysis['api_endpoints']))
        
        return analysis
    
    def analyze_real_time_features(self, content):
        """Analyze real-time features and update mechanisms"""
        analysis = {
            'websocket_indicators': [],
            'polling_indicators': [],
            'server_sent_events': [],
            'real_time_keywords': [],
            'update_intervals': [],
            'ajax_patterns': [],
            'event_listeners': []
        }
        
        # Check for WebSocket indicators
        ws_patterns = [
            r'new WebSocket\(',
            r'WebSocket\(',
            r'ws://',
            r'wss://',
            r'WebSocket\.OPEN',
            r'WebSocket\.CLOSED',
            r'ws\.onmessage',
            r'ws\.onopen',
            r'ws\.onclose'
        ]
        
        for pattern in ws_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['websocket_indicators'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
        
        # Check for polling indicators
        polling_patterns = [
            r'setInterval\(',
            r'setTimeout\(',
            r'ajax.*interval',
            r'polling',
            r'refresh.*interval',
            r'window\.setInterval',
            r'window\.setTimeout'
        ]
        
        for pattern in polling_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['polling_indicators'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
        
        # Check for Server-Sent Events
        sse_patterns = [
            r'new EventSource\(',
            r'EventSource\(',
            r'source\.onmessage',
            r'source\.onopen',
            r'source\.onerror',
            r'EventSource\.CLOSED'
        ]
        
        for pattern in sse_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['server_sent_events'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
        
        # Check for real-time keywords
        real_time_keywords = [
            'live', '实时', 'real-time', 'streaming', 'websocket',
            'polling', 'sse', 'eventsource', 'push', 'notification',
            'subscribe', 'publish', 'broadcast', 'channel', 'message'
        ]
        
        for keyword in real_time_keywords:
            count = len(re.findall(keyword, content, re.IGNORECASE))
            if count > 0:
                analysis['real_time_keywords'].append({
                    'keyword': keyword,
                    'count': count
                })
        
        # Check for update intervals
        interval_patterns = [
            r'setInterval\([^,]+,\s*(\d+)',
            r'setTimeout\([^,]+,\s*(\d+)',
            r'interval:\s*(\d+)',
            r'delay:\s*(\d+)',
            r'frequency:\s*(\d+)',
            r'rate:\s*(\d+)'
        ]
        
        for pattern in interval_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                intervals = [int(m) for m in matches if m.isdigit()]
                analysis['update_intervals'].extend(intervals)
        
        # Check for AJAX patterns
        ajax_patterns = [
            r'\$\.ajax\(',
            r'fetch\(',
            r'XMLHttpRequest\(',
            r'axios\.',
            r'$.get\(',
            r'$.post\(',
            r'$.getJSON\('
        ]
        
        for pattern in ajax_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['ajax_patterns'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
        
        # Check for event listeners
        event_patterns = [
            r'addEventListener\(',
            r'onclick=',
            r'onload=',
            r'onmessage=',
            r'onopen=',
            r'onclose=',
            r'\.click\(',
            r'\.submit\('
        ]
        
        for pattern in event_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['event_listeners'].append({
                    'pattern': pattern,
                    'count': len(matches)
                })
        
        return analysis
    
    def analyze_performance_features(self, content, headers):
        """Analyze performance optimization features"""
        analysis = {
            'caching_strategies': [],
            'lazy_loading': [],
            'compression': [],
            'cdn_usage': [],
            'optimization_techniques': [],
            'image_optimization': []
        }
        
        # Check for caching strategies
        cache_patterns = [
            r'cache-control',
            r'expires',
            r'etag',
            r'last-modified',
            r'if-modified-since',
            r'no-cache',
            r'max-age'
        ]
        
        for pattern in cache_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['caching_strategies'].append(pattern)
        
        # Check for lazy loading
        lazy_patterns = [
            r'loading="lazy"',
            r'data-src',
            r'intersectionobserver',
            r'onscroll',
            r'virtualization',
            r'lazy-load',
            r'data-lazy'
        ]
        
        for pattern in lazy_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['lazy_loading'].append(pattern)
        
        # Check for compression
        compression_headers = headers.get('Content-Encoding', '')
        if compression_headers:
            analysis['compression'].append(compression_headers)
        
        # Check for CDN usage (from content analysis)
        cdn_patterns = [
            r'cdn\.',
            r'static\.',
            r'assets\.',
            r'cloudfront',
            r'akamai',
            r'cloudflare'
        ]
        
        for pattern in cdn_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['cdn_usage'].append(pattern)
        
        # Check for optimization techniques
        optimization_patterns = [
            r'minified',
            r'bundle',
            r'chunk',
            r'code-splitting',
            r'tree-shaking',
            r'gzip',
            r'brotli',
            r'optimization',
            r'performance'
        ]
        
        for pattern in optimization_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['optimization_techniques'].append(pattern)
        
        # Check for image optimization
        image_patterns = [
            r'webp',
            r'lazyload',
            r'srcset',
            r'picture',
            r'loading="lazy"',
            r'data-srcset'
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['image_optimization'].append(pattern)
        
        return analysis
    
    def analyze_security_features(self, content, headers):
        """Analyze security features and anti-scraping measures"""
        analysis = {
            'anti_scraping_indicators': [],
            'bot_detection': [],
            'rate_limiting': [],
            'captcha_indicators': [],
            'user_agent_checks': [],
            'javascript_obfuscation': []
        }
        
        # Check for anti-scraping indicators
        anti_scraping_patterns = [
            r'bot',
            r'scraper',
            r'crawler',
            r'spider',
            r'robot',
            r'automated',
            r'headless',
            r'phantom',
            r'puppeteer'
        ]
        
        for pattern in anti_scraping_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['anti_scraping_indicators'].append(pattern)
        
        # Check for bot detection
        bot_detection_patterns = [
            r'navigator\.',
            r'window\.',
            r'document\.',
            r'location\.',
            r'screen\.',
            r'performance\.',
            r'crypto\.',
            r'localStorage',
            r'sessionStorage'
        ]
        
        for pattern in bot_detection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['bot_detection'].append(pattern)
        
        # Check for rate limiting indicators
        rate_limiting_patterns = [
            r'rate.*limit',
            r'too.*many.*requests',
            r'429',
            r'wait',
            r'delay',
            r'throttle',
            r'limit.*request'
        ]
        
        for pattern in rate_limiting_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['rate_limiting'].append(pattern)
        
        # Check for CAPTCHA indicators
        captcha_patterns = [
            r'captcha',
            r'recaptcha',
            r'hcaptcha',
            r'challenge',
            r'verify.*human',
            r'robot.*check'
        ]
        
        for pattern in captcha_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['captcha_indicators'].append(pattern)
        
        # Check for user agent checks
        user_agent_patterns = [
            r'user.*agent',
            r'navigator\.userAgent',
            r'window\.navigator',
            r'browser.*check'
        ]
        
        for pattern in user_agent_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['user_agent_checks'].append(pattern)
        
        # Check for JavaScript obfuscation
        obfuscation_patterns = [
            r'eval\(',
            r'Function\(',
            r'\\u[0-9a-fA-F]{4}',
            r'atob\(',
            r'btoa\(',
            r'base64',
            r'obfuscate'
        ]
        
        for pattern in obfuscation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['javascript_obfuscation'].append(pattern)
        
        return analysis
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        logger.info("Generating comprehensive analysis report")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            report = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'target_url': self.base_url,
                'basic_structure': self.analyze_basic_structure(),
                'javascript_frameworks': self.analyze_javascript_frameworks(content),
                'network_analysis': self.analyze_network_requests(content),
                'real_time_features': self.analyze_real_time_features(content),
                'performance_analysis': self.analyze_performance_features(content, response.headers),
                'security_analysis': self.analyze_security_features(content, response.headers)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None

def main():
    """Main function to run the website analysis"""
    target_url = 'https://www.gelonghui.com/live?channelId=all'
    
    analyzer = SimpleWebsiteAnalyzer(target_url)
    report = analyzer.generate_report()
    
    if report:
        # Save report to JSON file
        with open('simple_website_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\n=== Website Analysis Summary ===")
        print(f"Target URL: {report['target_url']}")
        print(f"Analysis Time: {report['timestamp']}")
        
        if report['basic_structure']:
            print(f"\nBasic Structure:")
            print(f"  Status Code: {report['basic_structure']['status_code']}")
            print(f"  Content Type: {report['basic_structure']['content_type']}")
            print(f"  Server: {report['basic_structure']['server']}")
            print(f"  Content Length: {report['basic_structure']['content_length']} bytes")
            print(f"  JavaScript Frameworks: {', '.join(report['javascript_frameworks'])}")
        
        if report['real_time_features']:
            print(f"\nReal-time Features:")
            print(f"  WebSocket Indicators: {len(report['real_time_features']['websocket_indicators'])}")
            print(f"  Polling Indicators: {len(report['real_time_features']['polling_indicators'])}")
            print(f"  Real-time Keywords: {len(report['real_time_features']['real_time_keywords'])}")
            print(f"  Update Intervals: {report['real_time_features']['update_intervals']}")
        
        if report['security_analysis']:
            print(f"\nSecurity Features:")
            print(f"  Anti-scraping Indicators: {len(report['security_analysis']['anti_scraping_indicators'])}")
            print(f"  Bot Detection: {len(report['security_analysis']['bot_detection'])}")
            print(f"  CAPTCHA Indicators: {len(report['security_analysis']['captcha_indicators'])}")
        
        print(f"\nDetailed report saved to: simple_website_analysis.json")
    else:
        print("Failed to generate analysis report")

if __name__ == '__main__':
    main()