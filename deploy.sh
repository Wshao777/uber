#!/bin/bash

# === Configuration ===
# Please replace the following placeholder values with your actual GCP Project ID and Service Account Email.
GCP_PROJECT_ID="YOUR_PROJECT_ID"  # e.g., my-lightning-empire-123
SA_EMAIL="YOUR_SERVICE_ACCOUNT_EMAIL" # e.g., my-project-id@appspot.gserviceaccount.com
REGION="asia-east1" # You can change this to your preferred region

# === Script Variables ===
IMAGE_NAME="lightning-dispatch-fleet"
IMAGE_TAG="gcr.io/${GCP_PROJECT_ID}/${IMAGE_NAME}"
JOB_NAME="daily-dispatch-mission"
SCHEDULER_NAME="daily-dispatch-trigger"
SECRET_NAME="google-credentials"

# --- Pre-flight Checks ---
echo "INFO: Performing pre-flight checks..."

# Check for placeholder values
if [ "$GCP_PROJECT_ID" = "YOUR_PROJECT_ID" ] || [ "$SA_EMAIL" = "YOUR_SERVICE_ACCOUNT_EMAIL" ]; then
  echo "❌ ERROR: Please replace the placeholder values for GCP_PROJECT_ID and SA_EMAIL in this script."
  exit 1
fi

# Check for required files
for file in Dockerfile requirements.txt google_credentials.json lightning_dispatch_8AI_dual_sync.py; do
  if [ ! -f "$file" ]; then
    echo "❌ ERROR: Missing required file '$file'. Please ensure you are in the correct project directory."
    exit 1
  fi
done

# Check for gcloud and docker commands
if ! command -v gcloud &> /dev/null || ! command -v docker &> /dev/null; then
  echo "❌ ERROR: 'gcloud' or 'docker' command not found. Please ensure Google Cloud SDK and Docker are installed and in your PATH."
  exit 1
fi

echo "✅ Pre-flight checks passed."

# --- Deployment Steps ---
set -e # Exit immediately if a command exits with a non-zero status.

echo -e "\n--- Step 1: Setting GCP Project ---"
gcloud config set project "$GCP_PROJECT_ID"

echo -e "\n--- Step 2: Enabling Required APIs ---"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com

echo -e "\n--- Step 3: Configuring Docker Authentication ---"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

echo -e "\n--- Step 4: Building and Uploading Docker Container ---"
gcloud builds submit --tag "$IMAGE_TAG" .

echo -e "\n--- Step 5: Uploading Credentials to Secret Manager ---"
if gcloud secrets describe "$SECRET_NAME" &> /dev/null; then
  echo "INFO: Secret '$SECRET_NAME' already exists. Skipping creation."
else
  gcloud secrets create "$SECRET_NAME" --data-file=google_credentials.json
fi
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

echo -e "\n--- Step 6: Granting Service Account Cloud Run Invoker Role ---"
gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker"

echo -e "\n--- Step 7: Creating Cloud Run Job ---"
gcloud run jobs create "$JOB_NAME" \
  --image "$IMAGE_TAG" \
  --region "$REGION" \
  --set-secrets="/app/google_credentials.json=${SECRET_NAME}:latest" \
  --max-retries 3 \
  --task-timeout "10m"

echo -e "\n--- Step 8: Creating Cloud Scheduler Task ---"
gcloud scheduler jobs create http "$SCHEDULER_NAME" \
  --schedule="0 8 * * *" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${GCP_PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method=POST \
  --oidc-service-account-email="$SA_EMAIL" \
  --time-zone="Asia/Taipei"

echo -e "\n✅ Deployment complete! The 'Lightning AI Legion' is ready for duty."
echo "To manually test the job, run: gcloud run jobs execute ${JOB_NAME} --region ${REGION}"
echo "To view logs, run: gcloud run jobs logs ${JOB_NAME} --region ${REGION} --limit 50"
set +e