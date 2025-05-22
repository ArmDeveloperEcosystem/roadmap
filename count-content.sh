#!/bin/bash
set -e

REPO_URL="https://github.com/ArmDeveloperEcosystem/arm-learning-paths.git"
REPO_DIR="arm-learning-paths"
REPORTS_DIR="reports/content-count"

# Parse optional date argument
if [ $# -ge 1 ]; then
    INPUT_DATE="$1"
    # Convert MM-DD-YYYY to YYYY-MM-DD for git (cross-platform)
    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        GIT_DATE="$(date -d "$INPUT_DATE" +"%Y-%m-%d")"
    else
        # BSD date (macOS)
        GIT_DATE="$(date -j -f "%m-%d-%Y" "$INPUT_DATE" +"%Y-%m-%d")"
    fi
    DATE_STAMP="$INPUT_DATE"
else
    # Default to today's date if not provided
    DATE_STAMP=$(date +"%m-%-d-%Y")
    GIT_DATE=""
fi

# Clone or update the repository
if [ -d "$REPO_DIR" ]; then
    echo "Repository already exists. Pulling latest changes..."
    git -C "$REPO_DIR" fetch
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
fi

# If a date was provided, checkout the repo as it was on that date
if [ -n "$GIT_DATE" ]; then
    echo "Checking out repository as of $GIT_DATE..."
    cd "$REPO_DIR"
    # Detect default branch (main or master)
    if git show-ref --verify --quiet refs/heads/main; then
        DEFAULT_BRANCH="main"
    else
        DEFAULT_BRANCH="master"
    fi
    # Find the latest commit on or before the date
    COMMIT_HASH=$(git rev-list -1 --before="$GIT_DATE 23:59:59" "$DEFAULT_BRANCH")
    if [ -z "$COMMIT_HASH" ]; then
        echo "No commit found on or before $GIT_DATE"
        exit 1
    fi
    git checkout "$COMMIT_HASH"
    cd ..
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install Python requirements
pip install --upgrade pip
pip install -r tools/requirements.txt

# Copy count-content.py if missing in the checked-out repo
if [ ! -f "$REPO_DIR/tools/count-content.py" ]; then
    echo "tools/count-content.py not found in checked-out repo. Copying from local tools/ directory..."
    cp tools/count-content.py "$REPO_DIR/tools/count-content.py"
fi

# Run the Python script to generate the report
echo "Running content count script..."
(cd "$REPO_DIR" && python3 tools/count-content.py)

# Ensure the reports directory exists
mkdir -p "$REPORTS_DIR"

# Copy the generated report with date stamp
cp "$REPO_DIR/content_summary.md" "$REPORTS_DIR/content_summary_${DATE_STAMP}.md"

echo "Report copied to $REPORTS_DIR/content_summary_${DATE_STAMP}.md"
