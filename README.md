# Securing FastAPI Routes with JSON Web Tokens

## Prereqs

- Python3.7+
- Docker
- Google Cloud Account (Signup for free and get $300 worth of credit)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- cURL or Postman
  <br/>

## Project Setup

1. Clone the repository

```
git clone git@github.com:tdeg/ms-capstone.git
```

2. Open the directory containg the project, generate a secure secret value, and add the variables to .env file for local development

Change directory

```bash
cd ms-capstone
```

Generate a secure string

```bash
openssl rand -hex 32
c3b1983511b2d4b7082bbf1f104590653d41b4c94f2341818a8a814a272a0c8e
```

Create the .env file

```bash
JWT_SECRET=c3b1983511b2d4b7082bbf1f104590653d41b4c94f2341818a8a814a272a0c8e
JWT_ALGORITHM=HS256
```

3. Configure gcloud sdk

```bash
gcloud auth login
gcloud config set project PROJECT_ID
```

4. Test locally with docker

```docker
# build the image

docker build -t capstone-api .
```

```docker
# build the image

docker build -t capstone-api .
```

```docker
# run the image

docker run -t -p 8081:8081 capstone-api
```

```bash
# test the unprotected endpoint

curl -H 'Accept: application/json' http://localhost:8081/unprotected
```

If the request is succesful you should get back a json response:

```json
{ "protected": false }
```

You should also see in the server logs that the /unprotected route was requested

```bash
INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using statreload
INFO:     Started server process [9]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     172.17.0.1:64396 - "GET /unprotected HTTP/1.1" 200 OK
```

Get the name of the running docker container

```bash
docker container ls

CONTAINER ID   IMAGE          COMMAND            CREATED         STATUS         PORTS                    NAMES
fd5e996c4e04   capstone-api   "python main.py"   3 minutes ago   Up 3 minutes   0.0.0.0:8081->8081/tcp   trusting_cohen
```

Stop the running docker container

```bash
docker stop trusting_cohen
```

5. Deploy to cloud run

Create a [service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-console), and give the service account the following roles:

```
Secret Manager Secret Accessor

Cloud Run Service Agent
```

Create secrets using the [secret manager](https://cloud.google.com/secret-manager/docs/quickstart). The two secrets that need to be created are JWT_SECRET, and JWT_ALGORITHM:

```
JWT_SECRET=c3b1983511b2d4b7082bbf1f104590653d41b4c94f2341818a8a814a272a0c8e
JWT_ALGORITHM=HS256
```

Once the service account is created modify the deploy.sh script to include your PROJECT_ID and SERVICE_ACCOUNT:

```bash
# TODO: Set PROJECT_ID, SERVICE_ACCOUNT

CLOUDSDK_CORE_DISABLE_PROMPTS="1"
IMAGE_NAME="cybapi"
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
    --set-env-vars="PROJECT_ID=${PROJECT_ID},ENV=prod" \
    --tag=${TAG} \
    --region=${REGION} \
    --service-account=${SERVICE_ACCOUNT} \
    --format=json
```

Make the script executable:

```bash
chmod +x deploy.sh
```

Run the script:

```
./deploy.sh
```

Once comepleted, get the base url for the API

```bash
gcloud beta run services list

   SERVICE       REGION    URL                                           LAST DEPLOYED BY           LAST DEPLOYED AT
  capstone-api  us-east4  https://capstone-api-mewph73t4a-uk.a.run.app  tylerdegennaro7@gmail.com  2021-05-06T18:04:51.972472Z
```

Now that we have the API for our URL, try the following cURL commands to test it:

```bash
# unprotected:
curl -H 'Accept: application/json' https://capstone-api-mewph73t4a-uk.a.run.app/unprotected

# signup:
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' --data '{"email":"email@gmail.com","password":"password"}' https://capstone-api-mewph73t4a-uk.a.run.app/signup

# login:
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' --data '{"email":"email@gmail.com","password":"password"}' https://capstone-api-mewph73t4a-uk.a.run.app/login

# protected route:
curl -H 'Accept: application/json' -H "Authorization: Bearer TOKEN" https://capstone-api-mewph73t4a-uk.a.run.app/protected

# Message route, create two users
user1:
-------------------

# POST message one in from user 1
curl -s -X \
POST -H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN" \
-H 'Content-Type: application/json' --data '{"content":"hello from user1"}' \
https://capstone-api-mewph73t4a-uk.a.run.app/message

# POST message two in from user 1
curl -s -X \
POST -H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN1" \
-H 'Content-Type: application/json' --data '{"content":"hello again from user1"}' \
https://capstone-api-mewph73t4a-uk.a.run.app/message

# Read messages pertaining to a user
curl \
-H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN1" \
https://capstone-api-mewph73t4a-uk.a.run.app/message

user2:
-------------------
# POST message one in from user 2
curl -s -X \
POST -H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN2" \
-H 'Content-Type: application/json' --data '{"content":"hello from user2"}' \
https://capstone-api-mewph73t4a-uk.a.run.app/message

# POST message one in from user 2
curl -s -X \
POST -H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN2" \
-H 'Content-Type: application/json' --data '{"content":"hello again from user2"}' \
https://capstone-api-mewph73t4a-uk.a.run.app/message

# Read messages pertaining to a user
curl \
-H 'Accept: application/json' \
-H "Authorization: Bearer TOKEN1" \
https://capstone-api-mewph73t4a-uk.a.run.app/message
```
