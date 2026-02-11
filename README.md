# SteuerEx Benchmark - Participant Guide

## Overview

The SteuerEx Benchmark is an evaluation framework for assessing language model performance on German tax law questions. This benchmark uses a rigorous bootstrap-based evaluation methodology to ensure reliable and reproducible results.

**Official Server**: https://steuerllm.i5.ai.fau.de/benchmark

## Dataset

The benchmark consists of **115 questions** covering various aspects of German tax law. All questions are evaluated using the same bootstrap methodology used in the original paper.

### Question Categories

- Einkommensteuer (Income Tax)
- Körperschaftsteuer (Corporate Tax)
- Umsatzsteuer (VAT)
- Gewerbesteuer (Trade Tax)
- Abgabenordnung (Tax Code)
- Erbschaftsteuer (Inheritance Tax)
- Umwandlungssteuer (Transformation Tax)
- Besteuerung von Personengesellschaften (Partnership Taxation)

### Data Format

Each question includes:
- `id`: Unique question identifier
- `exam`: Source examination
- `year`: Academic year
- `title`: Question title
- `category`: Tax law category
- `max_score`: Maximum points achievable
- `question`: Full question text

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Internet connection for submission

### Installation

```bash
# Install required packages
pip install -r requirements.txt
```

### Files Provided

```
client/
├── requirements.txt           # Python dependencies
├── generate_predictions.py    # Template for generating predictions
└── submit_predictions.py      # Submission script

benchmark-questions.json       # All 115 questions (no reference answers)
```

## Generating Predictions

### Step 1: Implement Your Model

Edit `generate_predictions.py` to implement your model's prediction logic:

```python
def generate_answer(question_data):
    """
    Generate an answer for a given question.
    
    Args:
        question_data: Dict with keys 'id', 'question', 'max_score', etc.
    
    Returns:
        str: Your model's answer
    """
    # TODO: Implement your model here
    # Example: Call your LLM, retrieval system, etc.
    
    answer = your_model.generate(question_data['question'])
    return answer
```

### Step 2: Generate Predictions

```bash
python generate_predictions.py
```

This creates `predictions.json` with your model's answers.

### Submission Format

Your submission must be a JSON file mapping question IDs to answer strings:

```json
{
  "1001": "Your answer to question 1001...",
  "1002": "Your answer to question 1002...",
  ...
  "1115": "Your answer to question 1115..."
}
```

**Requirements:**
- **All 115 question IDs must be present**
- All answers must be non-empty strings
- Use UTF-8 encoding

## Submitting Predictions

### Command Line Submission

```bash
python submit_predictions.py predictions.json \
  --model "YourModelName-v1" \
  --key "GerTaxLaw2025" \
  --server "https://steuerllm.i5.ai.fau.de/benchmark"
```

### Parameters

- `predictions.json`: Path to your predictions file
- `--model` / `-m`: Your model name (required)
- `--key` / `-k`: Submission key (default: "GerTaxLaw2025")
- `--server` / `-s`: Server URL (default: https://steuerllm.i5.ai.fau.de/benchmark)

### Submission Limits

- **One submission per IP address**
- Choose your best model carefully
- Results are final once submitted

## Evaluation Methodology

### Bootstrap-Based Evaluation

The benchmark uses **points-based bootstrap resampling** with the following parameters:

- **B = 1,000**: Number of bootstrap replicates
- **Seed = 42**: Fixed random seed for reproducibility
- **Target = 1,035.5 points**: Constrained bootstrap target

### Scoring

1. Each answer is evaluated by GPT-4 against reference answers
2. Points are awarded based on correctness (0 to max_score)
3. Bootstrap resampling calculates mean performance and confidence intervals
4. Results reported as: **Mean% ± SD [95% CI: Low, High]**

### Example Result

```
Performance: 85% ± 3 [95% CI: 79, 91]
Total Score: 881.7/1035.5 (85.1%)
Questions: 115
```

**Interpretation:**
- **85%**: Mean performance across 1,000 bootstrap samples
- **± 3**: Standard deviation (uncertainty measure)
- **[79, 91]**: 95% confidence interval
- **881.7/1035.5**: Raw points earned

## Workflow

### 1. Review the Questions

Examine the benchmark questions to understand the task:

```python
import json

with open('benchmark-questions.json', 'r') as f:
    questions = json.load(f)

# Review question structure
for q in questions[:5]:
    print(f"ID: {q['id']}, Category: {q['category']}, Max Score: {q['max_score']}")
    print(f"Question: {q['question'][:200]}...")
```

### 2. Implement Your Model

Edit `client/generate_predictions.py` to add your model logic.

### 3. Generate Predictions

Run the generation script to create answers for all 115 questions:

```bash
cd client
python generate_predictions.py
```

This creates `predictions.json` with all 115 answers.

### 4. Submit

Submit your predictions once:

```bash
python submit_predictions.py predictions.json -m "YourModel-v1"
```

## Best Practices

### Model Development

1. **Review benchmark questions**: Understand the scope and difficulty of all 115 questions
2. **Consider question difficulty**: Questions have varying max_scores (1-51 points)
3. **Handle long questions**: Some questions exceed 1,000 words
4. **Provide detailed answers**: Reference specific legal paragraphs when applicable
5. **Test your implementation**: Validate your model produces answers for all questions
6. **Use correct parameters**: Set `temperature=0` and `max_tokens=4096` to match benchmark evaluation
7. **Remove thinking traces**: If your model outputs `<think>...</think>` blocks, remove them before submission

### Answer Quality

- Cite relevant legal provisions (e.g., "§ 15 Abs. 1 S. 1 Nr. 2 EStG")
- Show calculations where applicable
- Structure complex answers clearly
- Use proper legal terminology
- Provide reasoning, not just conclusions

### Technical Considerations

- **Encoding**: Use UTF-8 for German characters (ä, ö, ü, ß)
- **Validation**: Test your submission format with `example_submission.json`
- **Error handling**: Check submission status and error messages
- **Timeout**: Evaluation may take several minutes

## Troubleshooting

### Common Issues

**Validation Error: Missing question IDs**
```
Solution: Ensure all 115 question IDs are in your predictions.json
```

**Validation Error: Empty answers**
```
Solution: All answers must be non-empty strings
```

**Submission rejected: Key already used**
```
Solution: Only one submission per IP address is allowed
```

**Connection Error**
```
Solution: Check server URL and network connection
```

### Getting Help

If you encounter issues:

1. Check the example submission format
2. Validate your JSON syntax
3. Review error messages carefully
4. Ensure all requirements are met

## Citation

If you use this benchmark in your research, please cite:

```bibtex
@misc{steuerex2025,
  title={SteuerEx: A Bootstrap-Evaluated Benchmark for German Tax Law},
  author={[Author Names]},
  year={2025},
  url={https://steuerllm.i5.ai.fau.de/benchmark},
  note={Bootstrap methodology: seed=42, B=1000, target=1035.5 points}
}
```

## Leaderboard

View current rankings and detailed results at:
```
https://steuerllm.i5.ai.fau.de/benchmark/leaderboard_page
```

## License

[Specify your license here]

## Contact

For questions or issues, please contact: [Your contact information]

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Benchmark Questions**: 115 total
