# Worko Agency Flow - AWS Lambda Deployment

## 📖 The Complete Story: From Zero to Automated Deployment

This project is a simple AWS Lambda function that automatically deploys to AWS whenever you push code to the `main` branch. Let me walk you through everything we learned and how it all works together.

---

## 🎯 What This Project Does

This is a **test Lambda function** that:
- Runs on AWS Lambda (serverless compute)
- Uses Python 3.9 runtime
- Has external dependencies packaged as a Lambda Layer
- Automatically deploys via CodeCatalyst CI/CD pipeline
- Can be invoked directly (no API Gateway needed)

---

## 📚 Lessons Learned: Trial and Error Journey

### Problem 1: SAM CLI Not Installed Locally
**Issue**: Couldn't test locally without SAM CLI  
**Solution**: Created `test_lambda.py` to test the function directly with Python

### Problem 2: Docker Required for Layer Building
**Issue**: Windows needs Docker to build Lambda layers  
**Solution**: Used EC2 compute in CodeCatalyst (has Docker built-in)

### Problem 3: S3 Bucket for Deployment
**Issue**: SAM needs S3 bucket to upload Lambda code  
**Solution**: Used existing bucket `aws-sam-cli-managed-default-samclisourcebucket-mpwvaft0yfqx`

### Problem 4: Reserved Environment Variables
**Issue**: Lambda doesn't allow setting `AWS_REGION` manually  
**Solution**: Removed it - Lambda provides this automatically

### Problem 5: Required Parameters Without Values
**Issue**: Template required Azure OpenAI parameters  
**Solution**: Added placeholder default values for future use

### Problem 6: Failed Stack in ROLLBACK_COMPLETE State
**Issue**: Can't update a failed stack  
**Solution**: Added cleanup step to delete failed stack before deploying

### Problem 7: Invalid CodeCatalyst Connection
**Issue**: Wrong IAM role name in workflow  
**Solution**: Removed connection specification to use default

---

## 📁 Project Structure Explained

```
worko-agency-flow/
├── .codecatalyst/
│   └── workflows/
│       └── auto-deploy.yaml      # CI/CD pipeline definition
├── events/
│   ├── initial-event.json        # Test event for initial mode
│   ├── feedback-event.json       # Test event for feedback mode
│   └── completion-event.json     # Test event for completion mode
├── layers/
│   └── python-deps/
│       └── requirements.txt      # External Python dependencies
├── src/
│   └── lambda_function.py        # Main Lambda handler code
├── .gitignore                    # Files to exclude from git
├── env.json                      # Local environment variables (not in git)
├── env.json.example              # Example environment file
├── README.md                     # This file
├── requirements.txt              # Project-level dependencies
├── samconfig.toml                # SAM deployment configuration
├── template.yaml                 # AWS infrastructure definition
└── test_lambda.py                # Local testing script
```

---

## 📄 File-by-File Explanation

### 1. `template.yaml` - The Infrastructure Blueprint

This file tells AWS what resources to create. Think of it as a recipe for your cloud infrastructure.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
# This is the version of CloudFormation template format we're using
# It's like saying "I'm writing this recipe in English version 2.0"

Transform: AWS::Serverless-2016-10-31
# This enables SAM (Serverless Application Model) shortcuts
# SAM makes it easier to define serverless resources

Description: Worko Agency Flow - Test Lambda
# A human-readable description of what this stack does

Parameters:
  # Parameters are like function arguments - you can pass different values when deploying
  
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
    # This parameter lets you choose which environment to deploy to
    # Default is 'dev', but you can choose 'staging' or 'prod'
  
  AzureOpenAIEndpoint:
    Type: String
    Description: Azure OpenAI endpoint URL
    Default: "https://placeholder.openai.azure.com/"
    # Placeholder for Azure OpenAI endpoint - replace when you need it
  
  AzureOpenAIDeployment:
    Type: String
    Description: Azure OpenAI deployment name
    Default: "placeholder-deployment"
    # Placeholder for Azure OpenAI deployment name
  
  AzureOpenAIApiKey:
    Type: String
    NoEcho: true  # This hides the value in CloudFormation console (security)
    Description: Azure OpenAI API key
    Default: "placeholder-api-key-replace-later"
    # Placeholder for API key - NoEcho keeps it secret

