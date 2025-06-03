# Arm Learning Path Roadmap

Arm Learning Paths are maintained at: https://github.com/ArmDeveloperEcosystem/arm-learning-paths 

## Learning Path Project

There is a project which tracks the Todo, In Progress, and Published Learning Paths at https://github.com/orgs/ArmDeveloperEcosystem/projects/4 

## Learning Path Roadmap (Todo)

Put roadmap items for new Learning Paths on the project Todo list by creating an [issue in this repository](https://github.com/ArmDeveloperEcosystem/roadmap/issues) with the title of the proposed Learning Path and a short summary of the concept.

## Learning Path Reports

Use the Python script `tools/generate-monthly-report.py` to generate reports of the current Todo items and the published Learning Paths.

You need a GitHub Token to be able to read the Learning Path project data.

```console
export GITHUB_TOKEN=<YOUR_GithubPersonalAccessToken_HERE>
```

Here are the steps to generate a report.

Create a Python virtual environment:

```console
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```console
pip3 install -r tools/requirements.txt
```

Create report for the current month:

```console
python3 tools/generate-monthly-report.py
```

Create report for a month:

```console
python3 tools/generate-monthly-report.py --month 2025-04
```

Create a report for a range of months:

```console
python3 tools/generate-monthly-report.py --month-range 2025-03 2025-04
```

The report is generated in the `reports/` directory.

## Learning Path Content Count 

The total number of Learning Path contents over time is tracked using the scripts `tools/count-content.py` and `tools/plot-content-counts.py`.

- **`tools/count-content.py`**: This script counts the number of unique Learning Paths, shared Learning Paths, drafts, and Install Guides in the repository. It generates a Markdown summary report (e.g., `content_summary_MM-DD-YYYY.md`) in the `reports/content-count/` directory. You can run it directly from the root of a checked-out Learning Paths repository:

  ```console
  python3 tools/count-content.py
  ```
  
  The script will output a summary to the console and write a detailed report to `content_summary.md`.

- **`count-content.sh`**: This shell script automates running `count-content.py` for a specific date (to analyze the repository at a point in time). It clones or updates the Learning Paths repository, sets up a Python environment, and runs the content count script. The resulting report is saved in `reports/content-count/` with a date-stamped filename:

  ```console
  ./count-content.sh MM-DD-YYYY
  ```
  
  If no date is provided, it uses the current date.

- **`tools/plot-content-counts.py`**: This script reads all the date-stamped summary reports in `reports/content-count/` and generates a plot (`content_over_time.png`) showing the growth of Install Guides, unique Learning Paths, and total published content over time. Run it as follows:

  ```console
  python3 tools/plot-content-counts.py
  ```

The generated plot can be found at `reports/content-count/content_over_time.png`.

These tools help track the evolution of Learning Path content and visualize growth trends over time.

## Hugging Face Learning Paths

To list all Learning Paths that use the "Hugging Face" tag, use the script `tools/count-huggingface-lps.py`. This script clones the main branch of the Arm Learning Paths repository, scans all `_index.md` files for the "Hugging Face" tag in the `tools_software_languages` section, and generates a markdown table with the Learning Path title, category, and a direct link.

**How to run:**

First, ensure your Python environment is set up and dependencies are installed:

```console
python3 -m venv venv
source venv/bin/activate
pip install -r tools/requirements.txt
```

Then run the script:

```console
python3 tools/count-huggingface-lps.py
```

**Output:**

The results will be written to:

```
reports/hugging-face/huggingface-learning-paths.md
```

This file contains a table listing all Learning Paths with the "Hugging Face" tag, including their category and a direct link to each Learning Path on learn.arm.com.