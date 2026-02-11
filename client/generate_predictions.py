#!/usr/bin/env python3
"""
Generate predictions for the GerTaxLaw Benchmark.

This script loads ALL 115 benchmark questions and generates predictions using your model.
You need to implement the generate_answer() function with your model's logic.

IMPORTANT: Use max_tokens=4096 and temperature=0 to match the benchmark evaluation settings.
"""

import json
import re
from pathlib import Path
from typing import Dict

def remove_thinking_trace(model_answer: str) -> str:
    """
    Remove thinking traces from reasoning model outputs.
    Some models (e.g., DeepSeek-R1) include <think>...</think> blocks.
    This function removes everything up to and including the </think> tag.
    """
    if not model_answer:
        return model_answer
    
    # Find the end of thinking trace
    think_end = model_answer.find('</think>')
    
    if think_end != -1:
        # Remove everything up to and including </think>
        cleaned_answer = model_answer[think_end + len('</think>'):].strip()
        return cleaned_answer
    
    # No thinking trace found, return original
    return model_answer

def generate_answer(question_data: Dict) -> str:
    """
    Generate an answer for a given question.
    
    Args:
        question_data: Dictionary containing question information with keys:
            - id: Question ID
            - question: The question text
            - max_score: Maximum points for this question
            - title: Question title
            - category: Tax law category
            - exam: Source exam
            - year: Academic year
    
    Returns:
        str: Your model's answer to the question
    
    TODO: Implement your model here!
    """
    # Example placeholder - replace with your actual model
    # You might want to:
    # - Call an LLM API (OpenAI, Anthropic, etc.)
    # - Use a local model
    # - Apply retrieval-augmented generation
    # - Use specialized tax law knowledge bases
    
    question_text = question_data['question']
    
    # PLACEHOLDER: Replace this with your model
    answer = f"This is a placeholder answer for question {question_data['id']}. " \
             f"Please implement your model in the generate_answer() function."
    
    # Example of how you might call an API:
    # from openai import OpenAI
    # client = OpenAI(api_key="your-api-key")
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "You are an expert in German tax law."},
    #         {"role": "user", "content": question_text}
    #     ],
    #     temperature=0,      # Use temperature=0 to match benchmark evaluation
    #     max_tokens=4096     # Use max_tokens=4096 to match benchmark evaluation
    # )
    # answer = response.choices[0].message.content
    # 
    # # Remove thinking traces if present (e.g., from DeepSeek-R1)
    # answer = remove_thinking_trace(answer)
    
    return answer


def main():
    """Generate predictions for all benchmark questions."""
    # Load all questions from benchmark-questions.json
    questions_file = Path("../benchmark-questions.json")
    
    if not questions_file.exists():
        print(f"Error: {questions_file} not found!")
        print("Make sure you're running this script from the client/ directory")
        return
    
    print("Loading all benchmark questions...")
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    print(f"Found {len(questions)} questions")
    print(f"Total points: {sum(q['max_score'] for q in questions)}")
    
    # Generate predictions
    predictions = {}
    
    print("\nGenerating predictions...")
    for i, question in enumerate(questions, 1):
        qid = question['id']
        print(f"  [{i}/{len(questions)}] Processing question {qid} ({question['category']})...", end='\r')
        
        answer = generate_answer(question)
        predictions[qid] = answer
    
    print(f"\n✓ Generated {len(predictions)} predictions")
    
    # Save predictions
    output_file = Path("predictions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Predictions saved to {output_file}")
    print(f"\nNext step: Submit your predictions using:")
    print(f"  python submit_predictions.py {output_file} -m YourModelName")
    
    # Validation
    print("\n" + "="*60)
    print("VALIDATION CHECK")
    print("="*60)
    print(f"Total predictions: {len(predictions)}")
    print(f"Expected questions: {len(questions)}")
    print(f"All IDs present: {'✓' if len(predictions) == len(questions) else '✗'}")
    
    empty_answers = [qid for qid, ans in predictions.items() if not ans or not ans.strip()]
    if empty_answers:
        print(f"⚠ Warning: {len(empty_answers)} empty answers found!")
        print(f"  Question IDs: {empty_answers[:5]}{'...' if len(empty_answers) > 5 else ''}")
    else:
        print("All answers non-empty: ✓")
    
    print("="*60)


if __name__ == "__main__":
    main()