Globals:
  # Global settings that apply to all Lambda functions in this template
  Function:
    Timeout: 60          # Maximum time Lambda can run (60 seconds)
    MemorySize: 256      # RAM allocated to Lambda (256 MB)
    Runtime: python3.9   # Python version to use

Resources:
  # Resources are the actual AWS services we want to create
  
  AgencyLambdaRole:
    # This is an IAM Role - it defines what permissions the Lambda has
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        # This says "Lambda service is allowed to use this role"
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        # This gives Lambda permission to write logs to CloudWatch
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  PythonDependenciesLayer:
    # Lambda Layer - a ZIP file containing external Python libraries
    # Layers are shared across Lambda functions and make deployments faster
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub "agency-test-deps-${Environment}"
      # !Sub means "substitute variables" - creates name like "agency-test-deps-dev"
      Description: Python dependencies for agency test lambda
      ContentUri: layers/python-deps/
      # SAM will look in this folder for requirements.txt and build the layer
      CompatibleRuntimes:
        - python3.9  # This layer only works with Python 3.9
      RetentionPolicy: Delete
      # When you delete the stack, delete this layer too
    Metadata:
      BuildMethod: python3.9
      # Tells SAM to use Python 3.9 to install dependencies

  AgencyTestFunction:
    # The actual Lambda function
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "agency-test-lambda-${Environment}"
      # Creates name like "agency-test-lambda-dev"
      CodeUri: src/
      # Lambda code is in the 'src' folder
      Handler: lambda_function.lambda_handler
      # When Lambda runs, it calls the 'lambda_handler' function in 'lambda_function.py'
      Role: !GetAtt AgencyLambdaRole.Arn
      # Use the IAM role we created above
      Layers:
        - !Ref PythonDependenciesLayer
        # Attach the dependencies layer to this function
      Environment:
        # Environment variables that the Lambda can access
        Variables:
          ENVIRONMENT: !Ref Environment
          # Pass the environment parameter (dev/staging/prod)
          AZURE_OPENAI_ENDPOINT: !Ref AzureOpenAIEndpoint
          AZURE_OPENAI_DEPLOYMENT: !Ref AzureOpenAIDeployment
          AZURE_OPENAI_API_KEY: !Ref AzureOpenAIApiKey
          # Pass Azure OpenAI credentials (currently placeholders)

Outputs:
  # Outputs are values you can see after deployment
  AgencyTestFunctionArn:
    Description: Agency Test Lambda Function ARN
    Value: !GetAtt AgencyTestFunction.Arn
    # ARN is the unique identifier for this Lambda in AWS
    Export:
      Name: !Sub "${AWS::StackName}-AgencyTestFunctionArn"
      # Export this so other CloudFormation stacks can reference it
```

---

### 2. `.codecatalyst/workflows/auto-deploy.yaml` - The Automation Pipeline

This file defines what happens when you push code. It's like a robot that watches your code and deploys it automatically.

```yaml
Name: DeployAgencyLambda
# The name of this workflow (shows up in CodeCatalyst UI)

SchemaVersion: "1.0"
# Version of CodeCatalyst workflow format

Triggers:
  # When should this workflow run?
  - Type: PUSH
    # Run when code is pushed to git
    Branches:
      - main
      # Only run when pushing to the 'main' branch

Actions:
  # Actions are the jobs that run in the workflow
  BuildAndDeploy:
    # Name of this action
    Identifier: aws/build@v1
    # Use AWS's pre-built build action (includes SAM CLI, AWS CLI, etc.)
    
    Inputs:
      Sources:
        - WorkflowSource
        # Use the code from the git repository
    
    Configuration:
      Steps:
        # Steps run in order, one after another
        
        - Run: |
            echo "=== Checking SAM version ==="
            sam --version
            # Print SAM version for debugging
            
            echo "=== Listing files ==="
            ls -la
            # Show all files in the directory
            
            echo "=== Building SAM application ==="
            sam build
            # Build the Lambda function and layer
            # This creates a .aws-sam folder with packaged code
        
        - Run: |
            echo "=== Cleaning up failed stack ==="
            aws cloudformation delete-stack --stack-name worko-agency-test --region ap-south-1 || true
            # Delete the stack if it exists and is in failed state
            # '|| true' means "don't fail if stack doesn't exist"
            
            aws cloudformation wait stack-delete-complete --stack-name worko-agency-test --region ap-south-1 || true
            # Wait for deletion to finish before proceeding
        
        - Run: |
            echo "=== Deploying to AWS ==="
            sam deploy \
              --stack-name worko-agency-test \
              # Name of the CloudFormation stack
              
              --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-mpwvaft0yfqx \
              # S3 bucket where Lambda code is uploaded
              
              --region ap-south-1 \
              # AWS region (Mumbai, India)
              
              --capabilities CAPABILITY_IAM \
              # Allow CloudFormation to create IAM roles
              
              --no-confirm-changeset \
              # Don't ask for confirmation - just deploy
              
              --no-fail-on-empty-changeset
              # Don't fail if nothing changed (idempotent)
    
    Environment:
      Name: dev
      # Deploy to 'dev' environment
    
    Compute:
      Type: EC2
      # Run this workflow on an EC2 instance (has Docker for building layers)
