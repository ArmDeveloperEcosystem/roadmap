# Arm Learning Paths Roadmap

Arm Learning Paths are maintained at: https://github.com/ArmDeveloperEcosystem/arm-learning-paths 

## Learning Paths project

There is a project which tracks the Todo, In Progress, and Published Learning Paths at https://github.com/orgs/ArmDeveloperEcosystem/projects/4 

## Learning Paths roadmap (Todo)

Put roadmap items for new Learning Paths on the project Todo list by creating an [issue in this repository](https://github.com/ArmDeveloperEcosystem/roadmap/issues) with the title of the proposed Learning Path and some information in the description about it. 

## Learning Path reports

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