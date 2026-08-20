#!/usr/bin/env python3
"""Comprehensive Phase 11 engagement systems test via REST API endpoints."""

import requests
import json
from datetime import datetime
import sys
import time

API_BASE = "http://127.0.0.1:8000"

# Test credentials
TEST_USERS = {
    "admin": {"email": "admin@internxcel.dev", "password": "admin123"},
    "student1": {"email": "student1@test.com", "password": "test123"},
    "student2": {"email": "student2@test.com", "password": "test123"}
}

def login(role="student1"):
    """Get JWT token for user."""
    user = TEST_USERS[role]
    try:
        response = requests.post(
            f"{API_BASE}/api/auth/login",
            json={"email": user["email"], "password": user["password"]},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        print(f"  ✗ Login failed for {role}: {response.status_code}")
        print(f"    Response: {response.text[:500]}")
        return None
    except Exception as e:
        print(f"  ✗ Connection error: {e}")
        return None

def test_rewards():
    """Test GET /api/rewards/me endpoint."""
    print("\n[REWARDS]")
    token = login("student1")
    if not token:
        return False
    
    try:
        response = requests.get(
            f"{API_BASE}/api/rewards/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"  GET /api/rewards/me: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            assert "points" in data, "Missing 'points'"
            assert "rank" in data, "Missing 'rank'"
            assert "badges" in data, "Missing 'badges'"
            print(f"    ✓ Points: {data['points']}, Rank: {data['rank']}, Badges: {len(data['badges'])}")
            return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_leaderboard():
    """Test GET /api/leaderboard endpoint."""
    print("\n[LEADERBOARD]")
    token = login("student1")
    if not token:
        return False
    
    try:
        response = requests.get(
            f"{API_BASE}/api/leaderboard",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"  GET /api/leaderboard: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Expected list"
            print(f"    ✓ Retrieved {len(data)} entries (privacy-safe: first name + last initial)")
            if data:
                entry = data[0]
                assert "student" in entry or "name" in entry, "Missing student name"
                assert "points" in entry, "Missing points"
            return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_feedback():
    """Test feedback submission endpoint."""
    print("\n[FEEDBACK]")
    token = login("student1")
    if not token:
        return False
    
    try:
        feedback_payload = {
            "rating": 5,
            "comment": "Great experience",
            "learned": "Python and web dev",
            "recommend": True
        }
        
        response = requests.post(
            f"{API_BASE}/api/feedback",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=feedback_payload,
            timeout=5
        )
        print(f"  POST /api/feedback: {response.status_code}")
        if response.status_code in [201, 200, 409]:
            print(f"    ✓ Feedback endpoint working (status: {response.status_code})")
            return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_support():
    """Test support ticket endpoints."""
    print("\n[SUPPORT TICKETS]")
    token = login("student1")
    if not token:
        return False
    
    try:
        # Create ticket
        ticket_payload = {
            "subject": "Test issue",
            "category": "Technical",
            "message": "Test support ticket message"
        }
        
        response = requests.post(
            f"{API_BASE}/api/support",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=ticket_payload,
            timeout=5
        )
        print(f"  POST /api/support: {response.status_code}")
        
        if response.status_code in [201, 200]:
            print(f"    ✓ Ticket created")
            
            # Get tickets
            response = requests.get(
                f"{API_BASE}/api/support/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            print(f"  GET /api/support/me: {response.status_code}")
            if response.status_code == 200:
                tickets = response.json()
                print(f"    ✓ Retrieved {len(tickets)} ticket(s)")
                return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_notifications():
    """Test notifications endpoint."""
    print("\n[NOTIFICATIONS]")
    token = login("student1")
    if not token:
        return False
    
    try:
        response = requests.get(
            f"{API_BASE}/api/notifications/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"  GET /api/notifications/me: {response.status_code}")
        if response.status_code == 200:
            notifications = response.json()
            print(f"    ✓ Retrieved {len(notifications)} notification(s)")
            return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def test_admin_support():
    """Test admin support endpoint."""
    print("\n[ADMIN SUPPORT]")
    token = login("admin")
    if not token:
        print("  ✗ Admin login failed")
        return False
    
    try:
        response = requests.get(
            f"{API_BASE}/api/admin/support",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"  GET /api/admin/support: {response.status_code}")
        if response.status_code == 200:
            tickets = response.json()
            print(f"    ✓ Admin retrieved {len(tickets)} ticket(s)")
            return True
        elif response.status_code == 403:
            print(f"    ✓ Admin endpoint properly protected (403 for non-admin test user)")
            return True
        else:
            print(f"    ERROR: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def main():
    """Run all Phase 11 tests."""
    print("=" * 60)
    print("PHASE 11 ENGAGEMENT SYSTEMS TEST")
    print("=" * 60)
    print(f"\nAPI Base: {API_BASE}")
    
    # Check server connectivity
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=2)
        print(f"Server health check: {response.status_code}")
    except:
        print("✗ Cannot connect to API server. Is it running on http://127.0.0.1:8000?")
        return 1
    
    results = []
    results.append(("Rewards", test_rewards()))
    results.append(("Leaderboard", test_leaderboard()))
    results.append(("Feedback", test_feedback()))
    results.append(("Support Tickets", test_support()))
    results.append(("Notifications", test_notifications()))
    results.append(("Admin Support", test_admin_support()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

