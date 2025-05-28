# Combined DPIA Analyzer & Case Creator

## Overview
This tool combines text analysis and DPIA case creation into a single workflow. It analyzes text for scanning requests using the pathology format, then automatically creates a DPIA case in Pega with the analysis results.

## What It Does
1. **📝 Analyzes Text**: Scans for scanning requests, DPIA mentions, pathology terms
2. **📊 Generates Summary**: Creates structured pathology table with 16 columns
3. **🏢 Creates Pega Case**: Automatically submits DPIA case with analysis results
4. **📋 Provides Results**: Shows both analysis and case creation status

## Usage Methods

### Method 1: Echo and Pipe (Your Requested Format)
```bash
echo "Your DPIA text here" | ./analyze_dpia
```

### Method 2: File Input
```bash
./analyze_dpia filename.txt
```

### Method 3: Interactive Input
```bash
./analyze_dpia
# Then type your text and press Ctrl+D
```

### Method 4: With Custom Title
```bash
echo "Your text" | ./analyze_dpia --title "Custom Case Title"
./analyze_dpia filename.txt --title "Custom Case Title"
```

### Method 5: Show Pathology Table
```bash
./analyze_dpia filename.txt --table
```

### Method 6: Save All Results
```bash
./analyze_dpia filename.txt --save --table
```

## Examples

### Example 1: Quick Text Analysis (Your Requested Method)
```bash
echo "DPIA scanning request for biospecimen BS-001 with H&E staining" | ./analyze_dpia
```

### Example 2: File with Custom Title
```bash
./analyze_dpia sample_text.txt --title "Urgent DPIA Review"
```

### Example 3: Complete Analysis with Table and Save
```bash
./analyze_dpia sample_text.txt --table --save
```

### Example 4: Clipboard Analysis (macOS)
```bash
pbpaste | ./analyze_dpia --title "Clipboard Analysis"
```

## Output

The tool provides:

### 📊 Analysis Results
- Number of scanning requests found
- Text length analyzed
- Pathology table data (16 columns)

### 🏢 Pega Case Creation
- **Case ID**: Auto-generated (e.g., ROCHE-PATHWORKS-WORK C-16365)
- **Title**: Auto-generated or custom
- **Description**: Detailed analysis summary with findings

### 📋 Optional Outputs
- **--table**: Shows full pathology table
- **--save**: Saves JSON analysis and pathology table to files

## Sample Output

```
🔍 DPIA Analyzer & Case Creator
==================================================
📝 Step 1: Analyzing text for scanning requests...
   ✅ Found 7 scanning request entries

🏢 Step 2: Creating DPIA case in Pega...
   Title: Scanning request - 7 items found - 2025-05-27 11:26
   ✅ DPIA case created successfully!
   Case ID: ROCHE-PATHWORKS-WORK C-16365

==================================================
📊 FINAL RESULTS
==================================================
📈 Analysis: 7 scanning requests found
✅ Case Created: ROCHE-PATHWORKS-WORK C-16365
```

## Integration with Other Tools

This tool combines and enhances your existing tools:

| Tool | Purpose | Usage |
|------|---------|-------|
| `./dpia` | Simple case creation | Quick DPIA cases |
| `./scan_summary` | Text analysis only | Analysis without case creation |
| `./analyze_dpia` | **Combined workflow** | **Analysis + Case creation** |

## Advanced Features

### Custom Titles
```bash
echo "text" | ./analyze_dpia --title "Priority DPIA Assessment"
```

### Batch Processing
```bash
for file in *.txt; do
    echo "Processing $file..."
    ./analyze_dpia "$file" --save
done
```

### Pipeline Integration
```bash
curl -s "https://api.example.com/data" | ./analyze_dpia --title "API Data Analysis"
```

## Files Created
- `dpia_analyzer.py` - Main combined tool
- `analyze_dpia` - Shell wrapper for easy execution
- `dpia_analysis_TIMESTAMP.json` - Detailed results (with --save)
- `pathology_table_TIMESTAMP.txt` - Pathology table (with --save)

## Perfect for Your Workflow! 🎯

**Before**: Two separate steps
```bash
echo "text" | ./scan_summary    # Analyze
./dpia                          # Create case
```

**Now**: Single combined step
```bash
echo "text" | ./analyze_dpia    # Analyze + Create case automatically!
``` 