#!/bin/bash

# Set the project ID
PROJECT_ID="rhea-461313"

echo "📦 Project: $PROJECT_ID"
echo "🔍 Fetching IAM policy bindings..."

# Step 1: Get IAM policy and list unique members
echo "👥 Listing all IAM accounts used in the project..."
gcloud projects get-iam-policy $PROJECT_ID \
  --format="table(bindings.members)" | \
  grep -E "user:|serviceAccount:" | sort | uniq

echo -e "\n✅ Step 1 complete: All accounts listed above.\n"

# Step 2: List permissions for each account
echo "🔐 Fetching roles and permissions for each account..."
echo "This might take a few seconds..."

# Get full policy
POLICY_JSON=$(gcloud projects get-iam-policy $PROJECT_ID --format=json)

# Extract unique members
MEMBERS=$(echo $POLICY_JSON | jq -r '.bindings[].members[]' | sort | uniq)

# Loop through each member and list their roles
for MEMBER in $MEMBERS; do
  echo -e "\n👤 Account: $MEMBER"
  echo "🔗 Roles:"
  echo $POLICY_JSON | jq -r --arg MEMBER "$MEMBER" '.bindings[] | select(.members[]? == $MEMBER) | .role'
done
