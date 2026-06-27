import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// Loads strictly from your local file system to handle network blockages
import { htmlReport } from "./k6-reporter.js";

// Safely load and parse data across all concurrent virtual users
const users = new SharedArray("user credentials", function () {
  const fileData = JSON.parse(open("./users.json"));
  const records = Array.isArray(fileData) ? fileData : fileData.users;
  return records.filter(item => item && item.email);
});

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<3000"],
  },
};

export default function () {
  const user = users[Math.floor(Math.random() * users.length)];

  if (!user) {
    console.warn("Warning: No valid users available in the loaded array.");
    return;
  }

  const payload = JSON.stringify({
    email: user.email,
    password: user.password,
    rememberMe: true,
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const response = http.post(
    "https://one.encircletechnologies.com/api/v1/auth/login", //live
    //"https://epms-app.encircledev.com/api/v1/auth/login", //Production
    //"https://epms-app-staging.encircledev.com/api/v1/auth/login", //Staging
    payload,
    params
  );

  let loginValid = false;
  try {
    const jsonResponse = JSON.parse(response.body);
    loginValid = !!(jsonResponse && (jsonResponse.token || jsonResponse.accessToken || jsonResponse.data || response.body.includes("success")));
  } catch (e) {
    loginValid = false;
  }

  const statusIcon = response.status === 200 && loginValid ? "✅ SUCCESS" : "❌ FAILED ";
  const paddedEmail = user.email.padEnd(35, " ");
  const paddedStatus = `Status: ${response.status}`.padEnd(12, " ");
  
  console.log(`[${statusIcon}] | User: ${paddedEmail} | ${paddedStatus} | Time: ${response.timings.duration.toFixed(0)}ms`);

  check(response, {
    "status is 200": (r) => r.status === 200,
    "has valid authentication data": () => loginValid
  });

  sleep(1);
}

// Generates user-friendly file naming mapping: summary_13_Jun_1:13PM.html
function getTimestampFilename() {
  const now = new Date();
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  
  const day = now.getDate();
  const month = months[now.getMonth()];
  
  let hours = now.getHours();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; 
  
  const minutes = String(now.getMinutes()).padStart(2, '0');
  
  return `summary_${day}_${month}_${hours}:${minutes}${ampm}.html`;
}

export function handleSummary(data) {
  const rawFileName = getTimestampFilename();
  
  // FIXED: Prepended 'Report/' to ensure it gets written directly into that subdirectory folder
  const filePath = `Report/${rawFileName}`;
  
  console.log(`\n💾 Exporting user-friendly summary report to: ${filePath}\n`);

  const configuredVUs = options.vus || 0;
  const totalUserPoolCount = users.length;

  // Injects critical summary data metrics right into the upper description block of your HTML
  const reportOptions = {
    title: "EPMS Authentication Load Test Report",
    customData: {
      "Target Environment": "Live (One Encircle)",
      "Total Virtual Users (VUs)": `${configuredVUs} VUs Parallel`,
      "Total Users Pool Tested": `${totalUserPoolCount} Accounts Available`,
      "Metric Table Display Units": "All duration numbers are calculated in Milliseconds (ms)"
    }
  };

  const reportOutputs = {};
  
  // Uses the folder path variable key to write into the correct directory location
  reportOutputs[filePath] = htmlReport(data, reportOptions); 
  
  // Replaced remote textSummary with k6's built-in stringifier fallback to work 100% offline
  reportOutputs["stdout"] = JSON.stringify(data.metrics, null, 2); 

  return reportOutputs;
}