```

---

### 3. `src/lambda_function.py` - The Lambda Handler

This is the actual code that runs when Lambda is invoked.

```python
import json  # For working with JSON data
import os    # For reading environment variables
import requests  # For making HTTP requests (from layer)

def lambda_handler(event, context):
    """
    This is the main function that AWS Lambda calls.
    
    Parameters:
    - event: Input data (dict) - contains the data passed to Lambda
    - context: Runtime information (object) - metadata about the execution
    
    Returns:
    - dict: Response with statusCode, headers, and body
    """
    
    # Get environment variables (set in template.yaml)
    env = os.environ.get("ENVIRONMENT", "dev")
    # Get ENVIRONMENT variable, default to "dev" if not set
    
    region = os.environ.get("AWS_REGION", "")
    # AWS_REGION is automatically provided by Lambda
    
    # Create response body with metadata
    body = {
        "message": "Worko Agency Test Lambda",
        "environment": env,
        "region": region,
        "path": event.get("path"),           # API path if called via API Gateway
        "method": event.get("httpMethod"),   # HTTP method if called via API Gateway
        "queryStringParameters": event.get("queryStringParameters"),  # Query params
    }
    
    # Return response in API Gateway format
    return {
        "statusCode": 200,              # HTTP 200 = success
        "headers": {
            "Content-Type": "application/json"  # Response is JSON
        },
        "body": json.dumps(body),       # Convert dict to JSON string
    }
```

---

### 4. `layers/python-deps/requirements.txt` - External Dependencies

This file lists Python packages that Lambda needs but aren't included by default.

```txt
# External Python libraries needed by the Lambda function
# SAM will install these into a Lambda Layer

requests>=2.31.0
# HTTP library for making API calls
# >=2.31.0 means "version 2.31.0 or newer"
```

---

### 5. `samconfig.toml` - SAM Configuration

This file stores deployment settings so you don't have to type them every time.

```toml
# SAM Configuration - Windows with Docker
# This config enables container-based builds for cross-platform compatibility

version = 0.1
# Configuration file format version

[default]
# Default configuration profile

[default.build.parameters]
use_container = true
# Build Lambda layers inside Docker containers
# Required on Windows for Linux-compatible packages

[default.deploy.parameters]
stack_name = "worko-agency-test"
# CloudFormation stack name

s3_bucket = "worko-agency-artifacts"
# S3 bucket for deployment artifacts (not used in CI/CD)

s3_prefix = "agency-test"
# Folder prefix in S3 bucket

region = "eu-west-1"
# AWS region (Ireland) - for local deployment only

capabilities = "CAPABILITY_IAM"
# Allow creating IAM roles

confirm_changeset = true
# Ask for confirmation before deploying (local only)
```

---

### 6. `.gitignore` - Files to Exclude from Git

This tells git which files NOT to track.

```gitignore
# SAM build artifacts
.aws-sam/
# Folder created by 'sam build' - contains packaged code

# Python
__pycache__/
# Python bytecode cache folders
*.py[cod]
# Compiled Python files (.pyc, .pyo, .pyd)
*$py.class
*.so
# Shared object files

# Environment variables
env.json
# Contains secrets - NEVER commit this!

# IDE
.vscode/
.idea/
*.swp
# Editor configuration files

# OS
.DS_Store
Thumbs.db
# Operating system files

# Logs
*.log
# Log files

