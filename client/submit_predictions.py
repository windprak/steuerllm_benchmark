#!/usr/bin/env python3
"""
Client script for submitting predictions to the GerTaxLaw Benchmark server.
"""
import argparse
import json
import requests
import time
from pathlib import Path

def validate_predictions_file(filepath):
    """Validate predictions file format."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        if not isinstance(predictions, dict):
            print("❌ Error: Predictions file must be a JSON object")
            return None
        
        # Check all values are strings
        for qid, answer in predictions.items():
            if not isinstance(answer, str):
                print(f"❌ Error: Answer for question {qid} must be a string")
                return None
            if not answer.strip():
                print(f"⚠️  Warning: Answer for question {qid} is empty")
        
        print(f"✅ Predictions file validated: {len(predictions)} answers")
        return predictions
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def submit_predictions(server_url, predictions_file, model_name, submission_key):
    """Submit predictions to the benchmark server."""
    
    # Validate predictions
    predictions = validate_predictions_file(predictions_file)
    if predictions is None:
        return False
    
    # Prepare submission
    print(f"\n📤 Submitting predictions to {server_url}")
    print(f"   Model: {model_name}")
    print(f"   Questions: {len(predictions)}")
    
    try:
        # Option 1: Submit as file
        with open(predictions_file, 'rb') as f:
            files = {'file': (Path(predictions_file).name, f, 'application/json')}
            data = {
                'model_name': model_name,
                'key': submission_key
            }
            
            response = requests.post(
                f"{server_url}/submit",
                files=files,
                data=data,
                timeout=30
            )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                submission_id = result.get('submission_id')
                queue_position = result.get('queue_position')
                
                print(f"\n✅ Submission successful!")
                print(f"   Submission ID: {submission_id}")
                print(f"   Queue position: {queue_position}")
                print(f"   Status URL: {server_url}/status/{submission_id}")
                
                # Poll for status
                if input("\n👀 Monitor evaluation progress? (y/n): ").lower() == 'y':
                    monitor_status(server_url, submission_id)
                
                return True
            else:
                print(f"\n❌ Submission failed: {result.get('error')}")
                if 'details' in result:
                    print("\nDetails:")
                    for detail in result['details']:
                        print(f"  • {detail}")
                return False
        
        elif response.status_code == 403:
            print("\n❌ Invalid submission key")
            return False
        
        elif response.status_code == 429:
            print("\n❌ Too many submissions from your IP")
            return False
        
        else:
            print(f"\n❌ Server error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to server at {server_url}")
        print("   Make sure the server is running and the URL is correct")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def monitor_status(server_url, submission_id):
    """Monitor evaluation status with progress updates."""
    print("\n🔄 Monitoring evaluation progress...")
    print("   Press Ctrl+C to stop monitoring\n")
    
    try:
        last_status = None
        while True:
            try:
                response = requests.get(f"{server_url}/status/{submission_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    
                    # Only print if status changed
                    if status != last_status:
                        print(f"   Status: {status}")
                        last_status = status
                    
                    if status == 'queued':
                        queue_pos = data.get('queue_position', '?')
                        print(f"   ⏳ Position in queue: {queue_pos}")
                    
                    elif status == 'evaluating':
                        progress = data.get('progress', 0)
                        bar_length = 30
                        filled = int(bar_length * progress / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"   🔄 [{bar}] {progress}%", end='\r')
                    
                    elif status == 'completed':
                        print(f"\n   ✅ Evaluation completed!")
                        print(f"   Completed at: {data.get('completed_at')}")
                        break
                    
                    elif status == 'failed':
                        print(f"\n   ❌ Evaluation failed: {data.get('error')}")
                        break
                
                else:
                    print(f"   ⚠️  Could not fetch status (HTTP {response.status_code})")
                
                time.sleep(2)  # Poll every 2 seconds
                
            except KeyboardInterrupt:
                print("\n\n   Monitoring stopped. Evaluation continues on server.")
                break
            except Exception as e:
                print(f"\n   ⚠️  Error fetching status: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n\n   Monitoring stopped.")

def main():
    parser = argparse.ArgumentParser(
        description='Submit predictions to GerTaxLaw Benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python submit_predictions.py predictions.json --model "GPT-4" --key "YourKey"
  python submit_predictions.py predictions.json -m "MyModel-v1" -k "YourKey" -s http://localhost:5000

The predictions.json file should contain:
  {
    "1001": "Your answer for question 1001...",
    "1002": "Your answer for question 1002...",
    ...
  }
        """
    )
    
    parser.add_argument('predictions_file', help='Path to predictions JSON file')
    parser.add_argument('-m', '--model', required=True, help='Model name')
    parser.add_argument('-k', '--key', default='GerTaxLaw2025', help='Submission key')
    parser.add_argument('-s', '--server', default='https://steuerllm.i5.ai.fau.de/benchmark', 
                       help='Server URL (default: http://localhost:5000)')
    
    args = parser.parse_args()
    
    # Submit
    success = submit_predictions(
        args.server,
        args.predictions_file,
        args.model,
        args.key
    )
    
    if success:
        print("\n🎉 Done! Check the leaderboard for results.")
    else:
        print("\n❌ Submission failed. Please check the errors above.")
        exit(1)

if __name__ == '__main__':
    main()
