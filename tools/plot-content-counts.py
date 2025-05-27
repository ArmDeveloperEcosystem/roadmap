#!/usr/bin/env python3
import os
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
from datetime import datetime

REPORTS_DIR = 'reports/content-count/'
pattern = re.compile(r'content_summary_(\d{2}-\d{2}-\d{4})\.md$')

# Data containers
dates = []
install_guides = []
unique_paths = []
published_content = []

for fname in sorted(os.listdir(REPORTS_DIR)):
    m = pattern.match(fname)
    if not m:
        continue
    date_str = m.group(1)
    with open(os.path.join(REPORTS_DIR, fname), 'r') as f:
        content = f.read()
        # Extract values
        ig = re.search(r'\| Install Guides \| (\d+) \|', content)
        up = re.search(r'\| Total Learning Paths \(unique\) \| (\d+) \|', content)
        pc = re.search(r'\| Total Published Content \(unique Learning Paths \+ Install Guides\) \| (\d+) \|', content)
        if ig and up and pc:
            # Convert MM-DD-YYYY to datetime for sorting
            dt = datetime.strptime(date_str, '%m-%d-%Y')
            dates.append(dt)
            install_guides.append(int(ig.group(1)))
            unique_paths.append(int(up.group(1)))
            published_content.append(int(pc.group(1)))

# Sort by date
sorted_data = sorted(zip(dates, install_guides, unique_paths, published_content))
dates, install_guides, unique_paths, published_content = zip(*sorted_data)

# Plot
plt.figure(figsize=(12, 7))
plt.plot(dates, install_guides, label='Install Guides')
plt.plot(dates, unique_paths, label='Total Learning Paths (unique)')
plt.plot(dates, published_content, label='Total Published Content')
plt.xlabel('Date')
plt.ylabel('Count')
plt.title('Arm Learning Paths Content Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Annotate numbers at the start of each quarter
for i, dt in enumerate(dates):
    if dt.month in [1, 4, 7, 10] or i == 0 or i == len(dates) - 1:  # Start of each quarter, first point, and last point
        plt.annotate(str(install_guides[i]), (dt, install_guides[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='tab:blue')
        plt.annotate(str(unique_paths[i]), (dt, unique_paths[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='tab:orange')
        plt.annotate(str(published_content[i]), (dt, published_content[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='tab:green')

plt.savefig('reports/content-count/content_over_time.png')
