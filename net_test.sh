#!/bin/bash

# URL to check
url="http://www.google.com"

# Function to check website
check_website() {
    local u1=$1
    local timeout=${2:-5}

    # Use curl to check the website
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "$u1")

    if [ "$response" -eq 200 ]; then
        echo "ok"
    else
        echo "403"
    fi
}

# Main script execution
check_website $url