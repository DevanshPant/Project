# 🚀 Quick Start Guide - Resume Screening System

Get up and running in 5 minutes!

## Installation (2 minutes)

### Step 1: Clone and Navigate
```bash
cd resume_screening_system
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download NLTK Data
```bash
python setup.py
```

## Usage (3 minutes)

### Option 1: Run Demo
```bash
python main.py
```

**Output**: See sample results in console and exported files in `outputs/` folder

### Option 2: Launch Web Interface
```bash
streamlit run src/app.py
```

**Access**: Open browser to `http://localhost:8501`

### Option 3: Use as Library
```python
from main import ResomeScreeningPipeline

# Create pipeline
pipeline = ResomeScreeningPipeline()

# Run matching
results = pipeline.run_complete_pipeline(
    resumes=['Resume text 1', 'Resume text 2'],
    job_description='Job description text',
    shortlist_threshold=0.3,
    top_candidates=5,
    export_format='all'
)

# Access results
print(results['shortlist'])  # DataFrame with shortlisted candidates
print(results['statistics']) # Matching statistics
```

---

## What Happens in Background?

### Processing Pipeline:
```
1. Load Resumes
   ↓
2. Preprocess Text (NLP)
   - Lowercase
   - Remove special characters
   - Tokenization
   - Remove stopwords
   - Lemmatization
   ↓
3. Extract Features (TF-IDF)
   - Convert to vectors
   - 5000 features max
   ↓
4. Match with Job Description
   - Cosine similarity
   - Rank candidates
   ↓
5. Shortlist Candidates
   - Apply threshold (0.3 default)
   - Select top-N
   ↓
6. Export Results
   - CSV, Excel, or JSON
```

---

## File Structure Overview

```
resume_screening_system/
├── main.py                     ← Main script (run this!)
├── src/
│   ├── data_loader.py         ← Load data
│   ├── preprocess.py          ← Clean text
│   ├── feature_extraction.py  ← TF-IDF vectors
│   ├── matcher.py             ← Match & rank
│   ├── app.py                 ← Web interface
│   └── utils.py               ← Export & helpers
├── outputs/                    ← Results saved here
├── docs/                       ← Full documentation
└── README.md                   ← More information
```

---

## Common Tasks

### Task 1: Process Resumes from File
```python
import pandas as pd
from main import ResomeScreeningPipeline

# Load resumes from CSV
df = pd.read_csv('resumes.csv')
resumes = df['resume_text'].tolist()
names = df['name'].tolist()

# Create pipeline and run
pipeline = ResomeScreeningPipeline()
results = pipeline.run_complete_pipeline(
    resumes=resumes,
    job_description="Senior Developer with Python...",
    candidate_names=names,
    export_format='excel'
)

# Save results
results['shortlist'].to_csv('shortlisted.csv', index=False)
```

### Task 2: Custom Threshold
```python
# Lower threshold = more candidates (recall ↑)
results = pipeline.run_complete_pipeline(
    resumes=resumes,
    job_description=job_desc,
    shortlist_threshold=0.2,  # More candidates
    export_format='all'
)

# Higher threshold = fewer but better matches (precision ↑)
results = pipeline.run_complete_pipeline(
    resumes=resumes,
    job_description=job_desc,
    shortlist_threshold=0.6,  # Fewer candidates
    export_format='all'
)
```

### Task 3: Download from Kaggle
```python
from src.data_loader import DataLoader

loader = DataLoader()
loader.download_dataset()  # Downloads from Kaggle
df = loader.load_dataset()
```

### Task 4: Just Preprocess Text
```python
from src.preprocess import TextPreprocessor

preprocessor = TextPreprocessor()
clean_text = preprocessor.preprocess_text(raw_resume_text)
print(clean_text)
```

### Task 5: Extract Features Only
```python
from src.feature_extraction import FeatureExtractor

extractor = FeatureExtractor()
feature_matrix = extractor.extract_features(processed_texts)
print(f"Shape: {feature_matrix.shape}")
```

---

## Understanding Similarity Scores

| Score | Interpretation | Recommendation |
|-------|-----------------|-----------------|
| 0.9 - 1.0 | 🟩 Excellent Match | Definitely interview |
| 0.7 - 0.9 | 🟨 Good Match | Interview |
| 0.5 - 0.7 | 🟧 Moderate Match | Consider interviewing |
| 0.3 - 0.5 | 🟥 Weak Match | Maybe interview |
| < 0.3 | ⬛ Poor Match | Likely skip |

