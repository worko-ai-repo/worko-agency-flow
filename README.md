# worko-agency-flow

This folder contains a small test AWS Lambda and a SAM template to deploy it.

Files added:

- `template.yaml` — SAM template for the `agency-test-lambda`.
- `src/lambda_function.py` — simple handler returning JSON metadata.
- `layers/python-deps/requirements.txt` — dependencies for the Lambda layer.
- `requirements.txt` — top-level project requirements.
- `samconfig.toml` — SAM config with Docker container build enabled (required for Windows).

## Prerequisites

- **AWS CLI** — install from https://aws.amazon.com/cli/
- **SAM CLI** — install from https://aws.amazon.com/serverless/sam/
- **Docker Desktop** — install from https://www.docker.com/ (SAM uses Docker to build Lambda layers on Windows)

## Quick Deploy (Windows with Docker)

The `samconfig.toml` file pre-configures `use_container = true` so that builds run inside Docker containers (required on Windows for Python layer compatibility).

```powershell
cd C:\Users\Administrator\Desktop\worko_working\worko-workspace\worko-agency-flow

# Build using Docker (Docker Desktop must be running)
sam build

# Deploy (first time: use --guided to set stack name, S3 bucket, region, etc.)
sam deploy --guided

# Subsequent deploys (config saved in samconfig.toml):
sam deploy
```

After deployment, the stack outputs include `ApiEndpoint` which hosts the `/agency-test` GET endpoint.

## Local Testing

### Prerequisites
- Docker Desktop running
- Update `env.json` with your Azure OpenAI credentials

### Quick Test
```cmd
test-local.bat
```

### Manual Testing
```cmd
# Build
sam build

# Test function
sam local invoke AgencyTestFunction --env-vars env.json

# Start local API
sam local start-api --env-vars env.json
```

### Test Events
- `events/initial-event.json` - Test with interview data
- `events/feedback-event.json` - Test with feedback data
- `events/completion-event.json` - Test completion flow

## Notes

- **Docker Required:** On Windows, Docker Desktop must be running for `sam build` to work (it builds the layer inside a Docker container).
- **samconfig.toml:** Pre-configured with `use_container = true`, `region = eu-west-1`, and `stack_name = worko-agency-test`. Modify as needed.
- **Azure OpenAI Parameters:** Optionally provide during `sam deploy --guided` or leave blank (they're optional).
- **Layer Dependencies:** The layer packages `requests` from `layers/python-deps/requirements.txt`.
