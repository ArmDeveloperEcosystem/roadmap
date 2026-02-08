import requests
import datetime
import json
from bs4 import BeautifulSoup
import contextlib
import argparse
import sys
import os  # Add os import for directory handling

# GitHub API settings
GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("PAT")
if not GITHUB_TOKEN:
    # Fallback for GitHub Actions: use secrets.PAT if available
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub project board settings
ORGANIZATION = "ArmDeveloperEcosystem"
PROJECT_NUMBER = 4

# Update the GraphQL query to handle all possible types of ProjectV2ItemFieldValue and support pagination
GRAPHQL_QUERY = """
query ($org: String!, $projectNumber: Int!, $cursor: String) {
  organization(login: $org) {
    projectV2(number: $projectNumber) {
      title
      items(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          content {
            ... on Issue {
              title
              url
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
            ... on PullRequest {
              title
              url
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2SingleSelectField { name }
                }
                name
              }
              ... on ProjectV2ItemFieldTextValue {
                field {
                  ... on ProjectV2FieldCommon { name }
                }
                text
              }
              ... on ProjectV2ItemFieldNumberValue {
                field {
                  ... on ProjectV2FieldCommon { name }
                }
                number
              }
              ... on ProjectV2ItemFieldDateValue {
                field {
                  ... on ProjectV2FieldCommon { name }
                }
                date
              }
            }
          }
        }
      }
    }
  }
}
"""

def run_graphql_query(query, variables):
    """
    Executes a GraphQL query against the GitHub API.
    """
    if not GITHUB_TOKEN:
        raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        GITHUB_API_URL,
        json={"query": query, "variables": variables},
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
    
    if "errors" in response.json():
        raise Exception(f"GraphQL query returned errors: {response.json()['errors']}")
    
    return response.json()

# Add a function to fetch items in the Done column with pagination
def fetch_done_items(month_filter=None, month_range=None):
    done_items = []
    has_next_page = True
    cursor = None
    processed_count = 0

    def in_month_range(publish_date):
        if not publish_date or not month_range:
            return False
        try:
            pub_dt = datetime.datetime.strptime(publish_date, "%Y-%m-%d")
            return month_range[0] <= pub_dt <= month_range[1]
        except Exception:
            return False

    # Use pagination to get all items
    while has_next_page:
        variables = {
            "org": ORGANIZATION,
            "projectNumber": PROJECT_NUMBER,
            "cursor": cursor
        }
        
        data = run_graphql_query(GRAPHQL_QUERY, variables)
        project = data["data"]["organization"]["projectV2"]
        page_info = project["items"]["pageInfo"]
        
        for item in project["items"]["nodes"]:
            processed_count += 1
            published_url = None
            start_date = None
            publish_date = None
            acm_label = False
            cca_label = False
            sme_label = False
            
            # Check for ACM, CCA and SME labels in content labels
            content = item.get("content", {})
            labels = []
            if content and "labels" in content and content["labels"] and "nodes" in content["labels"]:
                labels = [label["name"] for label in content["labels"]["nodes"] if "name" in label]
                if "ACM" in labels:
                    acm_label = True
                if "CCA" in labels:
                    cca_label = True
                if "SME" in labels:
                    sme_label = True
                    
            # Check for ACM label in each node's fieldValues
            for field in item["fieldValues"]["nodes"]:
                if (
                    "field" in field and field["field"]
                    and field["field"].get("name") == "Status"
                    and (field.get("name") in ["Done", "Maintenance"] or field.get("value") in ["Done", "Maintenance"])
                ):
                    # Find the Published URL, Start Date, Publish Date, and ACM fields
                    for f in item["fieldValues"]["nodes"]:
                        if (
                            "field" in f and f["field"]
                            and f["field"].get("name") == "Published URL"
                            and f.get("text")
                        ):
                            published_url = f["text"]
                        if (
                            "field" in f and f["field"]
                            and f["field"].get("name") == "Start Date"
                            and f.get("date")
                        ):
                            start_date = f["date"]
                        if (
                            "field" in f and f["field"]
                            and f["field"].get("name") == "Publish Date"
                            and f.get("date")
                        ):
                            publish_date = f["date"]
                    # Filter by month or month_range if set
                    if month_range:
                        if not in_month_range(publish_date):
                            continue
                    elif month_filter:
                        if not publish_date or not publish_date.startswith(month_filter):
                            continue
                    done_items.append({
                        "title": item["content"]["title"],
                        "published_url": published_url,
                        "start_date": start_date,
                        "publish_date": publish_date,
                        "acm_label": acm_label,
                        "cca_label": cca_label,
                        "sme_label": sme_label,
                        "content": item.get("content", {})
                    })
        
        # Update cursor for pagination
        has_next_page = page_info["hasNextPage"]
        if has_next_page:
            cursor = page_info["endCursor"]
            print(f"Fetched {processed_count} items, continuing to next page...", file=sys.stderr)

    print(f"Total items processed: {processed_count}", file=sys.stderr)
    return done_items

