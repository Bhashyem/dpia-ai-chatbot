# DPIA Scanning Request Tool

## Overview
This tool creates "Scanning request" cases in Pega with DPIA (Data Privacy Impact Assessment) context using a single command.

## Usage

### Method 1: Using Python script directly
```bash
python3 create_dpia.py
```

### Method 2: Using the shortcut (recommended)
```bash
./dpia
```

### With custom title and description
```bash
./dpia "Custom Scanning Title" "Custom description for the DPIA scanning request"
```

## Examples

### Default case (auto-generated title with timestamp)
```bash
./dpia
```
Creates: "Scanning request - 2025-05-27 10:53"

### Custom title only
```bash
./dpia "Urgent Privacy Review"
```
Creates: "Urgent Privacy Review" with default DPIA description

### Custom title and description
```bash
./dpia "New System Assessment" "Privacy impact assessment needed for new data processing system"
```

## Output
The tool will show:
- ✅ Success confirmation
- 📋 Case ID (e.g., ROCHE-PATHWORKS-WORK C-16360)
- 📋 Full Pega response details

## Configuration
- **Pega URL**: https://roche-gtech-dt1.pegacloud.net/prweb/api/v1
- **Case Type**: Roche-Pathworks-Work-DPIA
- **Channel**: API

## Files
- `create_dpia.py` - Main Python script
- `dpia` - Shell wrapper for easy execution
- `DPIA_USAGE.md` - This usage guide 