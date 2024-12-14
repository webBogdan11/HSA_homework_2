#!/bin/bash

# stress_test.sh
# Script to perform stress testing on combined endpoint using ApacheBench (ab)

# Base URL
BASE_URL="http://localhost:8080"

# Combined endpoint and description
ENDPOINT="/api/combined"
DESCRIPTION="Combined MongoDB and Elasticsearch Endpoint"

# ApacheBench Parameters
TOTAL_REQUESTS=5000      # Total number of requests to perform
CONCURRENCY=100          # Number of multiple requests to make at a time

# Output directory
OUTPUT_DIR="./ab_results"
mkdir -p "$OUTPUT_DIR"

# Function to perform the test
perform_test() {
  local endpoint=$1
  local description=$2
  local url="$BASE_URL$endpoint"
  local timestamp=$(date +"%Y%m%d_%H%M%S")
  # Replace slashes with underscores for filename
  local sanitized_endpoint=$(echo "$endpoint" | sed 's|/|_|g')
  local output_file="$OUTPUT_DIR/ab_${sanitized_endpoint}_$timestamp.txt"

  echo "Testing $description at $url"
  ab -n "$TOTAL_REQUESTS" -c "$CONCURRENCY" "$url" > "$output_file"

  echo "Results saved to $output_file"
  echo "----------------------------------------"
}

# Perform the test on combined endpoint
perform_test "$ENDPOINT" "$DESCRIPTION"

echo "Test completed."