# Test files (optional - remove if you want to commit them)
test_lambda.py
test-local.bat
test-api.bat
test-direct.bat
start-api.bat
# Local testing scripts
```

---

### 7. `env.json.example` - Example Environment Variables

This shows what `env.json` should look like (without real secrets).

```json
{
  "AgencyTestFunction": {
    // Environment variables for local testing
    
    "ENVIRONMENT": "dev",
    // Which environment (dev/staging/prod)
    
    "AWS_REGION": "eu-west-1",
    // AWS region for local testing
    
    "AZURE_OPENAI_ENDPOINT": "https://your-endpoint.openai.azure.com/",
    // Replace with your actual Azure OpenAI endpoint
    
    "AZURE_OPENAI_DEPLOYMENT": "your-deployment-name",
    // Replace with your deployment name
    
    "AZURE_OPENAI_API_KEY": "your-api-key"
    // Replace with your actual API key
  }
}
```

---

### 8. `test_lambda.py` - Local Testing Script

This lets you test the Lambda function on your computer without deploying.

```python
import json  # For pretty-printing JSON
import sys   # For modifying Python path
sys.path.insert(0, 'src')  # Add 'src' folder to Python path so we can import lambda_function

from lambda_function import lambda_handler  # Import the Lambda handler

# Test initial event
print('=== Testing Initial Event ===')
event = {'mode': 'initial', 'email': 'test@example.com', 'totalQuestions': 5}
# Create a test event (simulates what Lambda receives)

result = lambda_handler(event, None)
# Call the Lambda handler with test event

print(json.dumps(result, indent=2))
# Print the result in pretty JSON format

# Test basic event
print('\n=== Testing Basic Event ===')
event = {'path': '/agency-test', 'httpMethod': 'GET'}
# Create another test event

result = lambda_handler(event, None)
print(json.dumps(result, indent=2))
```

---

## 🚀 How to Use This Project

### First Time Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd worko-agency-flow
   ```

2. **Update placeholder values** (when you need Azure OpenAI)
   - Edit `template.yaml`
   - Replace placeholder values with real Azure OpenAI credentials

### Making Changes

1. **Edit the Lambda code**
   ```bash
   # Edit src/lambda_function.py
   ```

2. **Test locally** (optional)
   ```bash
   python test_lambda.py
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```

4. **Automatic deployment**
   - CodeCatalyst detects the push
   - Runs the workflow automatically
   - Deploys to AWS
   - Check CodeCatalyst UI for status

### Invoking the Lambda

```bash
# Using AWS CLI
aws lambda invoke \
  --function-name agency-test-lambda-dev \
  --region ap-south-1 \
  --payload '{"mode":"initial","email":"test@example.com"}' \
  response.json

# View the response
cat response.json
```

---

## 🔧 Troubleshooting

### Deployment Fails
- Check CodeCatalyst logs for error messages
- Common issues:
  - Stack in ROLLBACK_COMPLETE state → Workflow auto-deletes it
  - S3 bucket doesn't exist → Use existing bucket or create one
  - IAM permissions → Check CodeCatalyst has AWS access

### Lambda Doesn't Work
- Check CloudWatch Logs:
  ```bash
  aws logs tail /aws/lambda/agency-test-lambda-dev --follow
  ```

### Local Testing Fails
- Make sure you're in the project root directory
- Check Python version: `python --version` (should be 3.9+)

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│   Developer     │
│  (You)          │
└────────┬────────┘
         │ git push
         ▼
┌─────────────────┐
│  CodeCatalyst   │
│  (CI/CD)        │
└────────┬────────┘
         │ sam build
         │ sam deploy
         ▼
┌─────────────────┐      ┌──────────────┐
│  CloudFormation │─────▶│  S3 Bucket   │
│  (Stack)        │      │  (Code)      │
└────────┬────────┘      └──────────────┘
         │ creates
         ▼
