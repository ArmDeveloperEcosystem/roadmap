#!/bin/bash

# Script to trigger the "Generate Monthly Learning Path Report" workflow
# for months April 2025 through December 2025

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

# Array of months to process
months=("2025-04" "2025-05" "2025-06" "2025-07" "2025-08" "2025-09" "2025-10" "2025-11" "2025-12")

echo "Triggering workflow runs for 9 months (April 2025 - December 2025)..."
echo ""

# Loop through each month and trigger the workflow
for month in "${months[@]}"; do
    echo "Triggering workflow for month: $month"
    
    # Trigger the workflow with the month input
    gh workflow run "Generate Monthly Learning Path Report" \
        --ref main \
        --field month="$month" \
        --repo ArmDeveloperEcosystem/roadmap
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully triggered workflow for $month"
    else
        echo "✗ Failed to trigger workflow for $month"
    fi
    
    # Small delay to avoid rate limiting
    sleep 2
    echo ""
done

echo "All workflow runs have been triggered!"
echo "You can monitor the progress at: https://github.com/ArmDeveloperEcosystem/roadmap/actions"
