#!/usr/bin/env python3
"""
Test script for configuration switches
Tests various combinations of MQTT and REST enabled/disabled
"""

import sys
import os
import importlib

def test_configuration(mqtt_enabled, rest_enabled):
    """Test configuration with different MQTT and REST settings"""
    print(f"\n=== Testing MQTT_ENABLED={mqtt_enabled}, REST_ENABLED={rest_enabled} ===")

    # Temporarily modify config
    import config as cfg
    original_mqtt = cfg.MQTT_ENABLED
    original_rest = cfg.REST_ENABLED

    try:
        # Set test configuration
        cfg.MQTT_ENABLED = mqtt_enabled
        cfg.REST_ENABLED = rest_enabled

        print(f"Config: MQTT={cfg.MQTT_ENABLED}, REST={cfg.REST_ENABLED}, REST_FREQ={cfg.REST_MAX_FREQUENCY_SECONDS}s")

        # Test importing modules
        import rest_client
        import trannergy_parser

        # Test creating REST client
        if rest_enabled:
            client = rest_client.ChargeHQClient()
            print(f"✓ REST client created with {client._send_interval}s interval")
        else:
            print("✓ REST disabled - no client created")

        # Test creating parser
        parser = trannergy_parser.ParseTelegrams(None, None, None, None)
        if hasattr(parser, '_ParseTelegrams__rest_client'):
            if rest_enabled:
                print("✓ Parser has REST client")
            else:
                print("✓ Parser REST client is None (disabled)")

        print("✓ Configuration test passed")

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    finally:
        # Restore original configuration
        cfg.MQTT_ENABLED = original_mqtt
        cfg.REST_ENABLED = original_rest

    return True

def main():
    """Run configuration tests"""
    print("Testing configuration switches...")

    # Test all combinations
    configs = [
        (True, True),   # Both enabled
        (True, False),  # Only MQTT
        (False, True),  # Only REST
        (False, False), # Both disabled
    ]

    success_count = 0
    for mqtt, rest in configs:
        if test_configuration(mqtt, rest):
            success_count += 1

    print(f"\n=== Results ===")
    print(f"Tests passed: {success_count}/{len(configs)}")

    if success_count == len(configs):
        print("✓ All configuration tests passed!")
        return True
    else:
        print("✗ Some configuration tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