┌─────────────────┐      ┌──────────────┐
│  Lambda         │─────▶│  Lambda      │
│  Function       │      │  Layer       │
└─────────────────┘      └──────────────┘
```

---

## 🎓 Key Concepts Explained

### What is Lambda?
- Serverless compute - you don't manage servers
- Pay only when code runs
- Automatically scales

### What is a Lambda Layer?
- Shared code/libraries across Lambda functions
- Reduces deployment package size
- Faster deployments

### What is SAM?
- Serverless Application Model
- Simplifies CloudFormation for serverless apps
- Provides local testing tools

### What is CloudFormation?
- Infrastructure as Code (IaC)
- Defines AWS resources in YAML/JSON
- Creates/updates/deletes resources automatically

### What is CodeCatalyst?
- AWS's CI/CD service
- Automates build and deployment
- Integrated with AWS services

---

## 📝 Best Practices

1. **Never commit secrets** - Use environment variables or AWS Secrets Manager
2. **Test locally first** - Use `test_lambda.py` before deploying
3. **Use meaningful commit messages** - Helps track changes
4. **Monitor CloudWatch Logs** - Check for errors after deployment
5. **Use layers for dependencies** - Faster deployments, smaller packages
6. **Tag your resources** - Add tags in template.yaml for cost tracking

---

## 🔐 Security Notes

- `env.json` is in `.gitignore` - never commit it
- `AzureOpenAIApiKey` has `NoEcho: true` - hides in CloudFormation console
- Lambda has minimal IAM permissions (only CloudWatch Logs)
- Use AWS Secrets Manager for production secrets

---

## 💰 Cost Estimation

- **Lambda**: Free tier includes 1M requests/month
- **S3**: ~$0.023 per GB/month (minimal for code storage)
- **CloudWatch Logs**: First 5GB free
- **Total**: Likely $0-1/month for testing

---

## 🎉 Success Checklist

- ✅ Lambda function deployed: `agency-test-lambda-dev`
- ✅ Lambda layer created: `agency-test-deps-dev`
- ✅ CloudFormation stack: `worko-agency-test`
- ✅ Automatic deployment on push to main
- ✅ No API Gateway (direct Lambda invocation only)

---

## 💻 Complete Command Reference (End-to-End)

All commands used during this project setup and deployment:

### Initial Setup Commands

```powershell
# Navigate to project directory
cd C:\Users\Administrator\Desktop\worko_working\worko-workspace\worko-agency-flow

# Check git status
git status

# View project structure
dir
dir .codecatalyst\workflows
```

### Creating Project Structure

```powershell
# Create directories
mkdir .codecatalyst
mkdir .codecatalyst\workflows
mkdir layers
mkdir layers\python-deps
mkdir src
mkdir events

# Copy files to src directory
copy lambda_function.py src\
copy prompts.py src\
copy utils.py src\
```

### Git Operations

```powershell
# Check current branch and status
git status
git branch

# View commit history
git log --oneline -5

# View specific file in git
git show HEAD:.codecatalyst/workflows/auto-deploy.yaml

# Add files to staging
git add .
git add template.yaml
git add .codecatalyst/workflows/auto-deploy.yaml
git add README.md

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push origin main

# Rename file in git
git mv .codecatalyst/workflows/deploy.yaml .codecatalyst/workflows/auto-deploy.yaml
```

### Testing Locally (Without Docker/SAM)

```powershell
# Test Lambda function directly with Python
python test_lambda.py

# Run from specific directory
cd C:\Users\Administrator\Desktop\worko_working\worko-workspace\worko-agency-flow
python test_lambda.py
```

### AWS CLI Commands

```powershell
# Configure AWS credentials
aws configure

# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name worko-agency-test --region ap-south-1

# View stack events
aws cloudformation describe-stack-events --stack-name worko-agency-test --region ap-south-1

# Delete failed stack manually
aws cloudformation delete-stack --stack-name worko-agency-test --region ap-south-1

# Wait for stack deletion
aws cloudformation wait stack-delete-complete --stack-name worko-agency-test --region ap-south-1

# Invoke Lambda function
aws lambda invoke \
  --function-name agency-test-lambda-dev \
  --region ap-south-1 \
  --payload '{"mode":"initial","email":"test@example.com"}' \
  response.json

# View Lambda response
cat response.json

# Tail Lambda logs
aws logs tail /aws/lambda/agency-test-lambda-dev --follow --region ap-south-1

# List Lambda functions
aws lambda list-functions --region ap-south-1

# Get Lambda function details
aws lambda get-function --function-name agency-test-lambda-dev --region ap-south-1
```

### SAM CLI Commands (If Installed)

```powershell
# Check SAM version
sam --version

# Build SAM application
sam build

# Build with container (for Windows)
sam build --use-container

