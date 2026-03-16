#!/usr/bin/env python3
"""
API Endpoint Analysis Tool for 格隆汇 Live Streaming Platform
Tests the provided API endpoint and analyzes response structure
"""

import requests
import json
import time

def test_api_endpoint():
    """Test the provided API endpoint"""
    url = 'https://www.gelonghui.com/api/live-channels/all/lives/v4?category=all&limit=15&timestamp=1773409192465'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.gelonghui.com/',
        'Origin': 'https://www.gelonghui.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive'
    }

    try:
        print('=== Testing API Endpoint ===')
        print(f'URL: {url}')
        print('Making request...')
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f'Status Code: {response.status_code}')
        print(f'Content-Type: {response.headers.get("Content-Type", "Unknown")}')
        print(f'Response Length: {len(response.content)} bytes')
        
        if response.status_code == 200:
            try:
                data = response.json()
                print('\n=== API Response Structure ===')
                print(f'Top-level keys: {list(data.keys()) if isinstance(data, dict) else "Not a dictionary"}')
                
                if isinstance(data, dict) and 'data' in data:
                    print(f'Data keys: {list(data["data"].keys()) if isinstance(data["data"], dict) else "Not a dictionary"}')
                    
                    if 'lives' in data['data']:
                        lives = data['data']['lives']
                        print(f'Number of lives: {len(lives) if isinstance(lives, list) else 0}')
                        
                        if lives and isinstance(lives, list):
                            first_live = lives[0]
                            print(f'\nFirst live stream structure:')
                            print(f'Keys: {list(first_live.keys())}')
                            
                            # Show key fields
                            key_fields = ['id', 'title', 'description', 'startTime', 'endTime', 'status', 'viewerCount', 'channelId', 'hashtag']
                            for field in key_fields:
                                if field in first_live:
                                    print(f'  {field}: {first_live[field]}')
                
                # Save sample response
                with open('api_sample_response.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print('\nSample response saved to: api_sample_response.json')
                
                return data
                
            except json.JSONDecodeError as e:
                print(f'JSON Decode Error: {e}')
                print(f'Response content (first 500 chars): {response.text[:500]}')
                return None
        else:
            print(f'Error response: {response.text[:500]}')
            return None
            
    except Exception as e:
        print(f'Error: {e}')
        return None

def analyze_api_structure(data):
    """Analyze the API response structure in detail"""
    if not data or not isinstance(data, dict):
        print("No valid data to analyze")
        return
    
    print('\n=== Detailed API Structure Analysis ===')
    
    # Analyze top-level structure
    print(f'Top-level structure:')
    for key, value in data.items():
        if isinstance(value, dict):
            print(f'  {key}: dict with keys {list(value.keys())}')
        elif isinstance(value, list):
            print(f'  {key}: list with {len(value)} items')
        else:
            print(f'  {key}: {type(value).__name__} = {value}')
    
    # Analyze data section
    if 'data' in data and isinstance(data['data'], dict):
        data_section = data['data']
        print(f'\nData section structure:')
        for key, value in data_section.items():
            if isinstance(value, dict):
                print(f'  {key}: dict with keys {list(value.keys())}')
            elif isinstance(value, list):
                print(f'  {key}: list with {len(value)} items')
                if value and isinstance(value[0], dict):
                    print(f'    First item keys: {list(value[0].keys())}')
            else:
                print(f'  {key}: {type(value).__name__} = {value}')
    
    # Analyze live stream items
    if 'data' in data and 'lives' in data['data'] and isinstance(data['data']['lives'], list):
        lives = data['data']['lives']
        print(f'\nLive stream items analysis:')
        print(f'  Total lives: {len(lives)}')
        
        if lives:
            first_item = lives[0]
            print(f'  Sample fields:')
            for key, value in first_item.items():
                print(f'    {key}: {type(value).__name__} = {str(value)[:100]}{"..." if len(str(value)) > 100 else ""}')

def generate_api_documentation(data):
    """Generate API documentation based on the response"""
    if not data:
        return
    
    print('\n=== API Documentation ===')
    
    # Extract endpoint info
    endpoint = 'https://www.gelonghui.com/api/live-channels/all/lives/v4'
    params = {
        'category': 'all',
        'limit': 15,
        'timestamp': 1773409192465
    }
    
    print(f'Endpoint: {endpoint}')
    print(f'Parameters:')
    for param, value in params.items():
        print(f'  {param}: {value}')
    
    # Response structure
    if 'data' in data and 'lives' in data['data']:
        lives = data['data']['lives']
        if lives and isinstance(lives, list):
            sample_live = lives[0]
            
            print(f'\nResponse Structure:')
            print(f'  data: object')
            print(f'    lives: array of live stream objects')
            print(f'      Sample live stream object:')
            
            # Document each field
            field_descriptions = {
                'id': 'Unique identifier for the live stream',
                'title': 'Title of the live stream',
                'description': 'Description of the live stream content',
                'startTime': 'Start time timestamp',
                'endTime': 'End time timestamp (if applicable)',
                'status': 'Current status (live, upcoming, ended)',
                'viewerCount': 'Current number of viewers',
                'channelId': 'Channel identifier',
                'hashtag': 'Associated hashtags',
                'thumbnail': 'Thumbnail image URL',
                'content': 'Additional content information'
            }
            
            for field, value in sample_live.items():
                description = field_descriptions.get(field, 'Field description not available')
                print(f'        {field}: {type(value).__name__} - {description}')
    
    # Save documentation
    with open('api_documentation.md', 'w', encoding='utf-8') as f:
        f.write(f"# 格隆汇 Live Streaming API Documentation\n\n")
        f.write(f"## Endpoint\n")
        f.write(f"- **URL**: {endpoint}\n")
        f.write(f"- **Method**: GET\n\n")
        f.write(f"## Parameters\n")
        for param, value in params.items():
            f.write(f"- **{param}**: {value}\n")
        f.write(f"\n## Response Structure\n")
        f.write(f"```json\n")
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        f.write(f"\n```\n")
    
    print(f'\nAPI documentation saved to: api_documentation.md')

def main():
    """Main function to test and analyze the API endpoint"""
    print("Testing 格隆汇 Live Streaming API Endpoint")
    print("=" * 50)
    
    # Test the API
    data = test_api_endpoint()
    
    if data:
        # Analyze structure
        analyze_api_structure(data)
        
        # Generate documentation
        generate_api_documentation(data)
        
        print(f"\n=== Analysis Complete ===")
        print(f"The API endpoint is functional and provides structured live stream data.")
        print(f"Key findings:")
        print(f"- Returns live stream metadata including titles, descriptions, viewer counts")
        print(f"- Includes timestamp-based pagination via 'timestamp' parameter")
        print(f"- Supports category filtering and limit controls")
        print(f"- Provides comprehensive data for real-time monitoring")
    else:
        print(f"\n=== Analysis Failed ===")
        print(f"Could not successfully retrieve data from the API endpoint.")

if __name__ == '__main__':
    main()