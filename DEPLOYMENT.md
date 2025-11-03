# Deployment Instructions for Google Cloud Run

This guide provides the steps to build the Docker image for this project and deploy it to Google Cloud Run.

### Prerequisites

1.  **Install and Initialize `gcloud` CLI**: Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured.
2.  **Install Docker**: Ensure [Docker](https://docs.docker.com/get-docker/) is installed and running on your machine.
3.  **Set your Project ID**: Configure `gcloud` with your project ID:
    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```

### Deployment Steps

1.  **Enable APIs**: Enable the Artifact Registry, Cloud Run, and Secret Manager APIs for your project:
    ```bash
    gcloud services enable artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com
    ```

2.  **Create an Artifact Registry Repository**: Create a Docker repository to store your image. Replace `[REPOSITORY_NAME]` and `[REGION]` with your desired names (e.g., `workout-tracker-repo` and `us-central1`).
    ```bash
    gcloud artifacts repositories create [REPOSITORY_NAME] \
        --repository-format=docker \
        --location=[REGION] \
        --description="Workout Tracker container images"
    ```

3.  **Authenticate Docker**: Configure Docker to use `gcloud` as a credential helper for Artifact Registry:
    ```bash
    gcloud auth configure-docker [REGION]-docker.pkg.dev
    ```

4.  **Build and Tag the Docker Image**: Build your image using Docker. The tag format is important for pushing to Artifact Registry.
    *   `[REGION]`: The region of your Artifact Registry repository.
    *   `[YOUR_PROJECT_ID]`: Your Google Cloud project ID.
    *   `[REPOSITORY_NAME]`: The name you chose for your repository.
    *   `[IMAGE_NAME]`: A name for your image (e.g., `app-server`).

    Run this command from the root of your project directory (`C:\Users\Yash\Desktop\workout-tracker`):
    ```bash
    docker build -t [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/[IMAGE_NAME]:latest .
    ```

5.  **Push the Image to Artifact Registry**:
    ```bash
    docker push [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/[IMAGE_NAME]:latest
    ```

6.  **Create and Configure Secrets**:
    Your application now reads secrets directly from Google Secret Manager. You must create the secrets and grant the Cloud Run service account access to them.

    *   **Create each required secret** (e.g., `DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.):
        ```bash
        gcloud secrets create [SECRET_NAME] --replication-policy="automatic"
        ```
    *   **Add the secret value**:
        ```bash
        gcloud secrets versions add [SECRET_NAME] --data-file="/path/to/your/secret-file.txt"
        ```
        (Or use `--data='your-secret-value'`)

    *   **Grant Access**: Grant the default Compute Engine service account access to each secret.
        ```bash
        gcloud secrets add-iam-policy-binding [SECRET_NAME] \
            --member="serviceAccount:$(gcloud projects describe [YOUR_PROJECT_ID] --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
            --role="roles/secretmanager.secretAccessor"
        ```

7.  **Deploy to Cloud Run**: Deploy your container image. The application code will fetch the secrets automatically, so you only need to provide the `PROJECT_ID` as an environment variable.

    ```bash
    gcloud run deploy workout-tracker-service \
        --image=[REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/[IMAGE_NAME]:latest \
        --platform=managed \
        --region=[REGION] \
        --allow-unauthenticated \
        --set-env-vars="PROJECT_ID=[YOUR_PROJECT_ID]"
    ```
    *   `--allow-unauthenticated` makes your service publicly accessible. If you need to restrict access, you can configure authentication later.

After the last command completes, the output will include the URL of your deployed service.

```