import { spawn } from "child_process";

// Spawn Streamlit process
const streamlit = spawn("streamlit", ["run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"], {
  stdio: "inherit",
  shell: true
});

streamlit.on("close", (code) => {
  console.log(`Streamlit exited with code ${code}`);
  process.exit(code);
});

// Handle termination signals
process.on('SIGTERM', () => {
  streamlit.kill('SIGTERM');
  process.exit();
});

process.on('SIGINT', () => {
  streamlit.kill('SIGINT');
  process.exit();
});
