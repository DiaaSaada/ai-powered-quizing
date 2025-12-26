"""
Test script for the courses API endpoint.
Run this after starting the server to test the generate endpoint.
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
GENERATE_ENDPOINT = f"{BASE_URL}/api/v1/courses/generate"
TOPICS_ENDPOINT = f"{BASE_URL}/api/v1/courses/supported-topics"


def test_generate_course(topic: str):
    """Test the generate course endpoint."""
    print(f"\n{'='*70}")
    print(f"Testing: Generate Course for '{topic}'")
    print(f"{'='*70}")
    
    # Request payload
    payload = {"topic": topic}
    
    try:
        # Make POST request
        response = requests.post(GENERATE_ENDPOINT, json=payload)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"\nTopic: {data['topic']}")
            print(f"Total Chapters: {data['total_chapters']}")
            print(f"Message: {data['message']}\n")
            
            print("Chapters:")
            print("-" * 70)
            for chapter in data['chapters']:
                print(f"\nChapter {chapter['number']}: {chapter['title']}")
                print(f"  Difficulty: {chapter['difficulty']}")
                print(f"  Summary: {chapter['summary'][:80]}...")
                print(f"  Key Concepts: {', '.join(chapter['key_concepts'][:3])}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_supported_topics():
    """Test the supported topics endpoint."""
    print(f"\n{'='*70}")
    print(f"Testing: Get Supported Topics")
    print(f"{'='*70}")
    
    try:
        response = requests.get(TOPICS_ENDPOINT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"\nSupported Topics:")
            for topic in data['supported_topics']:
                print(f"  - {topic}")
            print(f"\nNote: {data['note']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  AI Learning Platform - API Tests")
    print("="*70)
    print("\nMake sure the server is running: python run.py")
    print("Then this script will test the new endpoints.\n")
    
    # Test supported topics
    test_supported_topics()
    
    # Test with predefined topic
    test_generate_course("Project Management")
    
    # Test with another predefined topic
    test_generate_course("Python Programming")
    
    # Test with generic topic
    test_generate_course("Machine Learning")
    
    print("\n" + "="*70)
    print("  Tests Complete!")
    print("="*70)
    print("\n💡 Try the interactive docs at: http://localhost:8000/docs")
    print()