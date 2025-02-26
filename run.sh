#!/bin/bash

# Exit on error
set -e

# Run streamlit app
streamlit run hn_core/app/app.py "$@"