# Update the generate_report function to print Done items
def generate_report(month_filter=None, month_range=None):
    # We'll fetch data directly through fetch_done_items which handles pagination

    # Generate the report
    if month_range:
        report_date = f"{month_range[0].strftime('%B %Y')} - {month_range[1].strftime('%B %Y')}"
    elif month_filter:
        report_month = datetime.datetime.strptime(month_filter, "%Y-%m")
        report_date = report_month.strftime("%B %Y")
    else:
        today = datetime.date.today()
        report_date = today.strftime("%B %Y")
        month_filter = today.strftime("%Y-%m")

    print(f"## Learning Path Report for {report_date}\n")

 
    # Fetch and print Done items for the given month or range
    done_items = fetch_done_items(month_filter=month_filter, month_range=month_range)
    # Sort done_items by publish_date (ascending), handling None as last
    def sort_key(item):
        pd = item.get('publish_date')
        return (pd is None, pd)
    done_items = sorted(done_items, key=sort_key)

    print("\n## Published Learning Paths\n| Title | Start Date | Publish Date | Time to Publish (days) | Program | Category | CSP |")
    print("|-------|--------------|-------------|----------------------|-----|----------|-----|")
    published_count = 0
    time_to_publish_values = []
    csp_counts = {"Google Cloud": 0, "Microsoft Azure": 0, "AWS": 0, "Oracle": 0}
    for item in done_items:
        html_title, category = get_html_title(item['published_url']) if item['published_url'] else ('', None)
        if html_title and html_title.endswith(' | Arm Learning Paths'):
            html_title = html_title[:-len(' | Arm Learning Paths')]
        title_link = f"[{html_title}]({item['published_url']})" if item['published_url'] else html_title
        
        # Get CSP tags for servers-and-cloud-computing LPs
        csps = get_cloud_service_providers(item['published_url'], category) if item['published_url'] else []
        csp_str = ", ".join(csps) if csps else ""
        for csp in csps:
            if csp in csp_counts:
                csp_counts[csp] += 1
        # Format start and publish dates
        formatted_start_date = ''
        formatted_publish_date = ''
        if item['start_date']:
            try:
                formatted_start_date = datetime.datetime.strptime(item['start_date'], "%Y-%m-%d").strftime("%B %d, %Y")
            except Exception:
                formatted_start_date = item['start_date']
        if item['publish_date']:
            try:
                formatted_publish_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").strftime("%B %d, %Y")
            except Exception:
                formatted_publish_date = item['publish_date']
        # Calculate time to publish in days
        time_to_publish = ''
        if item['start_date'] and item['publish_date']:
            try:
                start_dt = datetime.datetime.strptime(item['start_date'], "%Y-%m-%d")
                publish_dt = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d")
                time_to_publish = (publish_dt - start_dt).days
                time_to_publish_values.append(time_to_publish)
            except Exception:
                time_to_publish = ''
        
        # Check for ACM, CCA, and SME labels
        acm_label = "ACM" if item.get('acm_label') else ""
        cca_label = "CCA" if item.get('cca_label') else ""
        sme_label = "SME" if item.get('sme_label') else ""
        program_col = " ".join(filter(None, [acm_label, cca_label, sme_label]))
        
        print(f"| {title_link} | {formatted_start_date} | {formatted_publish_date} | {time_to_publish} | {program_col} | {category or ''} | {csp_str} |")
        published_count += 1

    # Count published Learning Paths by category
    from collections import Counter
    category_counts = Counter()
    for item in done_items:
        _, category = get_html_title(item['published_url']) if item['published_url'] else ('', None)
        if category:
            category_counts[category] += 1
        else:
            category_counts['(uncategorized)'] += 1

    print("\n| Statistic | Value |\n|-----------|-------|")
    print(f"| Number of Learning Paths published | {published_count} |")
    acm_count = sum(1 for item in done_items if item.get('acm_label'))
    print(f"| Number of ACM Learning Paths published | {acm_count} |")
    if time_to_publish_values:
        avg_time = sum(time_to_publish_values) / len(time_to_publish_values)
        max_time = max(time_to_publish_values)
        print(f"| Average time to publish (days) | {avg_time:.1f} |")
        print(f"| Longest time to publish (days) | {max_time} |")
    else:
        print(f"| Average time to publish (days) | N/A |")
        print(f"| Longest time to publish (days) | N/A |")
    # Add category counts
    for cat, count in category_counts.items():
        print(f"| Number in '{cat}' | {count} |")
    
    # Add CSP counts for servers-and-cloud-computing
    if any(count > 0 for count in csp_counts.values()):
        print(f"| Number with Google Cloud tag | {csp_counts['Google Cloud']} |")
        print(f"| Number with Microsoft Azure tag | {csp_counts['Microsoft Azure']} |")
        print(f"| Number with AWS tag | {csp_counts['AWS']} |")
        print(f"| Number with Oracle tag | {csp_counts['Oracle']} |")
    print("")

    # Planned Learning Paths Table
    print("## Planned Learning Paths\n| Title | Program | Created Date |")
    print("|-------|-----|--------------|")
    open_issues = fetch_open_issues()
    planned_count = 0
    for issue in open_issues:
        acm_label = "ACM" if "ACM" in [label["name"] for label in issue.get("labels", [])] else ""
        cca_label = "CCA" if "CCA" in [label["name"] for label in issue.get("labels", [])] else ""
        sme_label = "SME" if "SME" in [label["name"] for label in issue.get("labels", [])] else ""
        program_col = " ".join(filter(None, [acm_label, cca_label, sme_label]))
        created_date = datetime.datetime.strptime(issue.get("created_at", ""), "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y")
        print(f"| [{issue['title']}]({issue['html_url']}) | {program_col} | {created_date} |")
        planned_count += 1
    print(f"\nTotal planned Learning Paths: {planned_count}\n")

    print(f"\n_Report generated on {datetime.datetime.now().astimezone().strftime('%B %d, %Y at %H:%M:%S %Z')}_\n")

