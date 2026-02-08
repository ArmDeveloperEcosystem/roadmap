# Running Monthly Reports for April - December 2025

This document explains how to generate the monthly Learning Path reports for months April 2025 through December 2025.

## Option 1: Using the trigger script (Recommended)

A script has been created to automate the triggering of all 9 workflow runs.

### Prerequisites
- GitHub CLI (`gh`) must be installed
- You must be authenticated with `gh auth login`

### Usage

```bash
./trigger-monthly-reports.sh
```

This will trigger the "Generate Monthly Learning Path Report" workflow 9 times with the following month inputs:
- 2025-04 (April 2025)
- 2025-05 (May 2025)
- 2025-06 (June 2025)
- 2025-07 (July 2025)
- 2025-08 (August 2025)
- 2025-09 (September 2025)
- 2025-10 (October 2025)
- 2025-11 (November 2025)
- 2025-12 (December 2025)

## Option 2: Manual workflow dispatch via GitHub UI

1. Go to https://github.com/ArmDeveloperEcosystem/roadmap/actions/workflows/update-roadmap-project-dates.yml
2. Click the "Run workflow" button
3. Enter the month in YYYY-MM format (e.g., `2025-04`)
4. Click "Run workflow"
5. Repeat steps 2-4 for each of the 9 months

## Option 3: Using GitHub CLI manually

Run each command individually:

```bash
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-04" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-05" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-06" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-07" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-08" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-09" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-10" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-11" --repo ArmDeveloperEcosystem/roadmap
gh workflow run "Generate Monthly Learning Path Report" --ref main --field month="2025-12" --repo ArmDeveloperEcosystem/roadmap
```

## Expected Results

After all 9 workflow runs complete successfully, the following report files should be updated in the `reports/` directory:

- `reports/LP-report-2025-04.md`
- `reports/LP-report-2025-05.md`
- `reports/LP-report-2025-06.md`
- `reports/LP-report-2025-07.md`
- `reports/LP-report-2025-08.md`
- `reports/LP-report-2025-09.md`
- `reports/LP-report-2025-10.md`
- `reports/LP-report-2025-11.md`
- `reports/LP-report-2025-12.md`

## Monitoring Progress

You can monitor the progress of all workflow runs at:
https://github.com/ArmDeveloperEcosystem/roadmap/actions