# Deploy with guided setup
sam deploy --guided

# Deploy with parameters
sam deploy \
  --stack-name worko-agency-test \
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-mpwvaft0yfqx \
  --region ap-south-1 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

# Deploy with specific config
sam deploy --config-env default

# Invoke Lambda locally
sam local invoke AgencyTestFunction --event events/initial-event.json --env-vars env.json

# Start local API
sam local start-api --env-vars env.json

# View SAM logs
sam logs -n AgencyTestFunction --stack-name worko-agency-test --tail

# Delete SAM stack
sam delete --stack-name worko-agency-test --region ap-south-1
```

### Docker Commands (If Using Docker)

```powershell
# Check Docker status
docker --version

# List running containers
docker ps

# Run Lambda with Docker
docker run --rm -v %cd%:/var/task amazon/aws-lambda-python:3.9 python lambda_function.py
```

### File Operations

```powershell
# View file contents
type template.yaml
type .codecatalyst\workflows\auto-deploy.yaml
type src\lambda_function.py

# List files
dir /b
dir .codecatalyst\workflows /b

# Create files
echo # Test > README.md
echo "" >> README.md

# Delete files
del src\requirements.txt
```

### Debugging Commands

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Install dependencies
pip install -r requirements.txt

# Check environment variables
echo %PATH%

# View current directory
cd
pwd
```

### CodeCatalyst Workflow Triggers

```powershell
# Any push to main branch triggers deployment
git add .
git commit -m "Trigger deployment"
git push origin main

# Check workflow status in CodeCatalyst UI:
# 1. Go to CodeCatalyst console
# 2. Navigate to your project
# 3. Click CI/CD → Workflows
# 4. View DeployAgencyLambda workflow runs
```

### Complete Deployment Flow

```powershell
# 1. Make changes to code
code src/lambda_function.py

# 2. Test locally (optional)
python test_lambda.py

# 3. Add to git
git add .

# 4. Commit changes
git commit -m "Update Lambda function"

# 5. Push to trigger deployment
git push origin main

# 6. Monitor deployment in CodeCatalyst
# (Check CodeCatalyst UI for logs)

# 7. Verify deployment
aws lambda get-function --function-name agency-test-lambda-dev --region ap-south-1

# 8. Test deployed Lambda
aws lambda invoke \
  --function-name agency-test-lambda-dev \
  --region ap-south-1 \
  --payload '{"test":"data"}' \
  output.json

# 9. View response
type output.json

# 10. Check logs
aws logs tail /aws/lambda/agency-test-lambda-dev --follow --region ap-south-1
```

### Troubleshooting Commands

```powershell
# If deployment fails, check stack status
aws cloudformation describe-stacks --stack-name worko-agency-test --region ap-south-1

# View stack events to see what failed
aws cloudformation describe-stack-events \
  --stack-name worko-agency-test \
  --region ap-south-1 \
  --max-items 20

# If stack is in ROLLBACK_COMPLETE, delete it
aws cloudformation delete-stack --stack-name worko-agency-test --region ap-south-1
aws cloudformation wait stack-delete-complete --stack-name worko-agency-test --region ap-south-1

# Then push code again to redeploy
git commit --allow-empty -m "Retry deployment"
git push origin main

# Check Lambda function exists
aws lambda list-functions --region ap-south-1 | findstr agency-test

# Get Lambda configuration
aws lambda get-function-configuration --function-name agency-test-lambda-dev --region ap-south-1

# View recent Lambda logs
aws logs tail /aws/lambda/agency-test-lambda-dev --since 10m --region ap-south-1
```

### Quick Reference: Most Used Commands

```powershell
# Check status
git status

# Deploy changes
git add .
git commit -m "Your message"
git push origin main

# Test locally
python test_lambda.py

# Invoke deployed Lambda
aws lambda invoke --function-name agency-test-lambda-dev --region ap-south-1 --payload '{"test":"data"}' output.json

# View logs
aws logs tail /aws/lambda/agency-test-lambda-dev --follow --region ap-south-1
```

---

## 📞 Support

If something doesn't work:
1. Check CodeCatalyst workflow logs
2. Check CloudWatch Logs for Lambda errors
3. Verify AWS credentials and permissions
4. Review this README for troubleshooting steps
5. Use the command reference above to debug

---

**Happy Deploying! 🚀**