def fetch_open_issues():
    url = "https://api.github.com/repos/ArmDeveloperEcosystem/roadmap/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch issues: {response.status_code} {response.text}")

    issues = response.json()
    open_issues = [issue for issue in issues if issue.get("state") == "open"]
    return open_issues

def get_cloud_service_providers(url, category):
    """
    Detect which cloud service providers are tagged for a learning path.
    Only checks for servers-and-cloud-computing category.
    Returns a list of CSP tags (e.g., ['Google Cloud', 'Microsoft Azure']).
    """
    if category != "servers-and-cloud-computing":
        return []
    
    # Extract the learning path slug from URL
    if not url or not url.startswith("https://learn.arm.com/learning-paths/servers-and-cloud-computing/"):
        return []
    
    path = url[len("https://learn.arm.com/learning-paths/servers-and-cloud-computing/"):]
    parts = path.split("/")
    if not parts or not parts[0]:
        return []
    
    lp_slug = parts[0]
    
    # Fetch the category listing page to extract tags from the div class attribute
    try:
        category_url = "https://learn.arm.com/learning-paths/servers-and-cloud-computing/"
        response = requests.get(category_url, timeout=15)
        if response.status_code != 200:
            return []
        
        # Look for the div containing this learning path's card
        # The pattern is: <div class='...' with tags><ads-card link=.../{lp_slug}/
        # Extract the class attribute content that precedes the ads-card link
        import re
        pattern = rf"<div class='([^']*)'><ads-card link=/learning-paths/servers-and-cloud-computing/{re.escape(lp_slug)}/"
        match = re.search(pattern, response.text)
        
        if not match:
            return []
        
        class_attr = match.group(1)
        
        # Map tag names to display names
        csp_tag_map = {
            "tag-google-cloud": "Google Cloud",
            "tag-microsoft-azure": "Microsoft Azure",
            "tag-aws": "AWS",
            "tag-oracle": "Oracle"
        }
        
        found_csps = []
        for tag, display_name in csp_tag_map.items():
            if tag in class_attr:
                found_csps.append(display_name)
        
        return found_csps
        
    except Exception as e:
        print(f"Warning: Failed to get CSP tags for {lp_slug}: {e}", file=sys.stderr)
        return []

