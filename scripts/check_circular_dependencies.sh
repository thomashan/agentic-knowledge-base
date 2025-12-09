#!/bin/bash

echo "Starting circular dependency checks for all subprojects..."
echo ""

# Loop through all subdirectories in app/
for project_dir in app/*; do
    # Check if it's a directory
    if [ -d "$project_dir" ]; then
        SUBPROJECT_NAME=$(basename "$project_dir")
        SUBPROJECT_SRC_PATH="$project_dir/src"

        echo "================================================="
        echo "Checking for circular dependencies in: $SUBPROJECT_NAME ($SUBPROJECT_SRC_PATH)"
        echo "================================================="
        
        # Check if the src directory exists within the subproject
        if [ -d "$SUBPROJECT_SRC_PATH" ]; then
            # Run pydeps from the project root, targeting the subproject's src directory
            uv run pydeps --show-cycles --noshow "$SUBPROJECT_SRC_PATH"
        else
            echo "No 'src' directory found in $SUBPROJECT_NAME, skipping."
        fi
        echo ""
    fi
done

rm -rf *.svg

echo "Finished all circular dependency checks."
