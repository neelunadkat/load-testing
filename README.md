# Load Testing Tool

A simple load testing utility built using **k6** to validate Login API performance under concurrent user load.

## Project Files

```text
login-test.js      # Main load testing script
users.json         # Test user credentials
k6-reporter.js     # HTML report generator
```

---

# Software Requirements

Before running the tool, install the following software on your machine.

## 1. Install k6

### macOS

Install using Homebrew:

```bash
brew install k6
```

Verify installation:

```bash
k6 version
```

### Windows

Install using Chocolatey:

```powershell
choco install k6
```

Or download from:

https://grafana.com/docs/k6/latest/set-up/install-k6/

Verify installation:

```bash
k6 version
```

---

## 2. Install Node.js

Node.js is required for generating HTML reports.

Download and install the latest LTS version:

https://nodejs.org

Verify installation:

```bash
node -v
npm -v
```

---

# Running the Load Test

Open Terminal (macOS/Linux) or Command Prompt (Windows).

Navigate to the project folder:

```bash
cd path/to/load-testing-tool
```

Run the load test:

```bash
k6 run login-test.js
```

The script will:

* Read test users from `users.json`
* Execute concurrent login requests
* Collect performance metrics
* Display results in the terminal

---

# Generate HTML Report

After the test completes, generate the HTML report:

```bash
node k6-reporter.js
```

A new timestamp-based report will be generated automatically.

Example:

```text
summary_13_Jun_1_40PM.html
summary_13_Jun_2_10PM.html
summary_15_Jun_5_08PM.html
```

---

# View Report

Open the generated HTML file in any browser.

### macOS

```bash
open summary_15_Jun_5_08PM.html
```

### Windows

```powershell
start summary_15_Jun_5_08PM.html
```

---

# Output Metrics

The report includes:

* Success Rate
* Failed Requests
* Average Response Time
* Minimum Response Time
* Maximum Response Time
* Throughput
* Request Duration Statistics
* Virtual User Information

---

# Notes

* A new HTML report is generated for every execution.
* Previous reports are preserved for historical comparison.
* The current version is configured for Login API load testing.
* Update `users.json` to add or modify test accounts.
