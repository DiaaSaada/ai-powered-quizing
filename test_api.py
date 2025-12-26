"""
Test script for the AI Learning Platform API.
Tests the complete validation and course generation flow.

Run this after starting the server:
    python run.py
    python test_api.py
"""
import requests
import json
from typing import Optional

# API endpoints
BASE_URL = "http://localhost:8000"
VALIDATE_ENDPOINT = f"{BASE_URL}/api/v1/courses/validate"
GENERATE_ENDPOINT = f"{BASE_URL}/api/v1/courses/generate"
TOPICS_ENDPOINT = f"{BASE_URL}/api/v1/courses/supported-topics"
PROVIDERS_ENDPOINT = f"{BASE_URL}/api/v1/courses/providers"
PRESETS_ENDPOINT = f"{BASE_URL}/api/v1/courses/config-presets"
HEALTH_ENDPOINT = f"{BASE_URL}/health"


def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_subheader(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*50}")
    print(f"  {title}")
    print(f"{'-'*50}")


# =============================================================================
# Health Check Tests
# =============================================================================

def test_health():
    """Test the health check endpoint."""
    print_subheader("Health Check")

    try:
        response = requests.get(HEALTH_ENDPOINT)
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"App: {data['app_name']} v{data['version']}")
            print(f"Database: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Is it running on http://localhost:8000?")
        return False


# =============================================================================
# Validation Tests
# =============================================================================

