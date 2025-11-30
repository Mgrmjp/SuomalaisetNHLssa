#!/usr/bin/env python3
"""
Test script to verify the rate limiting implementation for NHL API requests
"""

import sys
import time
from pathlib import Path

# Add the finnish data collection module to path
sys.path.insert(0, str(Path(__file__).parent / "data_collection" / "finnish"))

from fetch import fetch_from_api, NHL_API_BASE

def test_rate_limiting():
    """Test the rate limiting implementation with multiple rapid requests"""
    print("Testing rate limiting implementation...")
    print("=" * 60)
    
    # Test URLs that would normally trigger rate limits if called rapidly
    test_urls = [
        f"{NHL_API_BASE}/v1/gamecenter/2025020376/boxscore",
        f"{NHL_API_BASE}/v1/gamecenter/2025020318/boxscore",
        f"{NHL_API_BASE}/v1/gamecenter/2025020271/boxscore",
        f"{NHL_API_BASE}/v1/gamecenter/2025020376/play-by-play",
        f"{NHL_API_BASE}/v1/gamecenter/2025020318/play-by-play",
    ]
    
    print(f"Testing {len(test_urls)} API calls with rate limiting...")
    print()
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"[{i}/{len(test_urls)}] Testing: {url}")
        
        result = fetch_from_api(url, max_retries=3)
        
        if result:
            success_count += 1
            print(f"      ✅ Success")
        else:
            error_count += 1
            print(f"      ❌ Failed")
        
        elapsed = time.time() - start_time
        print(f"      Elapsed time: {elapsed:.2f}s")
        print()
    
    total_time = time.time() - start_time
    avg_time_per_request = total_time / len(test_urls)
    
    print("=" * 60)
    print("Test Results:")
    print(f"  Total requests: {len(test_urls)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time per request: {avg_time_per_request:.2f}s")
    print(f"  Rate: {len(test_urls)/total_time:.2f} requests/second")
    
    # Check if rate limiting is working (should be around 1 request per second minimum)
    if avg_time_per_request >= 0.9:  # Allow some tolerance
        print("\n✅ Rate limiting appears to be working correctly")
        return True
    else:
        print("\n⚠️  Rate limiting may not be working as expected")
        return False

def test_exponential_backoff():
    """Test exponential backoff with an invalid URL"""
    print("\nTesting exponential backoff with invalid URL...")
    print("=" * 60)
    
    # Use an invalid game ID to trigger errors
    invalid_url = f"{NHL_API_BASE}/v1/gamecenter/999999999/boxscore"
    
    start_time = time.time()
    result = fetch_from_api(invalid_url, max_retries=3)
    elapsed = time.time() - start_time
    
    print(f"Invalid URL test completed in {elapsed:.2f}s")
    print(f"Result: {result}")
    
    # Should take at least some time due to retries with backoff
    if elapsed >= 4:  # Should take at least 4 seconds with retries
        print("✅ Exponential backoff appears to be working")
        return True
    else:
        print("⚠️  Exponential backoff may not be working as expected")
        return False

if __name__ == "__main__":
    print("NHL API Rate Limiting Test")
    print("=" * 60)
    print()
    
    rate_limiting_ok = test_rate_limiting()
    backoff_ok = test_exponential_backoff()
    
    print("\n" + "=" * 60)
    if rate_limiting_ok and backoff_ok:
        print("✅ All tests passed! Rate limiting implementation is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please review the implementation.")
        sys.exit(1)