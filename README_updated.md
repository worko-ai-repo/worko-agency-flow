# Worko AI Lambda - Intelligent Processing Function

## 📖 The Complete Story: From Zero to Automated Deployment

This project is an AI-powered AWS Lambda function that automatically deploys to AWS whenever you push code to the `main` branch. Let me walk you through everything we learned and how it all works together.

---

## 🎯 What This Project Does

This is an **AI Lambda function** that:
- Runs on AWS Lambda (serverless compute)
- Uses Python 3.10 runtime for AI/ML processing
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
worko-ai-lambda/
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

## 🚀 How to Use This Project

### First Time Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd worko-ai-lambda
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
  --function-name worko-ai-lambda-dev \
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
  aws logs tail /aws/lambda/worko-ai-lambda-dev --follow
  ```

### Local Testing Fails
- Make sure you're in the project root directory
- Check Python version: `python --version` (should be 3.10+)

---

## 🎉 Success Checklist

- ✅ Lambda function deployed: `worko-ai-lambda-dev`
- ✅ Lambda layer created: `worko-ai-lambda-deps-dev`
- ✅ CloudFormation stack: `worko-ai-lambda-test`
- ✅ Automatic deployment on push to main
- ✅ No API Gateway (direct Lambda invocation only)

---

## 💻 Quick Reference: Most Used Commands

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
aws lambda invoke --function-name worko-ai-lambda-dev --region ap-south-1 --payload '{"test":"data"}' output.json

# View logs
aws logs tail /aws/lambda/worko-ai-lambda-dev --follow --region ap-south-1
```

---

## 📞 Support

If something doesn't work:
1. Check CodeCatalyst workflow logs
2. Check CloudWatch Logs for Lambda errors
3. Verify AWS credentials and permissions
4. Review this README for troubleshooting steps

---

**Happy Deploying! 🚀**