#!/usr/bin/env python3
"""
Scanning Request Summarizer Tool
Scans text for "Scanning request" keywords and summarizes findings in pathology format.
Enhanced with therapeutic area detection.
"""

import re
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

class ScanningRequestSummarizer:
    def __init__(self):
        self.pathology_headers = [
            "Pathology Request No.",
            "Therapeutic Area",
            "Procedure",
            "Assay Type/Staining Type",
            "PI",
            "Pathologist",
            "Project Title",
            "Request Purpose",
            "Assay Instructions",
            "Trim Instructions",
            "Sectioning Instructions",
            "Block id",
            "Status"
        ]
        
        # Mandatory fields that must be provided before creating DPIA request
        self.mandatory_fields = [
            "PI",
            "Pathologist", 
            "Therapeutic Area",
            "Procedure",
            "Assay Type/Staining Type",
            "Project Title",
            "Request Purpose"
        ]
        
        # Therapeutic areas with their keywords
        self.therapeutic_areas = {
            "CVRM": [
                "cardiovascular", "cardiac", "heart", "vascular", "blood pressure", 
                "hypertension", "atherosclerosis", "coronary", "myocardial", "stroke",
                "thrombosis", "anticoagulant", "lipid", "cholesterol", "cvrm"
            ],
            "Neurology": [
                "neurological", "neurology", "brain", "spinal", "alzheimer", "parkinson",
                "multiple sclerosis", "epilepsy", "seizure", "dementia", "cognitive",
                "neurodegeneration", "neural", "neuron", "synapse", "ms", "als",
                "lung", "respiratory", "pulmonary", "stem cell", "stem cells", "at2"
            ],
            "Oncology": [
                "cancer", "tumor", "oncology", "chemotherapy", "radiation", "metastasis",
                "carcinoma", "sarcoma", "lymphoma", "leukemia", "malignant", "benign",
                "biopsy", "cytotoxic", "immunotherapy", "targeted therapy"
            ],
            "Ophthalmology": [
                "eye", "vision", "retina", "cornea", "glaucoma", "cataract", "macular",
                "ophthalmology", "ophthalmic", "visual", "intraocular", "vitreous",
                "diabetic retinopathy", "age-related macular degeneration", "amd"
            ],
            "Infectious Diseases": [
                "infection", "infectious", "bacterial", "viral", "fungal", "antibiotic",
                "antimicrobial", "pathogen", "sepsis", "pneumonia", "hepatitis",
                "hiv", "tuberculosis", "malaria", "vaccine", "immunization"
            ],
            "Immunology": [
                "immune", "immunology", "autoimmune", "inflammation", "inflammatory",
                "rheumatoid", "lupus", "psoriasis", "crohn", "ulcerative colitis",
                "immunosuppressive", "cytokine", "antibody", "antigen", "t-cell", "b-cell"
            ]
        }
        
        # Procedure types with their keywords
        self.procedures = {
            "Bright-field (BF)": [
                "bright field", "brightfield", "bf", "light microscopy", "transmitted light",
                "h&e", "hematoxylin", "eosin", "histology", "morphology"
            ],
            "Fluorescence (IF)": [
                "fluorescence", "fluorescent", "if", "immunofluorescence", "fitc", "tritc",
                "dapi", "gfp", "rfp", "alexa", "cy3", "cy5", "confocal"
            ],
            "BF+IF": [
                "bright field and fluorescence", "bf+if", "bf and if", "combined",
                "brightfield and fluorescence", "light and fluorescence"
            ]
        }
        
        # Assay Type/Staining Type with their keywords
        self.assay_staining_types = {
            "H&E": [
                "h&e", "hematoxylin and eosin", "hematoxylin", "eosin", "he stain",
                "routine stain", "standard stain", "morphology"
            ],
            "IHC": [
                "ihc", "immunohistochemistry", "immunohistochemical", "antibody staining",
                "primary antibody", "secondary antibody", "chromogen", "dab", "peroxidase"
            ],
            "Special Stain": [
                "special stain", "trichrome", "pas", "periodic acid schiff", "congo red",
                "silver stain", "reticulin", "elastic", "mucin", "glycogen", "iron stain"
            ],
            "Other": [
                "other stain", "custom stain", "research stain", "experimental stain"
            ]
        }
        
        # Keywords to look for in text
        self.scanning_keywords = [
            "scanning request",
            "scan request",
            "dpia",
            "data privacy",
            "privacy assessment",
            "pathology",
            "biospecimen",
            "assay",
            "slide",
            "block",
            "stain"
        ]
    
    def detect_therapeutic_area(self, text: str) -> str:
        """Detect therapeutic area from text based on keywords"""
        text_lower = text.lower()
        
        # Count matches for each therapeutic area
        area_scores = {}
        for area, keywords in self.therapeutic_areas.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', text_lower))
            area_scores[area] = score
        
        # Find the area with highest score
        max_score = max(area_scores.values())
        if max_score > 0:
            for area, score in area_scores.items():
                if score == max_score:
                    return area
        
        return "Unknown"
    
    def prompt_for_therapeutic_area(self, detected_area: str) -> str:
        """Prompt user for therapeutic area if not detected or if they want to override"""
        print(f"\n🔬 Therapeutic Area Detection:")
        print(f"   Detected: {detected_area}")
        
        if detected_area == "Unknown":
            print("   ⚠️  No therapeutic area keywords found in text")
        
        print("\nAvailable therapeutic areas:")
        areas = list(self.therapeutic_areas.keys()) + ["Unknown"]
        for i, area in enumerate(areas, 1):
            print(f"   {i}. {area}")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_area}' or enter number (1-{len(areas)}) to select different area: ").strip()
                
                if not choice:
                    return detected_area
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(areas):
                    selected_area = areas[choice_num - 1]
                    print(f"   ✅ Selected: {selected_area}")
                    return selected_area
                else:
                    print(f"   ❌ Please enter a number between 1 and {len(areas)}")
            except ValueError:
                print("   ❌ Please enter a valid number or press Enter")
            except KeyboardInterrupt:
                print(f"\n   Using detected area: {detected_area}")
                return detected_area

    def detect_procedure(self, text: str) -> str:
        """Detect procedure type from text based on keywords"""
        text_lower = text.lower()
        
        # Count matches for each procedure type
        procedure_scores = {}
        for procedure, keywords in self.procedures.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', text_lower))
            procedure_scores[procedure] = score
        
        # Check for combined procedures (BF+IF gets priority if both are found)
        bf_score = procedure_scores.get("Bright-field (BF)", 0)
        if_score = procedure_scores.get("Fluorescence (IF)", 0)
        combined_score = procedure_scores.get("BF+IF", 0)
        
        # If both BF and IF keywords are found, suggest BF+IF
        if bf_score > 0 and if_score > 0:
            return "BF+IF"
        
        # Find the procedure with highest score
        max_score = max(procedure_scores.values())
        if max_score > 0:
            for procedure, score in procedure_scores.items():
                if score == max_score:
                    return procedure
        
        return "Unknown"
    
    def prompt_for_procedure(self, detected_procedure: str) -> str:
        """Prompt user for procedure type if not detected or if they want to override"""
        print(f"\n🔬 Procedure Detection:")
        print(f"   Detected: {detected_procedure}")
        
        if detected_procedure == "Unknown":
            print("   ⚠️  No procedure keywords found in text")
        
        print("\nAvailable procedures:")
        procedures = list(self.procedures.keys()) + ["Unknown"]
        for i, procedure in enumerate(procedures, 1):
            print(f"   {i}. {procedure}")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_procedure}' or enter number (1-{len(procedures)}) to select different procedure: ").strip()
                
                if not choice:
                    return detected_procedure
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(procedures):
                    selected_procedure = procedures[choice_num - 1]
                    print(f"   ✅ Selected: {selected_procedure}")
                    return selected_procedure
                else:
                    print(f"   ❌ Please enter a number between 1 and {len(procedures)}")
            except ValueError:
                print("   ❌ Please enter a valid number or press Enter")
            except KeyboardInterrupt:
                print(f"\n   Using detected procedure: {detected_procedure}")
                return detected_procedure

    def detect_assay_staining_type(self, text: str) -> str:
        """Detect assay/staining type from text based on keywords"""
        text_lower = text.lower()
        
        # Count matches for each assay/staining type
        staining_scores = {}
        for staining_type, keywords in self.assay_staining_types.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', text_lower))
            staining_scores[staining_type] = score
        
        # Find the staining type with highest score
        max_score = max(staining_scores.values())
        if max_score > 0:
            for staining_type, score in staining_scores.items():
                if score == max_score:
                    return staining_type
        
        # Check for fluorescence indicators (might suggest "Other" for fluorescent staining)
        fluorescence_indicators = ["tritc", "dapi", "fitc", "fluorescent", "fluorescence", "gfp", "rfp"]
        if any(indicator in text_lower for indicator in fluorescence_indicators):
            return "Other"
        
        return "Unknown"
    
    def prompt_for_assay_staining_type(self, detected_staining: str) -> str:
        """Prompt user for assay/staining type if not detected or if they want to override"""
        print(f"\n🧪 Assay Type/Staining Type Detection:")
        print(f"   Detected: {detected_staining}")
        
        if detected_staining == "Unknown":
            print("   ⚠️  No assay/staining type keywords found in text")
        
        print("\nAvailable assay/staining types:")
        staining_types = list(self.assay_staining_types.keys()) + ["Unknown"]
        for i, staining_type in enumerate(staining_types, 1):
            print(f"   {i}. {staining_type}")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_staining}' or enter number (1-{len(staining_types)}) to select different type: ").strip()
                
                if not choice:
                    return detected_staining
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(staining_types):
                    selected_staining = staining_types[choice_num - 1]
                    print(f"   ✅ Selected: {selected_staining}")
                    return selected_staining
                else:
                    print(f"   ❌ Please enter a number between 1 and {len(staining_types)}")
            except ValueError:
                print("   ❌ Please enter a valid number or press Enter")
            except KeyboardInterrupt:
                print(f"\n   Using detected staining type: {detected_staining}")
                return detected_staining

    def validate_mandatory_fields(self, data: Dict[str, Any]) -> bool:
        """Validate that all mandatory fields are provided and not 'Unknown' - Interactive version"""
        missing_fields = []
        
        for field in self.mandatory_fields:
            if field not in data or data[field] == "Unknown" or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n⚠️  MANDATORY FIELD VALIDATION:")
            print(f"   Found {len(missing_fields)} missing mandatory field(s)")
            
            # Check if we can prompt interactively (not in a pipe)
            if sys.stdin.isatty():
                # Interactive prompting for missing fields
                for field in missing_fields:
                    print(f"\n📋 Missing Field: {field}")
                    
                    if field == "Therapeutic Area":
                        data[field] = self.prompt_for_therapeutic_area("Unknown")
                    elif field == "Procedure":
                        data[field] = self.prompt_for_procedure("Unknown")
                    elif field == "Assay Type/Staining Type":
                        data[field] = self.prompt_for_assay_staining_type("Unknown")
                    elif field == "PI":
                        data[field] = self.prompt_for_pi("Unknown")
                    elif field == "Pathologist":
                        data[field] = self.prompt_for_pathologist("Unknown")
                    elif field == "Project Title":
                        data[field] = self.prompt_for_project_title("Unknown")
                    elif field == "Request Purpose":
                        data[field] = self.prompt_for_request_purpose("Unknown")
            else:
                print(f"\n📝 Running in non-interactive mode (pipe/redirect)")
                print(f"   Cannot prompt for missing fields. Use interactive mode for field input.")
        
        # Final validation check
        final_missing = []
        for field in self.mandatory_fields:
            if field not in data or data[field] == "Unknown" or not data[field]:
                final_missing.append(field)
        
        if final_missing:
            print(f"\n❌ VALIDATION FAILED: Still missing mandatory fields:")
            for field in final_missing:
                print(f"   - {field}")
            return False
        
        print(f"\n✅ VALIDATION PASSED: All mandatory fields provided")
        return True

    def extract_scanning_requests(self, text: str) -> List[Dict[str, Any]]:
        """Extract scanning request information from text"""
        
        # Detect therapeutic area
        therapeutic_area = self.detect_therapeutic_area(text)
        
        # Detect procedure
        procedure = self.detect_procedure(text)
        
        # Detect assay/staining type
        assay_staining_type = self.detect_assay_staining_type(text)
        
        # Detect PI and Pathologist
        pi = self.detect_pi(text)
        pathologist = self.detect_pathologist(text)
        
        # Detect Project Title and Request Purpose
        project_title = self.detect_project_title(text)
        request_purpose = self.detect_request_purpose(text)
        
        text_lower = text.lower()
        
        # Look for scanning request patterns
        scanning_patterns = [
            r'scanning\s+request[s]?',
            r'scan\s+request[s]?',
            r'dpia\s+request[s]?',
            r'privacy\s+assessment[s]?'
        ]
        
        found_requests = []
        request_count = 0
        
        # Search for patterns
        for pattern in scanning_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                request_count += 1
                
                # Extract context around the match
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                # Generate request data
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                request_id = f"SR-{datetime.now().strftime('%Y%m%d')}-{request_count:03d}"
                
                request_data = {
                    "Pathology Request No.": request_id,
                    "Therapeutic Area": therapeutic_area,
                    "Procedure": procedure,
                    "Assay Type/Staining Type": assay_staining_type,
                    "PI": pi,
                    "Pathologist": pathologist,
                    "Project Title": project_title,
                    "Request Purpose": request_purpose,
                    "Assay Instructions": self._extract_assay_info(context),
                    "Trim Instructions": self._extract_trim_info(context),
                    "Sectioning Instructions": self._extract_section_info(context),
                    "Block id": self._extract_block_id(context),
                    "Status": "Detected"
                }
                
                # Validate mandatory fields (now interactive)
                if not self.validate_mandatory_fields(request_data):
                    request_data["Status"] = "Validation Failed"
                
                found_requests.append(request_data)
        
        # If no specific scanning requests found, create a general entry
        if not found_requests:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            request_id = f"SR-{datetime.now().strftime('%Y%m%d')}-001"
            
            # Check if text contains research-related content
            research_keywords = ["cells", "imaging", "quantification", "staining", "analysis", "study", "research"]
            has_research_content = any(keyword in text_lower for keyword in research_keywords)
            
            status = "Research Content" if has_research_content else "No Match"
            service_type = "Research Analysis" if has_research_content else "Text Analysis"
            
            default_entry = {
                "Pathology Request No.": request_id,
                "Therapeutic Area": therapeutic_area,
                "Procedure": procedure,
                "Assay Type/Staining Type": assay_staining_type,
                "PI": pi,
                "Pathologist": pathologist,
                "Project Title": project_title,
                "Request Purpose": request_purpose,
                "Assay Instructions": self._extract_assay_info(text),
                "Trim Instructions": "N/A",
                "Sectioning Instructions": self._extract_section_info(text),
                "Block id": "N/A",
                "Status": status
            }
            
            # Validate mandatory fields (now interactive)
            if not self.validate_mandatory_fields(default_entry):
                default_entry["Status"] = "Validation Failed"
            
            found_requests.append(default_entry)
        
        return found_requests
    
    def _extract_biospecimen(self, text: str) -> str:
        """Extract biospecimen information from text"""
        text_lower = text.lower()
        
        biospecimen_patterns = [
            r'biospecimen[:\-\s]*([^\n\r,;.]*)',
            r'specimen[:\-\s]*([^\n\r,;.]*)',
            r'sample[:\-\s]*([^\n\r,;.]*)',
            r'tissue[:\-\s]*([^\n\r,;.]*)',
            r'cells?[:\-\s]*([^\n\r,;.]*)',
            r'lung[:\-\s]*([^\n\r,;.]*)',
            r'blood[:\-\s]*([^\n\r,;.]*)'
        ]
        
        for pattern in biospecimen_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                return match.group(1).strip()[:50]
        
        # Look for specific biospecimen types
        biospecimen_types = ["lung", "blood", "tissue", "cells", "serum", "plasma", "biopsy"]
        for bio_type in biospecimen_types:
            if bio_type in text_lower:
                return bio_type.title()
        
        return "N/A"
    
    def _extract_stain_info(self, text: str) -> str:
        """Extract staining information from text"""
        text_lower = text.lower()
        
        stain_patterns = [
            r'stain[ed|ing]*[:\-\s]*([^\n\r,;.]*)',
            r'tritc[:\-\s]*([^\n\r,;.]*)',
            r'dapi[:\-\s]*([^\n\r,;.]*)',
            r'fluorescent[:\-\s]*([^\n\r,;.]*)',
            r'immunofluorescence[:\-\s]*([^\n\r,;.]*)'
        ]
        
        stains_found = []
        for pattern in stain_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if match.group(1).strip():
                    stains_found.append(match.group(1).strip())
        
        # Look for common stain types
        common_stains = ["tritc", "dapi", "fitc", "h&e", "immunofluorescence", "fluorescent"]
        for stain in common_stains:
            if stain in text_lower:
                stains_found.append(stain.upper())
        
        if stains_found:
            return ", ".join(list(set(stains_found))[:3])  # Limit to 3 stains
        
        return "N/A"
    
    def _extract_assay_info(self, text: str) -> str:
        """Extract assay information from text"""
        text_lower = text.lower()
        
        assay_patterns = [
            r'assay[:\-\s]*([^\n\r,;.]*)',
            r'analysis[:\-\s]*([^\n\r,;.]*)',
            r'quantification[:\-\s]*([^\n\r,;.]*)',
            r'imaging[:\-\s]*([^\n\r,;.]*)',
            r'measurement[:\-\s]*([^\n\r,;.]*)'
        ]
        
        for pattern in assay_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                return match.group(1).strip()[:50]
        
        # Look for specific assay types
        assay_types = ["imaging", "quantification", "analysis", "measurement", "counting"]
        for assay_type in assay_types:
            if assay_type in text_lower:
                return assay_type.title()
        
        return "N/A"
    
    def _extract_trim_info(self, text: str) -> str:
        """Extract trim instructions from text"""
        text_lower = text.lower()
        
        trim_patterns = [
            r'trim[ming]*[:\-\s]*([^\n\r,;.]*)',
            r'cutting[:\-\s]*([^\n\r,;.]*)',
            r'preparation[:\-\s]*([^\n\r,;.]*)'
        ]
        
        for pattern in trim_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                return match.group(1).strip()[:50]
        
        return "N/A"
    
    def _extract_section_info(self, text: str) -> str:
        """Extract sectioning instructions from text"""
        text_lower = text.lower()
        
        section_patterns = [
            r'section[ing]*[:\-\s]*([^\n\r,;.]*)',
            r'slice[s]*[:\-\s]*([^\n\r,;.]*)',
            r'per\s+section[:\-\s]*([^\n\r,;.]*)'
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                return match.group(1).strip()[:50]
        
        # Look for section-related terms
        if "per lung section" in text_lower:
            return "Per lung section"
        elif "section" in text_lower:
            return "Standard sectioning"
        
        return "N/A"
    
    def _extract_label_info(self, text: str) -> str:
        """Extract label information from text"""
        text_lower = text.lower()
        
        # Extract first meaningful phrase or sentence
        sentences = text.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 10:
                return first_sentence[:100] + "..." if len(first_sentence) > 100 else first_sentence
        
        return text[:100] + "..." if len(text) > 100 else text
    
    def _extract_visualization_info(self, text: str) -> str:
        """Extract visualization information from text"""
        text_lower = text.lower()
        
        viz_keywords = ["imaging", "microscopy", "fluorescence", "confocal", "visualization", "image"]
        for keyword in viz_keywords:
            if keyword in text_lower:
                return keyword.title()
        
        return "Standard"
    
    def _extract_assay_id(self, text: str) -> str:
        """Extract assay ID from text"""
        text_lower = text.lower()
        
        # Look for ID patterns
        id_patterns = [
            r'assay[:\-\s]*id[:\-\s]*([a-zA-Z0-9\-]+)',
            r'id[:\-\s]*([a-zA-Z0-9\-]+)',
            r'([a-zA-Z]+\-\d+)'
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).upper()
        
        return "N/A"
    
    def _extract_block_id(self, text: str) -> str:
        """Extract block ID from text"""
        text_lower = text.lower()
        
        block_patterns = [
            r'block[:\-\s]*id[:\-\s]*([a-zA-Z0-9\-]+)',
            r'block[:\-\s]*([a-zA-Z0-9\-]+)'
        ]
        
        for pattern in block_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).upper()
        
        return "N/A"
    
    def _extract_slide_id(self, text: str) -> str:
        """Extract slide ID from text"""
        text_lower = text.lower()
        
        slide_patterns = [
            r'slide[:\-\s]*id[:\-\s]*([a-zA-Z0-9\-]+)',
            r'slide[:\-\s]*([a-zA-Z0-9\-]+)'
        ]
        
        for pattern in slide_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).upper()
        
        return "N/A"

    def _extract_field(self, text: str, keywords: List[str]) -> str:
        """Extract field information based on keywords (legacy method)"""
        text_lower = text.lower()
        
        for keyword in keywords:
            pattern = rf'{keyword}[:\-\s]*([^\n\r]*)'
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                return match.group(1).strip()[:50]  # Limit length
        
        return "N/A"
    
    def _extract_numbers(self, text: str, keywords: List[str]) -> str:
        """Extract numbers associated with keywords"""
        text_lower = text.lower()
        
        for keyword in keywords:
            pattern = rf'{keyword}[:\-\s]*(\d+)'
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1)
        
        return "0"
    
    def format_as_table(self, data: List[Dict[str, Any]]) -> str:
        """Format data as a table"""
        if not data:
            return "No data to display"
        
        # Create header
        header = "\t".join(self.pathology_headers)
        
        # Create rows
        rows = []
        for entry in data:
            row = []
            for header_name in self.pathology_headers:
                row.append(str(entry.get(header_name, "N/A")))
            rows.append("\t".join(row))
        
        return header + "\n" + "\n".join(rows)
    
    def summarize_text(self, text: str, output_format: str = "table") -> str:
        """Main function to summarize scanning requests in text"""
        
        print("🔍 Scanning text for DPIA/Scanning requests...")
        print(f"   Text length: {len(text)} characters")
        
        # Extract scanning requests
        extracted_data = self.extract_scanning_requests(text)
        
        print(f"   Found: {len(extracted_data)} scanning request entries")
        
        if output_format == "json":
            return json.dumps(extracted_data, indent=2)
        elif output_format == "table":
            return self.format_as_table(extracted_data)
        else:
            return str(extracted_data)

    def detect_pi(self, text: str) -> str:
        """Detect Primary Investigator from text"""
        text_lower = text.lower()
        
        # Patterns to look for PI information (explicit patterns first - highest priority)
        explicit_pi_patterns = [
            r'primary investigator[:\-\s]*([a-zA-Z\s\.]+)',
            r'pi[:\-\s]*([a-zA-Z\s\.]+)',
            r'pi\s+is\s+([a-zA-Z\s\.]+)',
            r'principal investigator[:\-\s]*([a-zA-Z\s\.]+)',
            r'lead researcher[:\-\s]*([a-zA-Z\s\.]+)'
        ]
        
        # First, try explicit patterns (highest priority)
        for pattern in explicit_pi_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                # Clean up the name (remove extra spaces, capitalize)
                name = match.group(1).strip()
                # Remove common words that might be captured
                exclude_words = ['is', 'was', 'will', 'be', 'the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'quantification', 'analysis', 'study', 'research', 'cells', 'cell', 'section', 'lung', 'stem', 'total', 'area', 'normalized']
                name_parts = [word.capitalize() for word in name.split() if word.lower() not in exclude_words and len(word) > 1]
                if name_parts and len(' '.join(name_parts)) > 2:
                    # Check if it looks like a real name (has at least one word that could be a name)
                    potential_name = ' '.join(name_parts)
                    if any(part[0].isupper() and len(part) > 2 for part in name_parts):
                        return potential_name[:50]  # Limit length
        
        # Only if no explicit patterns found, try enhanced contextual detection
        # Look for capitalized words that could be names in research context
        research_context_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|is|was|conducted?|performing?|leading|responsible)',
            r'(?:conducted?|performed?|led|by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:research|study|investigation|experiment)',
            r'(?:researcher|investigator|scientist)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:and|&)\s+(?:team|colleagues|lab)',
            r'(?:dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:lab|laboratory|group)',
            # Simple pattern for standalone names in research context
            r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b'
        ]
        
        # Common non-name words to exclude
        exclude_names = {
            'scanning', 'request', 'analysis', 'study', 'research', 'data', 'privacy', 
            'assessment', 'pathology', 'biospecimen', 'assay', 'slide', 'block', 
            'stain', 'fluorescence', 'imaging', 'quantification', 'lung', 'stem', 
            'cells', 'cell', 'neurology', 'oncology', 'cardiovascular', 'immunology',
            'bright', 'field', 'microscopy', 'procedure', 'therapeutic', 'area',
            'project', 'title', 'purpose', 'instructions', 'sectioning', 'trim',
            'unknown', 'other', 'special', 'routine', 'standard', 'primary',
            'secondary', 'antibody', 'chromogen', 'peroxidase', 'hematoxylin',
            'eosin', 'trichrome', 'congo', 'silver', 'reticulin', 'elastic',
            'mucin', 'glycogen', 'iron', 'custom', 'experimental', 'total',
            'normalized', 'section', 'detection', 'identified', 'detected',
            'rmim', 'wmim', 'tritc', 'dapi'  # Add treatment names to exclude
        }
        
        potential_names = []
        
        for pattern in research_context_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name_candidate = match.group(1).strip()
                # Clean and validate the name
                name_parts = [word for word in name_candidate.split() if word.lower() not in exclude_names]
                
                if name_parts:
                    clean_name = ' '.join(name_parts)
                    # Check if it looks like a real name
                    if (len(clean_name) >= 3 and 
                        len(clean_name) <= 50 and
                        all(part.isalpha() for part in name_parts) and
                        not any(word.lower() in exclude_names for word in name_parts)):
                        potential_names.append(clean_name)
        
        # Return the first reasonable name found
        if potential_names:
            # Prefer shorter names (likely to be actual names vs phrases)
            potential_names.sort(key=len)
            return potential_names[0]
        
        return "Unknown"
    
    def detect_pathologist(self, text: str) -> str:
        """Detect Pathologist from text"""
        text_lower = text.lower()
        
        # Patterns to look for Pathologist information
        pathologist_patterns = [
            r'pathologist[:\-\s]*([a-zA-Z\s\.]+)',
            r'pathology[:\-\s]*([a-zA-Z\s\.]+)',
            r'reviewed by[:\-\s]*([a-zA-Z\s\.]+)',
            r'diagnosed by[:\-\s]*([a-zA-Z\s\.]+)',
            r'dr\.?\s*([a-zA-Z\s\.]+)',
            r'doctor[:\-\s]*([a-zA-Z\s\.]+)'
        ]
        
        for pattern in pathologist_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                # Clean up the name (remove extra spaces, capitalize)
                name = match.group(1).strip()
                # Remove common words that might be captured
                exclude_words = ['is', 'was', 'will', 'be', 'the', 'a', 'an', 'and', 'or', 'but', 'department', 'lab', 'laboratory']
                name_parts = [word.capitalize() for word in name.split() if word.lower() not in exclude_words]
                if name_parts and len(' '.join(name_parts)) > 2:
                    return ' '.join(name_parts)[:50]  # Limit length
        
        return "Unknown"
    
    def prompt_for_pi(self, detected_pi: str) -> str:
        """Prompt user for Primary Investigator if not detected"""
        print(f"\n👨‍🔬 Primary Investigator (PI) Detection:")
        print(f"   Detected: {detected_pi}")
        
        if detected_pi == "Unknown":
            print("   ⚠️  No PI information found in text")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_pi}' or enter PI name: ").strip()
                
                if not choice:
                    return detected_pi
                
                if len(choice) >= 2:
                    print(f"   ✅ Selected: {choice}")
                    return choice
                else:
                    print("   ❌ Please enter a valid name (at least 2 characters)")
            except KeyboardInterrupt:
                print(f"\n   Using detected PI: {detected_pi}")
                return detected_pi
    
    def prompt_for_pathologist(self, detected_pathologist: str) -> str:
        """Prompt user for Pathologist if not detected"""
        print(f"\n🩺 Pathologist Detection:")
        print(f"   Detected: {detected_pathologist}")
        
        if detected_pathologist == "Unknown":
            print("   ⚠️  No pathologist information found in text")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_pathologist}' or enter pathologist name: ").strip()
                
                if not choice:
                    return detected_pathologist
                
                if len(choice) >= 2:
                    print(f"   ✅ Selected: {choice}")
                    return choice
                else:
                    print("   ❌ Please enter a valid name (at least 2 characters)")
            except KeyboardInterrupt:
                print(f"\n   Using detected pathologist: {detected_pathologist}")
                return detected_pathologist

    def detect_project_title(self, text: str) -> str:
        """Detect Project Title from text"""
        text_lower = text.lower()
        
        # Patterns to look for Project Title information
        title_patterns = [
            r'project title[:\-\s]*([^\n\r.;]*)',
            r'title[:\-\s]*([^\n\r.;]*)',
            r'project[:\-\s]*([^\n\r.;]*)',
            r'study title[:\-\s]*([^\n\r.;]*)',
            r'research title[:\-\s]*([^\n\r.;]*)',
            r'study[:\-\s]*([^\n\r.;]*)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                title = match.group(1).strip()
                # Clean up the title
                if len(title) > 10 and not any(word in title.lower() for word in ['is', 'was', 'will', 'the', 'and', 'or']):
                    return title[:100]  # Limit length
        
        # Try to create a descriptive title from key research terms
        research_terms = []
        
        # Look for cell types
        if "stem cell" in text_lower:
            research_terms.append("Stem Cell")
        if "lung" in text_lower:
            research_terms.append("Lung")
        if "at2" in text_lower:
            research_terms.append("AT2")
        if "cancer" in text_lower:
            research_terms.append("Cancer")
        if "tumor" in text_lower:
            research_terms.append("Tumor")
        if "brain" in text_lower:
            research_terms.append("Brain")
        if "heart" in text_lower:
            research_terms.append("Heart")
        
        # Look for research activities
        activities = []
        if "quantification" in text_lower:
            activities.append("Quantification")
        if "imaging" in text_lower:
            activities.append("Imaging")
        if "analysis" in text_lower:
            activities.append("Analysis")
        if "stain" in text_lower:
            activities.append("Staining")
        if "fluorescence" in text_lower:
            activities.append("Fluorescence")
        
        # Create a descriptive title
        if research_terms and activities:
            title = f"{' '.join(research_terms)} {' '.join(activities)} Study"
            return title
        elif research_terms:
            title = f"{' '.join(research_terms)} Research Study"
            return title
        elif activities:
            title = f"{' '.join(activities)} Research Project"
            return title
        
        # Try to extract meaningful phrases that could be project titles
        sentences = text.split('.')
        for sentence in sentences[:3]:  # Check first 3 sentences
            sentence = sentence.strip()
            if 10 < len(sentence) < 100 and any(keyword in sentence.lower() for keyword in ['study', 'research', 'analysis', 'investigation']):
                return sentence
        
        return "Unknown"
    
    def detect_request_purpose(self, text: str) -> str:
        """Detect Request Purpose from text"""
        text_lower = text.lower()
        
        # Patterns to look for Request Purpose information
        purpose_patterns = [
            r'purpose[:\-\s]*([^\n\r.;]*)',
            r'objective[:\-\s]*([^\n\r.;]*)',
            r'goal[:\-\s]*([^\n\r.;]*)',
            r'aim[:\-\s]*([^\n\r.;]*)',
            r'request purpose[:\-\s]*([^\n\r.;]*)',
            r'reason[:\-\s]*([^\n\r.;]*)'
        ]
        
        for pattern in purpose_patterns:
            match = re.search(pattern, text_lower)
            if match and match.group(1).strip():
                purpose = match.group(1).strip()
                if len(purpose) > 5:
                    return purpose[:200]  # Limit length
        
        # Look for common research purposes
        purpose_keywords = {
            "quantification": "Quantification and analysis",
            "imaging": "Imaging and visualization", 
            "analysis": "Data analysis",
            "measurement": "Measurement and assessment",
            "comparison": "Comparative analysis",
            "evaluation": "Evaluation and assessment"
        }
        
        for keyword, purpose in purpose_keywords.items():
            if keyword in text_lower:
                return purpose
        
        return "Unknown"
    
    def prompt_for_project_title(self, detected_title: str) -> str:
        """Prompt user for Project Title if not detected"""
        print(f"\n📋 Project Title Detection:")
        print(f"   Detected: {detected_title}")
        
        if detected_title == "Unknown":
            print("   ⚠️  No project title found in text")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_title}' or enter project title: ").strip()
                
                if not choice:
                    if detected_title != "Unknown":
                        return detected_title
                    else:
                        print("   ❌ Project title is mandatory. Please enter a title.")
                        continue
                
                if len(choice) >= 5:
                    print(f"   ✅ Selected: {choice}")
                    return choice
                else:
                    print("   ❌ Please enter a valid project title (at least 5 characters)")
            except KeyboardInterrupt:
                if detected_title != "Unknown":
                    print(f"\n   Using detected title: {detected_title}")
                    return detected_title
                else:
                    print("\n   ❌ Project title is mandatory!")
                    continue
    
    def prompt_for_request_purpose(self, detected_purpose: str) -> str:
        """Prompt user for Request Purpose if not detected"""
        print(f"\n🎯 Request Purpose Detection:")
        print(f"   Detected: {detected_purpose}")
        
        if detected_purpose == "Unknown":
            print("   ⚠️  No request purpose found in text")
        
        while True:
            try:
                choice = input(f"\nPress Enter to use '{detected_purpose}' or enter request purpose: ").strip()
                
                if not choice:
                    if detected_purpose != "Unknown":
                        return detected_purpose
                    else:
                        print("   ❌ Request purpose is mandatory. Please enter a purpose.")
                        continue
                
                if len(choice) >= 5:
                    print(f"   ✅ Selected: {choice}")
                    return choice
                else:
                    print("   ❌ Please enter a valid request purpose (at least 5 characters)")
            except KeyboardInterrupt:
                if detected_purpose != "Unknown":
                    print(f"\n   Using detected purpose: {detected_purpose}")
                    return detected_purpose
                else:
                    print("\n   ❌ Request purpose is mandatory!")
                    continue

def main():
    """Main function to handle command line usage"""
    
    print("🏥 Scanning Request Summarizer")
    print("=" * 50)
    
    summarizer = ScanningRequestSummarizer()
    
    # Check for input
    if len(sys.argv) > 1:
        # Read from file
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"📄 Reading from file: {filename}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
    else:
        # Read from stdin
        print("📝 Enter text to analyze (Ctrl+D to finish):")
        text = sys.stdin.read()
    
    # Determine output format
    output_format = "table"
    if "--json" in sys.argv:
        output_format = "json"
    
    # Process text
    result = summarizer.summarize_text(text, output_format)
    
    print("\n📊 SUMMARY RESULTS:")
    print("=" * 50)
    print(result)
    
    # Save to file if requested
    if "--save" in sys.argv:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"scanning_summary_{timestamp}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n💾 Results saved to: {output_file}")

if __name__ == "__main__":
    main() 