---

## Output Examples

### Console Output
```
Rank  Candidate ID  Candidate Name  Similarity Score  Match Type
────────────────────────────────────────────────────────────────
1     0            John Doe        0.8543           Excellent Match
2     4            Alice Johnson   0.7821           Good Match
3     2            Bob Wilson      0.6734           Good Match
```

### CSV Export
```
Rank,Candidate ID,Candidate Name,Similarity Score,Match Type,Score Percentage
1,0,John Doe,0.8543,Excellent Match,85.43%
2,4,Alice Johnson,0.7821,Good Match,78.21%
```

### Excel Export
- Main sheet: Ranked candidates
- Summary sheet: Statistics dashboard

### JSON Export
```json
{
  "candidates": [
    {
      "Rank": 1,
      "Candidate ID": 0,
      "Candidate Name": "John Doe",
      "Similarity Score": 0.8543,
      "Match Type": "Excellent Match"
    }
  ],
  "export_date": "2024-01-15T10:30:00"
}
```

---

## Troubleshooting

### Issue: Module not found errors
**Solution**: Make sure you activated virtual environment and installed requirements
```bash
pip install -r requirements.txt
```

### Issue: NLTK data error
**Solution**: Download NLTK data
```bash
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
"
```

### Issue: Slow processing
**Solution**: Reduce max_features or batch size
- Edit `src/feature_extraction.py`
- Reduce `max_features` from 5000 to 2000

### Issue: Out of memory
**Solution**: Process resumes in batches or reduce feature count

### Issue: Streamlit not starting
**Solution**: Make sure port 8501 is free
```bash
streamlit run src/app.py --server.port=8502  # Use different port
```

---

## Next Steps

1. **Read Full Documentation**: `docs/DOCUMENTATION.md`
2. **Understand Architecture**: `docs/SYSTEM_ARCHITECTURE.md`
3. **API Reference**: `docs/API.md`
4. **Run Tests**: `python test_system.py`
5. **Customize**: Modify `config.ini` for your needs
6. **Deploy**: Follow deployment guide in docs

---

## Performance Tips

1. **Batch Processing**
   ```python
   # Process 1000 resumes in 5 minutes (100/min)
   ```

2. **Enable Caching**
   ```python
   # Cache TF-IDF vectors to avoid recomputation
   ```

3. **Use Top-N Wisely**
   ```python
   # Top 100 candidates found in ~1 minute
   ```

4. **Optimize Threshold**
   ```python
   # threshold=0.5 is faster than threshold=0.2
   ```

---

## Key Concepts

### TF-IDF (Term Frequency-Inverse Document Frequency)
- Converts text to numerical vectors
- Gives importance to rare but meaningful words
- Fast and interpretable

### Cosine Similarity
- Measures angle between TF-IDF vectors
- Score between 0 (different) and 1 (identical)
- Works well with sparse vectors

### Candidate Matching
- Compares resume vs job using cosine similarity
- Ranks candidates by match score
- Filters by threshold

---

## Real-World Example

```python
from main import ResomeScreeningPipeline

# Your company's job description
job_desc = """
Senior Backend Engineer

Required:
- 5+ years Python development
- REST API design experience
- Microservices architecture knowledge
- PostgreSQL expertise

Nice to have:
- AWS experience
- Docker/Kubernetes
- CI/CD pipeline setup
"""

# Load candidate resumes (100 candidates)
candidates = [... list of resume texts ...]
candidate_names = [... list of names ...]

# Run screening
pipeline = ResomeScreeningPipeline()
results = pipeline.run_complete_pipeline(
    resumes=candidates,
    job_description=job_desc,
    candidate_names=candidate_names,
    shortlist_threshold=0.5,       # Only good matches
    top_candidates=10,
    export_format='excel'
)

# Get top 5 for interviews
top_5 = results['shortlist'].head(5)
print(top_5)  # John, Jane, Bob, Alice, Chris

# Save and share
top_5.to_csv('interview_candidates.csv')
```

---

## Support & Help

- **Issues**: Check troubleshooting section above
- **Documentation**: Read `docs/` folder
- **Tests**: Run `python test_system.py`
- **Examples**: Check `main.py` for complete pipeline

---

## What's Next?

After screening:
1. ✅ Share shortlist with hiring manager
2. ✅ Schedule interviews with top candidates
3. ✅ Collect feedback on hire quality
4. ✅ Improve system over time

---

**Happy Screening!** 🎉

For more information, see README.md and full documentation in docs/ folder.
