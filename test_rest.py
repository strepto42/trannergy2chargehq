#!/usr/bin/env python3
"""
Test script for REST client functionality
Tests the ChargeHQ client with sample data
"""

import rest_client

def test_rest_client():
    """Test the REST client with sample data"""
    print("Testing ChargeHQ REST client...")

    # Create client
    client = rest_client.ChargeHQClient()

    # Test data
    production_kw = 2.5  # 2.5kW production
    consumption_kw = 1.0  # 1.0kW consumption

    print(f"Sending test data: production={production_kw}kW, consumption={consumption_kw}kW")

    # First send should work (if API is reachable)
    result = client.send_solar_data(production_kw, consumption_kw)
    print(f"First send result: {result}")

    # Second send should be rate limited
    result = client.send_solar_data(production_kw, consumption_kw)
    print(f"Second send result (should be rate limited): {result}")

    # Test rate limiting check
    should_send = client.should_send_data()
    print(f"Should send data now: {should_send}")

    print("\nTest completed. Check logs for detailed information.")

if __name__ == "__main__":
    # Set up basic logging for testing
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    test_rest_client()
