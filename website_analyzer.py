#!/usr/bin/env python3
"""
Website Analysis Tool for 格隆汇 Live Streaming Platform
Analyzes website structure, technology stack, and real-time mechanisms
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
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
                'html_structure': self._analyze_html_structure(response.content),
                'javascript_frameworks': self._detect_javascript_frameworks(response.content),
                'build_tools': self._detect_build_tools(response.content),
                'meta_tags': self._extract_meta_tags(response.content),
                'security_headers': self._check_security_headers(response.headers)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing basic structure: {e}")
            return None
    
    def _analyze_html_structure(self, content):
        """Analyze HTML structure"""
        soup = BeautifulSoup(content, 'html.parser')
        
        structure = {
            'title': soup.title.string if soup.title else 'No title',
            'headings': {
                'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
            },
            'forms': len(soup.find_all('form')),
            'links': len(soup.find_all('a')),
            'scripts': len(soup.find_all('script')),
            'images': len(soup.find_all('img')),
            'interactive_elements': len(soup.find_all(['button', 'input', 'select', 'textarea']))
        }
        
        return structure
    
    def _detect_javascript_frameworks(self, content):
        """Detect JavaScript frameworks"""
        frameworks = []
        content_str = str(content)
        
        framework_patterns = {
            'React': [r'react', r'jsx', r'virtual-dom'],
            'Vue.js': [r'vue', r'v-bind', r'v-model'],
            'Angular': [r'angular', r'ng-app', r'ng-model'],
            'jQuery': [r'jquery', r'\$\(', r'\.ajax'],
            'Svelte': [r'svelte', r'\$:', r'\$bindable'],
            'Next.js': [r'next', r'getStaticProps', r'getServerSideProps'],
            'Nuxt.js': [r'nuxt', r'asyncData', r'fetch']
        }
        
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    frameworks.append(framework)
                    break
        
        return list(set(frameworks))
    
    def _detect_build_tools(self, content):
        """Detect build tools and bundlers"""
        tools = []
        content_str = str(content)
        
        tool_patterns = {
            'Webpack': [r'webpack', r'__webpack_require__'],
            'Vite': [r'vite', r'import\.meta'],
            'Parcel': [r'parcel', r'parcelRequire'],
            'Rollup': [r'rollup', r'__ROLLUP_REEXPORT__'],
            'Babel': [r'babel', r'babelHelpers'],
            'TypeScript': [r'typescript', r'\.ts$', r'\.tsx$']
        }
        
        for tool, patterns in tool_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    tools.append(tool)
                    break
        
        return list(set(tools))
    
    def _extract_meta_tags(self, content):
        """Extract meta tags"""
        soup = BeautifulSoup(content, 'html.parser')
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content_attr = meta.get('content')
            if name and content_attr:
                meta_tags[name] = content_attr
        
        return meta_tags
    
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
    
    def analyze_network_requests(self):
        """Analyze network requests and API endpoints"""
        logger.info("Analyzing network requests and API endpoints")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'external_scripts': [],
                'api_endpoints': [],
                'websocket_connections': [],
                'ajax_requests': [],
                'cdn_usage': [],
                'tracking_scripts': []
            }
            
            # Analyze script sources
            for script in soup.find_all('script'):
                src = script.get('src')
                if src:
                    full_url = urljoin(self.base_url, src)
                    analysis['external_scripts'].append(full_url)
                    
                    # Check for API endpoints in script URLs
                    if '/api/' in full_url or '/v1/' in full_url or '/v2/' in full_url:
                        analysis['api_endpoints'].append(full_url)
                    
                    # Check for WebSocket connections
                    if 'ws://' in full_url or 'wss://' in full_url:
                        analysis['websocket_connections'].append(full_url)
                    
                    # Check for CDN usage
                    if any(cdn in full_url for cdn in ['cdn.', 'static.', 'assets.']):
                        analysis['cdn_usage'].append(full_url)
                    
                    # Check for tracking scripts
                    if any(tracker in full_url.lower() for tracker in ['google-analytics', 'facebook', 'twitter', 'linkedin']):
                        analysis['tracking_scripts'].append(full_url)
            
            # Analyze links for API endpoints
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/api/' in href or '/v1/' in href or '/v2/' in href:
                    full_url = urljoin(self.base_url, href)
                    analysis['api_endpoints'].append(full_url)
            
            # Analyze form actions
            for form in soup.find_all('form'):
                action = form.get('action')
                if action:
                    full_url = urljoin(self.base_url, action)
                    analysis['api_endpoints'].append(full_url)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing network requests: {e}")
            return None
    
    def analyze_real_time_features(self):
        """Analyze real-time features and update mechanisms"""
        logger.info("Analyzing real-time features and update mechanisms")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'websocket_indicators': [],
                'polling_indicators': [],
                'server_sent_events': [],
                'long_polling': [],
                'real_time_keywords': [],
                'update_intervals': []
            }
            
            content_str = str(response.content)
            
            # Check for WebSocket indicators
            ws_patterns = [
                r'new WebSocket\(',
                r'WebSocket\(',
                r'ws://',
                r'wss://',
                r'WebSocket\.OPEN',
                r'WebSocket\.CLOSED'
            ]
            
            for pattern in ws_patterns:
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    analysis['websocket_indicators'].append({
                        'pattern': pattern,
                        'matches': len(matches)
                    })
            
            # Check for polling indicators
            polling_patterns = [
                r'setInterval\(',
                r'setTimeout\(',
                r'ajax.*interval',
                r'polling',
                r'refresh.*interval'
            ]
            
            for pattern in polling_patterns:
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    analysis['polling_indicators'].append({
                        'pattern': pattern,
                        'matches': len(matches)
                    })
            
            # Check for Server-Sent Events
            sse_patterns = [
                r'new EventSource\(',
                r'EventSource\(',
                r'source\.onmessage',
                r'source\.onopen'
            ]
            
            for pattern in sse_patterns:
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    analysis['server_sent_events'].append({
                        'pattern': pattern,
                        'matches': len(matches)
                    })
            
            # Check for real-time keywords
            real_time_keywords = [
                'live', '实时', 'real-time', 'streaming', 'websocket',
                'polling', 'sse', 'eventsource', 'push', 'notification'
            ]
            
            for keyword in real_time_keywords:
                count = len(re.findall(keyword, content_str, re.IGNORECASE))
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
                r'delay:\s*(\d+)'
            ]
            
            for pattern in interval_patterns:
                matches = re.findall(pattern, content_str, re.IGNORECASE)
                if matches:
                    analysis['update_intervals'].extend([int(m) for m in matches if m.isdigit()])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing real-time features: {e}")
            return None
    
    def analyze_performance_features(self):
        """Analyze performance optimization features"""
        logger.info("Analyzing performance optimization features")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'caching_strategies': [],
                'lazy_loading': [],
                'compression': [],
                'cdn_usage': [],
                'optimization_techniques': []
            }
            
            content_str = str(response.content)
            
            # Check for caching strategies
            cache_patterns = [
                r'cache-control',
                r'expires',
                r'etag',
                r'last-modified',
                r'if-modified-since'
            ]
            
            for pattern in cache_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    analysis['caching_strategies'].append(pattern)
            
            # Check for lazy loading
            lazy_patterns = [
                r'loading="lazy"',
                r'data-src',
                r'intersectionobserver',
                r'onscroll',
                r'virtualization'
            ]
            
            for pattern in lazy_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    analysis['lazy_loading'].append(pattern)
            
            # Check for compression
            compression_headers = response.headers.get('Content-Encoding', '')
            if compression_headers:
                analysis['compression'].append(compression_headers)
            
            # Check for CDN usage
            for script in soup.find_all('script'):
                src = script.get('src')
                if src:
                    if any(cdn in src for cdn in ['cdn.', 'static.', 'assets.']):
                        analysis['cdn_usage'].append(src)
            
            # Check for optimization techniques
            optimization_patterns = [
                r'minified',
                r'bundle',
                r'chunk',
                r'code-splitting',
                r'tree-shaking',
                r'gzip',
                r'brotli'
            ]
            
            for pattern in optimization_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    analysis['optimization_techniques'].append(pattern)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance features: {e}")
            return None
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        logger.info("Generating comprehensive analysis report")
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'target_url': self.base_url,
            'basic_structure': self.analyze_basic_structure(),
            'network_analysis': self.analyze_network_requests(),
            'real_time_features': self.analyze_real_time_features(),
            'performance_analysis': self.analyze_performance_features()
        }
        
        return report

def main():
    """Main function to run the website analysis"""
    target_url = 'https://www.gelonghui.com/live?channelId=all'
    
    analyzer = WebsiteAnalyzer(target_url)
    report = analyzer.generate_report()
    
    # Save report to JSON file
    with open('website_analysis.json', 'w', encoding='utf-8') as f:
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
        print(f"  JavaScript Frameworks: {', '.join(report['basic_structure']['javascript_frameworks'])}")
        print(f"  Build Tools: {', '.join(report['basic_structure']['build_tools'])}")
    
    if report['real_time_features']:
        print(f"\nReal-time Features:")
        print(f"  WebSocket Indicators: {len(report['real_time_features']['websocket_indicators'])}")
        print(f"  Polling Indicators: {len(report['real_time_features']['polling_indicators'])}")
        print(f"  Real-time Keywords: {len(report['real_time_features']['real_time_keywords'])}")
        print(f"  Update Intervals: {report['real_time_features']['update_intervals']}")
    
    print(f"\nDetailed report saved to: website_analysis.json")

if __name__ == '__main__':
    main()