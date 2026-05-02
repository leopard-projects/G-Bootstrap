#!/bin/bash

# =============================================================================

# mythos-scan.sh — AI-Powered Security Scanner (Opus 4)

# Simulates Mythos-class vulnerability discovery for Spring Boot + Python stacks

# Author: Based on Claude Mythos research preview findings

# Usage: ./mythos-scan.sh [options]

# =============================================================================

set -euo pipefail

# ─── CONFIG ──────────────────────────────────────────────────────────────────

MODEL=“claude-opus-4-5”
OUTPUT_DIR=”./security-reports”
TIMESTAMP=$(date +”%Y%m%d_%H%M%S”)
REPORT_FILE=”$OUTPUT_DIR/scan_$TIMESTAMP.md”
SEVERITY_FILTER=“CRITICAL|HIGH”  # Change to “CRITICAL|HIGH|MEDIUM” for more findings

# Colors

RED=’\033[0;31m’
YELLOW=’\033[1;33m’
GREEN=’\033[0;32m’
BLUE=’\033[0;34m’
NC=’\033[0m’

# ─── PROMPTS ─────────────────────────────────────────────────────────────────

JAVA_PROMPT=’
You are a senior security researcher writing a formal CVE report.
Analyze this Java/Spring Boot code with an attacker mindset.

FIND THESE VULNERABILITY CLASSES ONLY:

1. IDOR (Insecure Direct Object Reference)
- Any repo.findById() without owner/userId scoping
- Missing @PreAuthorize or ownership check before returning data
- Controller accepting IDs without validating caller owns the resource
1. Authentication Bypass
- JWT validated at gateway but not re-checked at service level
- @PermitAll or missing @Secured on sensitive endpoints
- Trust assumptions on internal service calls without re-validation
1. Taint Flow / Injection
- User input reaching @Query, native SQL, or Kafka producer unsanitized
- String concatenation in queries
- Missing @Valid or input sanitization on @RequestBody/@RequestParam
1. TOCTOU (Time-of-Check-Time-of-Use)
- Balance/limit check followed by async gap before debit/credit
- Non-atomic read-modify-write on financial state
- Missing @Transactional on multi-step financial operations
1. Kafka Security Gaps
- @KafkaListener consuming messages without signature/HMAC verification
- Payload used directly in business logic without validation
- No dead-letter-queue poisoning protection
1. Business Logic Flaws
- Correct code that produces wrong financial behavior under edge cases
- Missing idempotency keys on payment operations
- Race conditions in reconciliation logic
1. Audit Logging Gaps
- Financial state changes without structured audit trail
- Missing correlation IDs on Kafka → DB flows

## FORMAT EACH FINDING EXACTLY LIKE THIS:

## SEVERITY: [CRITICAL|HIGH]
CLASS: [vulnerability class]
FILE: [filename]
LINE: [line number or range]
DESCRIPTION: [what the vulnerability is]
EXPLOIT: [how an attacker abuses it - be specific]
FIX: [exact code fix]

Output CRITICAL and HIGH severity only. If no issues found, say “NO HIGH/CRITICAL FINDINGS”.
’

PYTHON_PROMPT=’
You are a senior security researcher writing a formal CVE report.
Analyze this Python/FastAPI code with an attacker mindset.

FIND THESE VULNERABILITY CLASSES ONLY:

1. IDOR
- DB queries fetching by ID without user ownership scoping
- Missing dependency injection for current_user validation
- Route params used directly in queries without authorization check
1. Authentication/Authorization Gaps
- Missing Depends(get_current_user) on sensitive routes
- JWT decoded but claims not validated for resource ownership
- Admin-only operations missing role check
1. Injection / Taint Flow
- f-strings or % formatting in SQL queries
- User input reaching subprocess, eval, or exec
- Missing Pydantic validation on request models
- Unvalidated query params reaching ORM
1. Async Race Conditions
- Non-atomic financial operations in async handlers
- Missing database transaction context on multi-step operations
- Fire-and-forget patterns on state-mutating operations
1. Prompt Injection (for AI/agentic code)
- User input concatenated directly into LLM prompts
- Missing sanitization before Bedrock/Claude API calls
- Agent tool results trusted without validation
1. ServiceNow / Agentic Gaps
- Ticket data used in routing decisions without sanitization
- Missing severity classification validation
- Agent actions not logged for audit trail
1. FastAPI Specific
- Background tasks mutating shared state without locks
- Missing rate limiting on expensive endpoints
- Unhandled exceptions exposing stack traces

## FORMAT EACH FINDING EXACTLY LIKE THIS:

## SEVERITY: [CRITICAL|HIGH]
CLASS: [vulnerability class]
FILE: [filename]
LINE: [line number or range]
DESCRIPTION: [what the vulnerability is]
EXPLOIT: [how an attacker abuses it - be specific]
FIX: [exact code fix]

Output CRITICAL and HIGH severity only. If no issues found, say “NO HIGH/CRITICAL FINDINGS”.
’

CROSSFILE_PROMPT=’
You are a senior security researcher performing cross-component taint analysis.
These files work together as a system. Analyze the DATA FLOW between them.

FOCUS ON:

1. Cross-File Taint Flow
- Trace user input from entry point (Controller/Route) through Service → Repository → DB
- Identify where sanitization/validation is MISSING in the chain
- Flag if input validated in one layer but bypassed in another
1. Trust Boundary Violations
- Data crossing from untrusted (external) to trusted (internal) without validation
- Kafka message → Service → DB flow without ownership re-validation
- API Gateway → Microservice → DB without re-checking auth claims
1. Broken Auth Chain
- Auth checked at Layer A but assumption of auth at Layer B
- Service A trusts Service B without verifying identity
- JWT claims extracted but specific claim (userId, accountId) not validated downstream
1. Reconciliation/Parallel Run Gaps
- Legacy vs new service producing different results silently
- Missing integrity check on reconciled records
- Translation layer introducing data corruption edge cases
1. Inter-Service Communication
- HTTP calls between services without mTLS or service tokens
- Shared DB tables accessed by multiple services without row-level security

## FORMAT EACH FINDING:

## SEVERITY: [CRITICAL|HIGH]
CLASS: [vulnerability class]
ENTRY_POINT: [where tainted data enters]
SINK: [where it causes harm]
FLOW: [step by step data path]
EXPLOIT: [attacker scenario]
FIX: [remediation]

’

# ─── FUNCTIONS ────────────────────────────────────────────────────────────────

print_banner() {
echo -e “${BLUE}”
echo “╔═══════════════════════════════════════════════════╗”
echo “║         MYTHOS-SCAN — AI Security Scanner         ║”
echo “║      Powered by Claude Opus 4 (Attacker Mode)     ║”
echo “╚═══════════════════════════════════════════════════╝”
echo -e “${NC}”
}

print_usage() {
echo “Usage: $0 [OPTIONS]”
echo “”
echo “Options:”
echo “  -f, –file FILE        Scan a single file”
echo “  -d, –dir DIR          Scan all files in directory”
echo “  -x, –cross DIR        Cross-file taint analysis on directory”
echo “  -p, –project          Full project scan (Java + Python)”
echo “  -h, –help             Show this help”
echo “”
echo “Examples:”
echo “  $0 –file src/ReconciliationService.java”
echo “  $0 –dir src/main/java/payments/”
echo “  $0 –cross src/main/java/kafka/”
echo “  $0 –project”
}

init_report() {
mkdir -p “$OUTPUT_DIR”
cat > “$REPORT_FILE” << EOF

# Security Scan Report

**Date:** $(date)
**Model:** $MODEL
**Scanner:** mythos-scan.sh

-----

EOF
echo -e “${GREEN}Report: $REPORT_FILE${NC}”
}

scan_file() {
local FILE=$1
local PROMPT=$2
local LABEL=$3

```
echo -e "${YELLOW}Scanning: $FILE${NC}"

if [ ! -f "$FILE" ]; then
    echo -e "${RED}File not found: $FILE${NC}"
    return 1
fi

# Add to report
echo "## $LABEL: \`$FILE\`" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Run Claude Opus scan
RESULT=$(cat "$FILE" | claude --model "$MODEL" "$PROMPT" 2>/dev/null || echo "SCAN_ERROR")

if [ "$RESULT" = "SCAN_ERROR" ]; then
    echo -e "${RED}Error scanning $FILE${NC}"
    echo "❌ Scan error" >> "$REPORT_FILE"
elif echo "$RESULT" | grep -qE "$SEVERITY_FILTER"; then
    echo -e "${RED}⚠ FINDINGS in $FILE${NC}"
    echo "$RESULT" >> "$REPORT_FILE"
else
    echo -e "${GREEN}✓ No high/critical findings${NC}"
    echo "✅ No HIGH/CRITICAL findings." >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
```

}

scan_directory() {
local DIR=$1
local LANG=$2

```
echo -e "${BLUE}Scanning directory: $DIR (${LANG})${NC}"

if [ ! -d "$DIR" ]; then
    echo -e "${RED}Directory not found: $DIR${NC}"
    return 1
fi

if [ "$LANG" = "java" ]; then
    PROMPT=$JAVA_PROMPT
    EXT="*.java"
else
    PROMPT=$PYTHON_PROMPT
    EXT="*.py"
fi

find "$DIR" -name "$EXT" | while read -r FILE; do
    scan_file "$FILE" "$PROMPT" "$LANG scan"
    sleep 2  # Rate limiting between files
done
```

}

cross_file_scan() {
local DIR=$1

```
echo -e "${BLUE}Cross-file taint analysis: $DIR${NC}"

if [ ! -d "$DIR" ]; then
    echo -e "${RED}Directory not found: $DIR${NC}"
    return 1
fi

echo "## Cross-File Taint Analysis: \`$DIR\`" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Bundle all files in directory for cross-file analysis
BUNDLED=$(find "$DIR" -name "*.java" -o -name "*.py" | head -10 | xargs cat 2>/dev/null)

if [ -z "$BUNDLED" ]; then
    echo -e "${RED}No Java or Python files found in $DIR${NC}"
    return 1
fi

echo -e "${YELLOW}Running cross-file taint analysis...${NC}"
RESULT=$(echo "$BUNDLED" | claude --model "$MODEL" "$CROSSFILE_PROMPT" 2>/dev/null || echo "SCAN_ERROR")

echo "$RESULT" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"

if echo "$RESULT" | grep -qE "$SEVERITY_FILTER"; then
    echo -e "${RED}⚠ CROSS-FILE FINDINGS DETECTED${NC}"
else
    echo -e "${GREEN}✓ No cross-file high/critical findings${NC}"
fi
```

}

full_project_scan() {
echo -e “${BLUE}Running full project scan…${NC}”

```
# Highest risk Java directories
JAVA_DIRS=(
    "src/main/java"
    "src/main/kotlin"
)

# Highest risk Python directories
PYTHON_DIRS=(
    "src"
    "app"
    "api"
    "services"
)

echo "## Full Project Scan" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Scan Java
for DIR in "${JAVA_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        # Prioritize high-risk modules
        for MODULE in reconciliation payment kafka consumer auth transaction; do
            FOUND=$(find "$DIR" -type d -iname "*${MODULE}*" 2>/dev/null | head -1)
            if [ -n "$FOUND" ]; then
                echo -e "${YELLOW}Priority module: $FOUND${NC}"
                scan_directory "$FOUND" "java"
            fi
        done
    fi
done

# Scan Python
for DIR in "${PYTHON_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        scan_directory "$DIR" "python"
    fi
done

# Cross-file analysis on kafka/payment modules
for MODULE in kafka payment reconciliation; do
    FOUND=$(find . -type d -iname "*${MODULE}*" 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        cross_file_scan "$FOUND"
    fi
done
```

}

print_summary() {
echo “”
echo -e “${BLUE}═══════════════════════════════════${NC}”
echo -e “${BLUE}           SCAN COMPLETE            ${NC}”
echo -e “${BLUE}═══════════════════════════════════${NC}”

```
CRITICAL_COUNT=$(grep -c "SEVERITY: CRITICAL" "$REPORT_FILE" 2>/dev/null || echo 0)
HIGH_COUNT=$(grep -c "SEVERITY: HIGH" "$REPORT_FILE" 2>/dev/null || echo 0)

echo -e "${RED}CRITICAL: $CRITICAL_COUNT${NC}"
echo -e "${YELLOW}HIGH:     $HIGH_COUNT${NC}"
echo ""
echo -e "Full report: ${GREEN}$REPORT_FILE${NC}"
echo ""

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo -e "${RED}⚠ ACTION REQUIRED: Critical vulnerabilities found.${NC}"
    echo "Fix before next deployment."
elif [ "$HIGH_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ High severity findings. Schedule fixes this sprint.${NC}"
else
    echo -e "${GREEN}✓ No critical/high findings in scanned files.${NC}"
fi
```

}

# ─── MAIN ────────────────────────────────────────────────────────────────────

print_banner
init_report

if [ $# -eq 0 ]; then
print_usage
exit 0
fi

case “$1” in
-f|–file)
FILE=$2
# Detect language from extension
if [[ “$FILE” == *.java ]]; then
scan_file “$FILE” “$JAVA_PROMPT” “Java Security Scan”
elif [[ “$FILE” == *.py ]]; then
scan_file “$FILE” “$PYTHON_PROMPT” “Python Security Scan”
else
echo -e “${RED}Unsupported file type. Use .java or .py${NC}”
exit 1
fi
;;
-d|–dir)
DIR=$2
LANG=${3:-“java”}  # default java
scan_directory “$DIR” “$LANG”
;;
-x|–cross)
cross_file_scan “$2”
;;
-p|–project)
full_project_scan
;;
-h|–help)
print_usage
exit 0
;;
*)
echo -e “${RED}Unknown option: $1${NC}”
print_usage
exit 1
;;
esac

print_summary