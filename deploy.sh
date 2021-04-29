# TODO: Set DOCKER_TAGNAME, PROJECT_ID, SERVICE_ACCOUNT

CLOUDSDK_CORE_DISABLE_PROMPTS="1"
IMAGE_NAME=""
CONCURRENCY="1"
CPU="1"
MEMORY="256Mi"
MAX_INSTANCES="1"
TIMEOUT="600s"
PROJECT_ID=""
SERVICE_ACCOUNT=""
REGION="us-east4"
VERSION=$(jq -M '.["app"]' app/metadata.json | sed 's/"//g')

gcloud --quiet auth configure-docker
docker build -t "${IMAGE_NAME}" .
docker tag ${IMAGE_NAME} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}

TAG=v${VERSION//\./\-}

gcloud beta run deploy capstone-api \
    --image=gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION} \
    --concurrency=${CONCURRENCY} \
    --cpu=${CPU} \
    --memory=${MEMORY} \
    --max-instances=${MAX_INSTANCES} \
    --platform=managed \
    --port=8081 \
    --allow-unauthenticated \
    --timeout=${TIMEOUT} \
    --set-env-vars="PROJECT_ID=${PROJECT_ID},env=prod" \
    --tag=${TAG} \
    --region=${REGION} \
    --service-account=${SERVICE_ACCOUNT} \
    --format=json