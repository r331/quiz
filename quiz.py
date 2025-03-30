#!/usr/bin/env python3
import argparse
import json
import os
import random
import sys
from typing import List, Dict, Any


def load_questions(filename: str) -> List[Dict[str, Any]]:
    """
    Load questions from a file.
    
    Args:
        filename: Path to the quiz file
        
    Returns:
        List of question dictionaries
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file isn't valid JSON
    """
    try:
        with open(filename, 'r') as file:
            questions = json.load(file)
            if not isinstance(questions, list):
                raise ValueError("File format error: Expected a list of questions")
            return questions
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading questions: {str(e)}")
        sys.exit(1)


def validate_questions(questions: List[Dict[str, Any]]) -> None:
    """
    Validate that questions have the required structure.
    
    Args:
        questions: List of question dictionaries
        
    Raises:
        ValueError: If any question has an invalid format
    """
    for i, q in enumerate(questions):
        # Check required fields
        required_fields = ["id", "q", "options", "answer", "answer_description"]
        for field in required_fields:
            if field not in q:
                raise ValueError(f"Question {i+1} is missing required field: {field}")
        
        # Check options
        if not isinstance(q["options"], dict) or len(q["options"]) < 2:
            raise ValueError(f"Question {i+1} must have at least 2 options")
        
        # Check answer is one of the options
        if q["answer"] not in q["options"]:
            raise ValueError(f"Question {i+1} has an invalid answer: {q['answer']}")


def select_random_questions(questions: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    """
    Shuffle all questions and select a random subset.
    
    Args:
        questions: List of all question dictionaries
        count: Number of questions to select
        
    Returns:
        List of randomly selected question dictionaries
    """
    if count > len(questions):
        print(f"Warning: Requested {count} questions, but only {len(questions)} are available.")
        return questions.copy()
    
    shuffled = questions.copy()
    random.shuffle(shuffled)
    return shuffled[:count]


def display_question(question: Dict[str, Any], question_num: int) -> None:
    """
    Display a question and its options.
    
    Args:
        question: Question dictionary
        question_num: Question number in the quiz
    """
    print(f"\nQuestion {question_num}:")
    print(question["q"])
    
    print("Options:")
    for option_key, option_value in question["options"].items():
        print(f"  {option_key}: {option_value}")


def get_user_answer(question: Dict[str, Any]) -> str:
    """
    Prompt the user for an answer and validate it.
    
    Args:
        question: Question dictionary
        
    Returns:
        User's valid answer
    """
    valid_options = list(question["options"].keys())
    while True:
        user_answer = input(f"Your answer ({', '.join(valid_options)}): ").strip().lower()
        if user_answer in valid_options:
            return user_answer
        print(f"Invalid answer. Please enter one of: {', '.join(valid_options)}")


def run_quiz(questions: List[Dict[str, Any]]) -> int:
    """
    Run the quiz with the selected questions.
    
    Args:
        questions: List of question dictionaries to use
        
    Returns:
        Number of correct answers
    """
    correct_answers = 0
    
    for i, question in enumerate(questions):
        display_question(question, i + 1)
        user_answer = get_user_answer(question)
        
        if user_answer == question["answer"]:
            print("✓ Correct!")
            correct_answers += 1
        else:
            correct_option = question["answer"]
            print(f"✗ Incorrect. The correct answer is: {correct_option}")
        
        print(f"Explanation: {question['answer_description']}")
    
    return correct_answers


def main():
    """Main function to process arguments and run the quiz."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Quiz application")
    parser.add_argument("filename", help="Path to the quiz file (.q)")
    parser.add_argument("count", type=int, help="Number of questions for the quiz")
    args = parser.parse_args()
    
    # Validate arguments
    if args.count < 1:
        print("Error: Number of questions must be at least 1.")
        sys.exit(1)
    
    try:
        # Load and validate questions
        questions = load_questions(args.filename)
        validate_questions(questions)
        
        # Check if we have enough questions
        if len(questions) < args.count:
            print(f"Warning: Requested {args.count} questions, but only {len(questions)} are available.")
            print(f"Proceeding with all {len(questions)} questions.")
            selected_questions = questions
        else:
            # Select random questions
            selected_questions = select_random_questions(questions, args.count)
        
        # Run the quiz
        print(f"\nStarting quiz with {len(selected_questions)} questions...")
        correct_answers = run_quiz(selected_questions)
        
        # Display results
        score_percentage = (correct_answers / len(selected_questions)) * 100
        print(f"\nQuiz complete! Your score: {correct_answers}/{len(selected_questions)} ({score_percentage:.1f}%)")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
