#!/usr/bin/env python3
"""
Test script for UTF-8 decoding fix
Tests the new error handling for binary data that can't be decoded as UTF-8
"""

import binascii

def test_utf8_handling():
    """Test the UTF-8 handling with problematic binary data"""
    print("Testing UTF-8 handling for binary inverter data...")

    # Simulate problematic binary data (contains byte 0xb3 which caused the original error)
    test_data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\xb3invalid_utf8_data\x00'

    print(f"Test data (hex): {test_data.hex()}")
    print(f"Test data length: {len(test_data)}")

    # Test the old approach (would fail)
    print("\n1. Testing old approach (would cause the error):")
    try:
        serial_old = str(test_data, encoding="UTF-8")
        print(f"Old approach result: {serial_old}")
    except UnicodeDecodeError as e:
        print(f"Old approach failed (expected): {e}")

    # Test the new approach (should work)
    print("\n2. Testing new approach:")
    try:
        # Convert to hex first, then try to decode
        serial_hex = binascii.hexlify(test_data)
        serial_new = binascii.unhexlify(serial_hex).decode('utf-8', errors='ignore').strip('\x00')
        print(f"New approach result: '{serial_new}'")
        print("New approach succeeded!")
    except Exception as e:
        print(f"New approach failed: {e}")

    # Test with actual serial-like data
    print("\n3. Testing with valid serial data:")
    valid_serial = b'PVL5400Nxxxxxxxx\x00\x00\x00\x00'
    try:
        serial_hex = binascii.hexlify(valid_serial)
        serial_decoded = binascii.unhexlify(serial_hex).decode('utf-8', errors='ignore').strip('\x00')
        print(f"Valid serial result: '{serial_decoded}'")
    except Exception as e:
        print(f"Valid serial test failed: {e}")

    print("\n✓ UTF-8 handling tests completed")

if __name__ == "__main__":
    test_utf8_handling()
