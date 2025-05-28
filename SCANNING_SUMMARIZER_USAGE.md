# Scanning Request Summarizer Tool

## Overview
This tool scans any text for "Scanning request" keywords and related terms, then summarizes the findings in the specified pathology format with all 16 columns.

## Features
- 🔍 **Keyword Detection**: Finds scanning requests, DPIA mentions, pathology terms
- 📊 **Structured Output**: Formats results in your specified pathology table format
- 📄 **Multiple Input Methods**: File input or interactive text input
- 💾 **Export Options**: Table format or JSON output with save functionality

## Usage

### Method 1: Analyze a text file
```bash
./scan_summary filename.txt
```

### Method 2: Interactive text input
```bash
./scan_summary
# Then type or paste your text and press Ctrl+D when done
```

### Method 3: JSON output format
```bash
./scan_summary filename.txt --json
```

### Method 4: Save results to file
```bash
./scan_summary filename.txt --save
```

### Method 5: Combined options
```bash
./scan_summary filename.txt --json --save
```

## Output Format

The tool outputs data in your specified format with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Pathology Request No. | Auto-generated ID | SR-20250527-001 |
| Biospecimen | Extracted specimen info | sample bs-001 |
| Service Type | Always "DPIA Scanning Request" | DPIA Scanning Request |
| SR ID | Scanning request ID | DPIA-001 |
| Special stain | Extracted staining info | H&E staining |
| Assay Instructions | Extracted assay details | immunohistochemistry |
| Trim Instructions | Extracted trim info | serial sectioning |
| Sectioning Instructions | Extracted section info | 4 microns |
| label | Brief description | scanning request for... |
| visualization | Always "Text Analysis" | Text Analysis |
| Assay ID | Auto-generated | ASSAY-001 |
| Block id | Extracted block info | BLK-2025-001 |
| Slide Count | Extracted slide numbers | 12 |
| Slide id | Extracted slide info | 5 sections |
| DPIA Batch run | Timestamp | 2025-05-27 11:12:09 |
| Status | Always "Identified" or "No Match" | Identified |

## Keywords Detected

The tool searches for these terms (case-insensitive):
- scanning request / scan request
- dpia
- data privacy / privacy assessment
- pathology
- biospecimen / specimen / sample
- assay / test / analysis
- slide / block / stain
- trim / sectioning

## Examples

### Example 1: Basic usage
```bash
./scan_summary sample_text.txt
```

### Example 2: Analyze clipboard content
```bash
pbpaste | ./scan_summary
```

### Example 3: Process multiple files
```bash
for file in *.txt; do
    echo "Processing $file..."
    ./scan_summary "$file" --save
done
```

## Files
- `scanning_summarizer.py` - Main Python script
- `scan_summary` - Shell wrapper for easy execution
- `sample_text.txt` - Example input file
- `SCANNING_SUMMARIZER_USAGE.md` - This usage guide

## Integration with DPIA Tool

This tool complements your DPIA creation tool:
1. Use `./dpia` to create scanning request cases in Pega
2. Use `./scan_summary` to analyze and summarize text content in pathology format

Both tools work together for comprehensive DPIA workflow management! 