def test_validate_rejected_topic():
    """Test that broad topics are rejected."""
    print_subheader("Validate Rejected Topic: 'Physics'")

    payload = {"topic": "Physics"}

    try:
        response = requests.post(VALIDATE_ENDPOINT, json=payload)
        data = response.json()

        if data.get("status") == "rejected":
            print(f"Status: {data['status']}")
            print(f"Reason: {data['reason']}")
            print(f"Message: {data['message']}")
            print(f"Suggestions:")
            for s in data.get('suggestions', []):
                print(f"  - {s}")
            return True
        else:
            print(f"Expected 'rejected', got: {data.get('status')}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_validate_accepted_topic():
    """Test that specific topics are accepted."""
    print_subheader("Validate Accepted Topic: 'Python Web Development with FastAPI'")

    payload = {"topic": "Python Web Development with FastAPI"}

    try:
        response = requests.post(VALIDATE_ENDPOINT, json=payload)
        data = response.json()

        print(f"Status: {data['status']}")
        print(f"Topic: {data['topic']}")
        print(f"Normalized: {data['normalized_topic']}")

        if data.get("complexity"):
            print(f"\nComplexity Assessment:")
            print(f"  Score: {data['complexity']['score']}/10")
            print(f"  Level: {data['complexity']['level']}")
            print(f"  Est. Chapters: {data['complexity']['estimated_chapters']}")
            print(f"  Est. Hours: {data['complexity']['estimated_hours']}")

        return data.get("status") == "accepted"
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_validate_vague_topic():
    """Test that vague topics need clarification."""
    print_subheader("Validate Vague Topic: 'stuff about things'")

    payload = {"topic": "stuff about things"}

    try:
        response = requests.post(VALIDATE_ENDPOINT, json=payload)
        data = response.json()

        print(f"Status: {data['status']}")
        print(f"Reason: {data.get('reason', 'N/A')}")
        print(f"Message: {data['message']}")

        return data.get("status") in ["rejected", "needs_clarification"]
    except Exception as e:
        print(f"Error: {e}")
        return False


# =============================================================================
# Course Generation Tests
# =============================================================================

def test_generate_with_difficulty(topic: str, difficulty: str):
    """Test course generation with a specific difficulty."""
    print_subheader(f"Generate: '{topic}' ({difficulty})")

    payload = {
        "topic": topic,
        "difficulty": difficulty,
        "skip_validation": True  # Skip AI validation for faster testing
    }

    try:
        response = requests.post(f"{GENERATE_ENDPOINT}?provider=mock", json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"Topic: {data['topic']}")
            print(f"Difficulty: {data['difficulty']}")
            print(f"Chapters: {data['total_chapters']}")
            print(f"Study Hours: {data['estimated_study_hours']}")
            print(f"Time/Chapter: {data['time_per_chapter_minutes']} min")

            if data.get('config'):
                print(f"Depth: {data['config']['chapter_depth']}")

            print(f"\nChapters:")
            for ch in data['chapters'][:3]:  # Show first 3
                print(f"  {ch['number']}. {ch['title']} ({ch['estimated_time_minutes']} min)")

            if len(data['chapters']) > 3:
                print(f"  ... and {len(data['chapters']) - 3} more")

            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_generate_rejected_topic():
    """Test that generating with a rejected topic returns an error."""
    print_subheader("Generate Rejected: 'Physics' (without skip)")

    payload = {
        "topic": "Physics",
        "difficulty": "beginner",
        "skip_validation": False
    }

    try:
        response = requests.post(f"{GENERATE_ENDPOINT}?provider=mock", json=payload)

        if response.status_code == 400:
            data = response.json()
            detail = data.get('detail', {})
            print(f"Correctly rejected!")
            print(f"Error: {detail.get('error', 'unknown')}")
            print(f"Reason: {detail.get('reason', 'N/A')}")
            print(f"Message: {detail.get('message', 'N/A')}")
            return True
        else:
            print(f"Expected 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


# =============================================================================
# Configuration Tests
# =============================================================================

def test_config_presets():
    """Test the configuration presets endpoint."""
    print_subheader("Configuration Presets")

    try:
        response = requests.get(PRESETS_ENDPOINT)

        if response.status_code == 200:
            data = response.json()

            for level, preset in data.get('presets', {}).items():
                print(f"\n{level.upper()}:")
                print(f"  Chapters: {preset['min_chapters']}-{preset['max_chapters']}")
                print(f"  Time/Chapter: {preset['time_per_chapter_minutes']} min")
                print(f"  Depth: {preset['chapter_depth']}")

            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_providers():
    """Test the providers endpoint."""
    print_subheader("AI Providers")

    try:
        response = requests.get(PROVIDERS_ENDPOINT)

        if response.status_code == 200:
            data = response.json()
            print(f"Default: {data.get('default_provider', 'N/A')}")
            print(f"Available: {', '.join(data.get('available_providers', []))}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_supported_topics():
    """Test the supported topics endpoint."""
    print_subheader("Supported Mock Topics")

    try:
        response = requests.get(TOPICS_ENDPOINT)

        if response.status_code == 200:
            data = response.json()
            print("Topics with specific mock data:")
            for topic in data.get('supported_topics', []):
                print(f"  - {topic}")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests():
    """Run all API tests."""
    print("\n" + "="*70)
    print("  AI Learning Platform - API Test Suite")
    print("="*70)
    print("\nMake sure the server is running: python run.py\n")

    results = []

    # Health check
    print_header("1. Health Check")
    if not test_health():
        print("\nServer not running. Please start with: python run.py")
        return
    results.append(("Health Check", True))

    # Validation tests
    print_header("2. Topic Validation Tests")
    results.append(("Rejected Topic (Physics)", test_validate_rejected_topic()))
    results.append(("Accepted Topic (FastAPI)", test_validate_accepted_topic()))
    results.append(("Vague Topic", test_validate_vague_topic()))

    # Generation tests
    print_header("3. Course Generation Tests")
    results.append(("Generate Beginner", test_generate_with_difficulty("Python Programming", "beginner")))
    results.append(("Generate Intermediate", test_generate_with_difficulty("Project Management", "intermediate")))
    results.append(("Generate Advanced", test_generate_with_difficulty("Machine Learning", "advanced")))
    results.append(("Reject Invalid Topic", test_generate_rejected_topic()))

    # Configuration tests
    print_header("4. Configuration Tests")
    results.append(("Config Presets", test_config_presets()))
    results.append(("AI Providers", test_providers()))
    results.append(("Mock Topics", test_supported_topics()))

    # Summary
    print_header("Test Results Summary")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  All tests passed!")
    else:
        print(f"\n  {total - passed} test(s) failed")

    print("\n" + "="*70)
    print("  Interactive docs: http://localhost:8000/docs")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
