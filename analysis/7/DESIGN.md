# Comprehensive NDJSON Content Extractor for Neo4j Intelligence Loading

## Problem / Metric

Current LanceDB export captures only 67.8% of available sessions, missing critical investigative intelligence that exists in the sessions.ndjson source file. Investigation revealed 26MB of extractable content across 10,502 sessions including:
- 8,301 phone call transcripts (40.9% of telephony)
- 1,380 social media posts (20.5% of social network) 
- 805 document files (98.7% of generic files)
- 14 complete intelligence reports (100% of intel reports)

**Current State**: Partial content extraction, missing investigative intelligence
**Target State**: Complete content extraction for comprehensive Neo4j graph loading

## Goal

Create a comprehensive NDJSON parser that extracts ALL textual content from sessions.ndjson for Neo4j loading, plus enhanced diagnostic tools that provide "X-ray vision" into available intelligence content.

## Scope (M/S/W)

### Must Have [M]
- [M] Comprehensive content extractor reading ALL text fields from sessions.ndjson
- [M] Support for `fulltext[]` arrays (Social Network, Intel Reports, Collection Report,...)
- [M] Support for `documents[].text` fields (Entity Reports, Generic Files, Social Network,...)
- [M] Support for `previewcontent` fields (potentially base64 encoded content)
- [M] Neo4j-ready JSON export with content + metadata + relationships
- [M] **Property naming consistency**: Use CamelCase matching existing Neo4j schema (e.g. use `contentType`, `sessionGuid`, `caseName` instead of snake_case (e.g. `content_type`, `session_guid`, `case_name`)
- [M] Enhanced diagnostic scripts showing content availability "X-ray"
- [M] Session type coverage statistics and content field mapping

### Should Have [S]
- [S] Enrichment data extraction from `enrichment_` fields (speech-to-text, etc.)
- [S] Base64 content decoding for `previewcontent` fields
- [S] Content quality scoring and validation
- [S] Parallel processing for large datasets
- [S] Export format optimization for Neo4j ingestion

### Won't Do [W]
- [W] Vector embedding generation (LanceDB's job)
- [W] Content translation or language processing
- [W] Real-time processing or streaming
- [W] Complex content transformation beyond extraction

## Acceptance Criteria

| # | Given | When | Then |
|---|-------|------|------|
| 1 | Gantry sessions.ndjson with 99,821 sessions | Runs comprehensive extractor | Extracts 78,284+ sessions (78.4% coverage) |
| 2 | Session with `fulltext[]` content | Processes social media/intel reports | Extracts readable text content for Neo4j |
| 3 | Session with `documents[].text` content | Processes entity reports/files | Extracts document text for graph loading |
| 4 | Investigator runs diagnostic script | Views content availability | Gets "X-ray" showing what intelligence exists per session type |
| 5 | Enhanced export for Neo4j | Loads into graph database | All content + metadata + relationships available for queries |
| 6 | Phone call with transcript in enrichment | Processes telephony session | Extracts speech-to-text content if available |
| 7 | Export JSON with mixed property naming | Validates against Neo4j schema | All properties use CamelCase (`contentType`, `sessionGuid`, `caseName`, `extractionConfidence`) |

## Technical Design

### Content Extraction Strategy

```python
def extract_all_content(session):
    """Extract all possible textual content from session"""
    content_sources = []
    
    # Primary content fields
    if 'fulltext' in session:
        content_sources.extend(extract_fulltext_array(session['fulltext']))
    
    if 'documents' in session:
        content_sources.extend(extract_documents_text(session['documents']))
    
    if 'previewcontent' in session:
        content_sources.append(decode_preview_content(session['previewcontent']))
    
    # Enrichment data (speech-to-text, etc.)
    if 'enrichment_' in session:
        content_sources.extend(extract_enrichment_content(session['enrichment_']))
    
    return combine_content_sources(content_sources)
```

### Session Type Content Mapping

| Session Type | Primary Fields | Secondary Fields | Expected Recovery |
|--------------|----------------|------------------|-------------------|
| **Messaging** | `fulltext[]` | `documents[].text` | 94.8% (64,156 sessions) |
| **Telephony** | `enrichment_.jsi-speech-to-text` | `documents[].text` | 40.9% (8,301 sessions) |
| **Social Network** | `fulltext[]` | `documents[].text` | 20.5% (1,380 sessions) |
| **Entity Report** | `documents[].text` | `enrichment_` | ~0.1% (1 session) |
| **Generic File** | `documents[].text` | `previewcontent` | 98.7% (805 sessions) |
| **Intel Report** | `fulltext[]` | `documents[].text` | 100% (14 sessions) |
| **Collection Report** | `fulltext[]` | `documents[].text` | 100% (1 session) |

### Enhanced Diagnostic Scripts

**Content X-Ray Script (`content_xray.py`)**:
```bash
python content_xray.py --case-dir ./data/gantry
```

**Output Format**:
```
🔍 CONTENT X-RAY: GANTRY INVESTIGATION
======================================================
📊 Total Sessions: 99,821

📱 MESSAGING (67,656 sessions)
   📝 fulltext[]: 64,156 sessions (94.8%) - 165.80 MB
   📄 documents[].text: 12,450 sessions (18.4%) - 23.12 MB
   🎯 Extractable: 64,156 sessions, 165.80 MB content

📞 TELEPHONY (20,310 sessions)  
   🗣️ enrichment_.jsi-speech-to-text: 8,301 sessions (40.9%) - 12.86 MB
   📄 documents[].text: 145 sessions (0.7%) - 0.45 MB
   🎯 Extractable: 8,301 sessions, 12.86 MB content

📲 SOCIAL NETWORK (6,732 sessions)
   📝 fulltext[]: 1,380 sessions (20.5%) - 10.45 MB
   📄 documents[].text: 1,380 sessions (20.5%) - 2.15 MB
   🎯 Extractable: 1,380 sessions, 10.45 MB content

🔍 INTEL REPORT (14 sessions)
   📝 fulltext[]: 14 sessions (100%) - 0.02 MB
   📄 Police incident reports, officer details, locations
   🎯 Extractable: 14 sessions, 0.02 MB content

===============================================
🎯 TOTAL EXTRACTABLE: 78,284 sessions (78.4%)
📊 TOTAL CONTENT: 189.13 MB
⚡ IMPROVEMENT: +10,501 sessions vs current LanceDB
```

### Neo4j Export Format

**Enhanced JSON Structure**:
```json
{
  "sessionId": "c122cd6e-5bb2-77d5-cffa-6de472...",
  "metadata": {
    "sessionType": "Messaging",
    "timestamp": "2023-03-07T11:57:50Z",
    "caseName": "Operation Gantry",
    "classification": "CONFIDENTIAL"
  },
  "content": {
    "primaryText": "Combined fulltext content...",
    "documents": [
      {"contentType": "transcript", "text": "Document content..."},
      {"contentType": "attachment", "text": "File content..."}
    ],
    "enrichment": {
      "speechToText": "Transcribed audio...",
      "languageDetection": "English"
    }
  },
  "relationships": {
    "participants": [
      {"person": "Omar Fisher", "role": "sender", "msisdn": "+1..."},
      {"person": "Sarah Chen", "role": "recipient", "msisdn": "+1..."}
    ],
    "locations": [
      {"latitude": 40.7128, "longitude": -74.0060, "source": "gps"}
    ]
  },
  "intelligenceSummary": {
    "contentLength": 2847,
    "keywordDensity": {"meeting": 3, "urgent": 1, "cash": 2},
    "suspiciousIndicators": ["cash", "usual place"],
    "extractionConfidence": 0.95
  }
}
```

### Implementation Strategy

**Phase 1: Core Content Extraction (Weekend)**
- Build comprehensive content extractor for all NDJSON fields
- Create enhanced diagnostic X-ray script
- Test extraction on gantry dataset
- Validate content quality and coverage improvements

**Phase 2: Neo4j Export Enhancement**
- Design Neo4j-optimized JSON export format
- Add relationship extraction (participants, locations, etc.)
- Implement intelligence summary generation
- Add content validation and quality scoring

**Phase 3: Production Optimization**
- Add parallel processing for large datasets
- Implement base64 decoding for preview content
- Add enrichment data processing
- Performance optimization for 100K+ sessions

### Success Metrics

**Content Recovery Targets**:
- Extract 78,284+ sessions (vs current 67,783)
- Recover 26+ MB of investigative content
- Achieve 78.4%+ session coverage (vs current 67.8%)
- Process 100K+ sessions in <5 minutes

**Intelligence Quality Targets**:
- 8,301 phone call transcripts recovered
- 1,380 social media posts/videos recovered
- 14 complete police intelligence reports recovered
- 805 document files with content recovered

**Investigator Experience Targets**:
- "X-ray vision" into available content per case
- One-command extraction for any case directory
- Neo4j-ready exports for immediate graph loading
- Clear content availability statistics

---
*Comprehensive intelligence extraction from existing data sources*