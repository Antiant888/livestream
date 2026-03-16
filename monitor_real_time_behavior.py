#!/usr/bin/env python3
"""
Real-time Behavior Monitor for 格隆汇 Live Streaming Platform
Captures actual runtime network traffic, WebSocket connections, and update mechanisms
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeBehaviorMonitor:
    def __init__(self):
        self.network_requests = []
        self.websocket_connections = []
        self.sse_connections = []
        self.dom_changes = []
        self.polling_patterns = []
        self.update_intervals = []
        
    async def start_monitoring(self, url="https://www.gelonghui.com/live?channelId=all", duration=120):
        """Start comprehensive monitoring of real-time behavior"""
        logger.info(f"Starting real-time behavior monitoring for {duration} seconds")
        logger.info(f"Target URL: {url}")
        
        async with async_playwright() as p:
            # Launch browser with detailed logging
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--enable-logging",
                    "--log-level=0",
                    "--enable-precise-memory-info",
                    "--enable-web-bluetooth",
                    "--enable-webvr"
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True
            )
            
            # Enable network monitoring
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            
            page = await context.new_page()
            
            # Set up event listeners
            self.setup_event_listeners(page)
            
            # Navigate to target page
            logger.info("Navigating to target page...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for initial content to load
            await page.wait_for_timeout(5000)
            
            # Start monitoring
            logger.info("Starting monitoring phase...")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Monitor DOM changes
                await self.monitor_dom_changes(page)
                
                # Check for new network requests
                await page.wait_for_timeout(1000)  # Check every second
                
            # Stop monitoring and collect data
            logger.info("Stopping monitoring...")
            await context.tracing.stop(path="trace.zip")
            
            await browser.close()
            
            # Analyze collected data
            self.analyze_behavior()
            
            return {
                'network_requests': self.network_requests,
                'websocket_connections': self.websocket_connections,
                'sse_connections': self.sse_connections,
                'dom_changes': self.dom_changes,
                'polling_patterns': self.polling_patterns,
                'update_intervals': self.update_intervals
            }
    
    def setup_event_listeners(self, page):
        """Set up event listeners for comprehensive monitoring"""
        
        # Monitor network requests
        page.on("request", self.handle_request)
        page.on("response", self.handle_response)
        
        # Monitor WebSocket connections
        page.on("websocket", self.handle_websocket)
        
        # Monitor console messages for debugging
        page.on("console", self.handle_console_message)
        
        # Monitor page errors
        page.on("pageerror", self.handle_page_error)
        
        # Inject JavaScript to monitor client-side behavior
        self.inject_monitoring_scripts(page)
    
    def handle_request(self, request):
        """Handle network requests"""
        request_data = {
            'timestamp': time.time(),
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'resource_type': request.resource_type,
            'is_navigation_request': request.is_navigation_request()
        }
        
        self.network_requests.append(request_data)
        
        # Check for polling patterns
        if self.is_polling_request(request.url, request.method):
            self.polling_patterns.append(request_data)
    
    def handle_response(self, response):
        """Handle network responses"""
        # Log responses for analysis
        response_data = {
            'timestamp': time.time(),
            'url': response.url,
            'status': response.status,
            'headers': dict(response.headers)
        }
        
        # Check if this is a live update response
        if self.is_live_update_response(response):
            logger.info(f"Live update detected: {response.url}")
    
    def handle_websocket(self, websocket):
        """Handle WebSocket connections"""
        ws_data = {
            'timestamp': time.time(),
            'url': websocket.url,
            'state': 'connected'
        }
        
        self.websocket_connections.append(ws_data)
        
        # Monitor WebSocket messages
        websocket.on("framesent", lambda frame: self.handle_ws_message(websocket.url, frame, 'sent'))
        websocket.on("framereceived", lambda frame: self.handle_ws_message(websocket.url, frame, 'received'))
        websocket.on("close", lambda: self.handle_ws_close(websocket.url))
    
    def handle_console_message(self, msg):
        """Handle console messages"""
        if 'WebSocket' in msg.text or 'EventSource' in msg.text or 'polling' in msg.text.lower():
            logger.info(f"Console message: {msg.text}")
    
    def handle_page_error(self, error):
        """Handle page errors"""
        logger.error(f"Page error: {error}")
    
    def handle_ws_message(self, ws_url, frame, direction):
        """Handle WebSocket messages"""
        message_data = {
            'timestamp': time.time(),
            'websocket_url': ws_url,
            'direction': direction,
            'frame': frame
        }
        logger.info(f"WebSocket {direction}: {frame}")
    
    def handle_ws_close(self, ws_url):
        """Handle WebSocket closure"""
        logger.info(f"WebSocket closed: {ws_url}")
    
    def inject_monitoring_scripts(self, page):
        """Inject JavaScript to monitor client-side behavior"""
        
        # Monitor fetch/XHR requests
        fetch_monitor_script = """
        (function() {
            const originalFetch = window.fetch;
            window.fetch = function(input, init) {
                const url = typeof input === 'string' ? input : input.url;
                const method = init && init.method ? init.method : 'GET';
                
                // Log fetch requests
                console.log('FETCH_REQUEST:', {
                    url: url,
                    method: method,
                    timestamp: Date.now()
                });
                
                return originalFetch.apply(this, arguments);
            };
            
            // Monitor XMLHttpRequest
            const originalXHR = window.XMLHttpRequest;
            const open = originalXHR.prototype.open;
            originalXHR.prototype.open = function(method, url) {
                console.log('XHR_REQUEST:', {
                    method: method,
                    url: url,
                    timestamp: Date.now()
                });
                return open.apply(this, arguments);
            };
        })();
        """
        
        # Monitor DOM changes
        dom_monitor_script = """
        (function() {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        console.log('DOM_CHANGE:', {
                            type: 'new_content_added',
                            timestamp: Date.now(),
                            added_nodes: mutation.addedNodes.length
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        })();
        """
        
        # Monitor polling patterns
        polling_monitor_script = """
        (function() {
            let pollingIntervals = [];
            
            const originalSetInterval = window.setInterval;
            window.setInterval = function(callback, delay) {
                pollingIntervals.push({
                    delay: delay,
                    timestamp: Date.now()
                });
                
                console.log('POLLING_INTERVAL:', {
                    delay: delay,
                    timestamp: Date.now()
                });
                
                return originalSetInterval.call(this, callback, delay);
            };
        })();
        """
        
        # Inject scripts
        page.add_init_script(fetch_monitor_script)
        page.add_init_script(dom_monitor_script)
        page.add_init_script(polling_monitor_script)
    
    async def monitor_dom_changes(self, page):
        """Monitor DOM changes for new content"""
        try:
            # Check for new live news items
            new_items = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.live-news-item, .news-item, [data-live-item]');
                    return Array.from(items).map(item => ({
                        id: item.getAttribute('data-id') || item.id,
                        text: item.textContent.substring(0, 100),
                        timestamp: Date.now()
                    }));
                }
            """)
            
            if new_items:
                self.dom_changes.extend(new_items)
                
        except Exception as e:
            logger.error(f"Error monitoring DOM changes: {e}")
    
    def is_polling_request(self, url, method):
        """Check if request is part of polling mechanism"""
        # Check for API endpoint patterns
        api_patterns = [
            '/api/live-channels/all/lives/v4',
            '/api/live-updates',
            '/api/updates'
        ]
        
        return (method == 'GET' and any(pattern in url for pattern in api_patterns))
    
    def is_live_update_response(self, response):
        """Check if response contains live update data"""
        try:
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                # This is likely a live update response
                return True
        except:
            pass
        return False
    
    def analyze_behavior(self):
        """Analyze collected behavior data"""
        logger.info("\n=== BEHAVIOR ANALYSIS RESULTS ===")
        
        # Analyze network requests
        logger.info(f"Total network requests: {len(self.network_requests)}")
        logger.info(f"Polling patterns detected: {len(self.polling_patterns)}")
        
        # Analyze WebSocket connections
        logger.info(f"WebSocket connections: {len(self.websocket_connections)}")
        for ws in self.websocket_connections:
            logger.info(f"  - {ws['url']} (connected at {datetime.fromtimestamp(ws['timestamp'])})")
        
        # Analyze polling intervals
        if self.polling_patterns:
            intervals = [req['url'] for req in self.polling_patterns]
            logger.info(f"Polling endpoints: {list(set(intervals))}")
        
        # Analyze DOM changes
        logger.info(f"DOM changes detected: {len(self.dom_changes)}")
        
        # Save detailed analysis
        self.save_analysis_report()
    
    def save_analysis_report(self):
        """Save detailed analysis report"""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'network_requests': self.network_requests,
            'websocket_connections': self.websocket_connections,
            'sse_connections': self.sse_connections,
            'dom_changes': self.dom_changes,
            'polling_patterns': self.polling_patterns,
            'summary': {
                'total_requests': len(self.network_requests),
                'websocket_count': len(self.websocket_connections),
                'polling_count': len(self.polling_patterns),
                'dom_changes_count': len(self.dom_changes)
            }
        }
        
        with open('real_time_behavior_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info("Detailed analysis saved to: real_time_behavior_analysis.json")

async def main():
    """Main function to run real-time behavior monitoring"""
    monitor = RealTimeBehaviorMonitor()
    
    print("格隆汇 Live Streaming Platform - Real-time Behavior Analysis")
    print("=" * 60)
    print("This tool will:")
    print("1. Launch a browser and navigate to the live page")
    print("2. Monitor all network traffic for 2 minutes")
    print("3. Detect WebSocket connections and polling patterns")
    print("4. Analyze DOM changes and update mechanisms")
    print("5. Generate a comprehensive technical report")
    print()
    
    input("Press Enter to start monitoring...")
    
    try:
        results = await monitor.start_monitoring(duration=120)  # Monitor for 2 minutes
        
        print("\n" + "=" * 60)
        print("MONITORING COMPLETE")
        print("=" * 60)
        print("Results saved to:")
        print("- real_time_behavior_analysis.json (detailed data)")
        print("- trace.zip (browser trace with screenshots)")
        print()
        print("Key findings:")
        print(f"- Network requests: {len(results['network_requests'])}")
        print(f"- WebSocket connections: {len(results['websocket_connections'])}")
        print(f"- Polling patterns: {len(results['polling_patterns'])}")
        print(f"- DOM changes: {len(results['dom_changes'])}")
        
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())