def get_html_title(url):
    category = None
    if url:
        if url.startswith("https://learn.arm.com/install-guides"):
            category = "install-guides"
        elif url.startswith("https://learn.arm.com/learning-paths"):
            # Extract the first directory after /learning-paths/
            path = url[len("https://learn.arm.com/learning-paths/"):]
            parts = path.split("/")
            if len(parts) > 1 and parts[0]:
                category = parts[0]
            elif len(parts) == 1 and parts[0]:
                category = parts[0]
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag is not None and title_tag.string:
            return title_tag.string.strip(), category
        else:
            return None, category
    except Exception as e:
        print(f"Error: {e}")
        return None, category

if __name__ == "__main__":
    # Ensure the reports directory exists in the current working directory
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    parser = argparse.ArgumentParser(description="Generate Learning Path monthly report.")
    parser.add_argument("--month", type=str, help="Month to generate report for (format: YYYY-MM). Defaults to current month.")
    parser.add_argument("--month-range", nargs=2, metavar=('START', 'END'), help="Range of months to generate report for (format: YYYY-MM YYYY-MM).")
    args = parser.parse_args()

    month_filter = None
    month_range = None

    if args.month_range:
        try:
            start = datetime.datetime.strptime(args.month_range[0], "%Y-%m")
            end = datetime.datetime.strptime(args.month_range[1], "%Y-%m")
            # Use the first day of start month and last day of end month
            start_dt = start.replace(day=1)
            # Get last day of end month
            next_month = (end.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
            end_dt = next_month - datetime.timedelta(days=1)
            if start_dt > end_dt:
                print("Start month must be before or equal to end month.")
                sys.exit(1)
            month_range = (start_dt, end_dt)
        except ValueError:
            print("Invalid month-range format. Use YYYY-MM YYYY-MM.")
            sys.exit(1)
    elif args.month:
        try:
            datetime.datetime.strptime(args.month, "%Y-%m")
            month_filter = args.month
        except ValueError:
            print("Invalid month format. Use YYYY-MM.")
            sys.exit(1)
    else:
        month_filter = datetime.date.today().strftime("%Y-%m")

    if month_range:
        output_filename = os.path.join(reports_dir, f"LP-report-{month_range[0].strftime('%Y-%m')}_to_{month_range[1].strftime('%Y-%m')}.md")
    else:
        report_month = datetime.datetime.strptime(month_filter, "%Y-%m")
        output_filename = os.path.join(reports_dir, f"LP-report-{report_month.strftime('%Y-%m')}.md")

    with open(output_filename, "w") as f:
        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(f))
            # Also print to original stdout
            class Tee:
                def __init__(self, *files):
                    self.files = files
                def write(self, obj):
                    for file in self.files:
                        file.write(obj)
                def flush(self):
                    for file in self.files:
                        file.flush()
            tee = Tee(f, sys.__stdout__)
            with contextlib.redirect_stdout(tee):
                generate_report(month_filter=month_filter, month_range=month_range)
    print(f"Report written to {output_filename}")
