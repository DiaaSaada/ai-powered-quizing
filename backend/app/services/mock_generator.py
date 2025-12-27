"""
Mock Content Generator Service
This simulates AI responses without making actual API calls.
Perfect for testing and development.
"""
from typing import List
from app.models.course import Chapter


class MockContentGenerator:
    """
    Mock service that generates fake chapters.
    This will be replaced with real AI calls later.
    """
    
    def __init__(self):
        self.mock_data = {
            "project management": [
                {
                    "number": 1,
                    "title": "Introduction to Project Management",
                    "summary": "Learn the fundamentals of project management including planning, execution, and monitoring. Understand the role of a project manager and key responsibilities.",
                    "key_concepts": ["Project lifecycle", "Stakeholder management", "Project charter", "Scope definition"],
                    "difficulty": "beginner"
                },
                {
                    "number": 2,
                    "title": "Project Planning and Scheduling",
                    "summary": "Master the art of creating effective project plans, timelines, and schedules. Learn about critical path method and resource allocation.",
                    "key_concepts": ["Work Breakdown Structure (WBS)", "Gantt charts", "Critical path", "Resource leveling"],
                    "difficulty": "intermediate"
                },
                {
                    "number": 3,
                    "title": "Risk Management and Quality Control",
                    "summary": "Identify, assess, and mitigate project risks. Implement quality assurance and control measures throughout the project lifecycle.",
                    "key_concepts": ["Risk identification", "Risk mitigation strategies", "Quality metrics", "Continuous improvement"],
                    "difficulty": "intermediate"
                },
                {
                    "number": 4,
                    "title": "Agile and Scrum Methodologies",
                    "summary": "Explore modern agile frameworks including Scrum, Kanban, and lean principles. Learn how to implement iterative development.",
                    "key_concepts": ["Scrum framework", "Sprint planning", "User stories", "Daily standups"],
                    "difficulty": "advanced"
                }
            ],
            "python programming": [
                {
                    "number": 1,
                    "title": "Python Basics and Syntax",
                    "summary": "Get started with Python programming. Learn variables, data types, operators, and basic control structures.",
                    "key_concepts": ["Variables and data types", "Operators", "If-else statements", "Loops"],
                    "difficulty": "beginner"
                },
                {
                    "number": 2,
                    "title": "Functions and Modules",
                    "summary": "Master Python functions, parameters, return values, and how to organize code using modules and packages.",
                    "key_concepts": ["Function definition", "Parameters and arguments", "Lambda functions", "Importing modules"],
                    "difficulty": "beginner"
                },
                {
                    "number": 3,
                    "title": "Object-Oriented Programming",
                    "summary": "Learn OOP concepts in Python including classes, objects, inheritance, and polymorphism.",
                    "key_concepts": ["Classes and objects", "Inheritance", "Encapsulation", "Magic methods"],
                    "difficulty": "intermediate"
                },
                {
                    "number": 4,
                    "title": "File Handling and Exception Management",
                    "summary": "Work with files, handle exceptions gracefully, and implement proper error handling in your programs.",
                    "key_concepts": ["File operations", "Try-except blocks", "Custom exceptions", "Context managers"],
                    "difficulty": "intermediate"
                }
            ],
            "default": [
                {
                    "number": 1,
                    "title": "Introduction and Fundamentals",
                    "summary": "Explore the basic concepts and foundational principles of the subject. Build a strong understanding of core terminology.",
                    "key_concepts": ["Core concepts", "Terminology", "Historical context", "Basic principles"],
                    "difficulty": "beginner"
                },
                {
                    "number": 2,
                    "title": "Intermediate Concepts and Applications",
                    "summary": "Dive deeper into practical applications and real-world examples. Learn intermediate techniques and methodologies.",
                    "key_concepts": ["Practical applications", "Case studies", "Problem-solving", "Best practices"],
                    "difficulty": "intermediate"
                },
                {
                    "number": 3,
                    "title": "Advanced Topics and Mastery",
                    "summary": "Master advanced concepts and expert-level techniques. Prepare for professional application of knowledge.",
                    "key_concepts": ["Advanced techniques", "Expert strategies", "Industry standards", "Future trends"],
                    "difficulty": "advanced"
                }
            ]
        }
    
    async def generate_chapters(self, topic: str) -> List[Chapter]:
        """
        Generate mock chapters for a given topic.
        
        Args:
            topic: The subject/topic for which to generate chapters
            
        Returns:
            List of Chapter objects
        """
        # Normalize the topic (lowercase, strip whitespace)
        normalized_topic = topic.lower().strip()
        
        # Get mock data for this topic, or use default
        chapter_data = self.mock_data.get(normalized_topic, self.mock_data["default"])
        
        # Convert dictionaries to Chapter objects
        chapters = [Chapter(**chapter) for chapter in chapter_data]
        
        return chapters
    
    def get_supported_topics(self) -> List[str]:
        """Get list of topics that have specific mock data."""
        return [topic for topic in self.mock_data.keys() if topic != "default"]