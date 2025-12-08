import json
import boto3
import re
import os
from datetime import datetime
from decimal import Decimal
import time
start_time = time.time()
from botocore.exceptions import ClientError

# Initialize Bedrock clients
# region = 'ap-south-1'
# region = 'us-east-1'
region =  'us-east-1'
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client(service_name='bedrock', region_name = region)
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name = region)

import json
import requests
import google.auth.transport.requests
from google.oauth2 import service_account

def get_secret(self, secret_name):
    """
    Retrieve individual secrets from AWS Secrets Manager using the get_secret_value API.
    This function assumes the stack mentioned in the source code README has been successfully deployed.
    This stack includes 7 secrets, all of which have names beginning with "mySecret".

    :param secret_name: The name of the secret fetched.
    :type secret_name: str
    """
    try:
        get_secret_value_response = self.client.get_secret_value(
            SecretId=secret_name
        )
        # logging.info("Secret retrieved successfully.")
        return get_secret_value_response["SecretString"]
    except self.client.exceptions.ResourceNotFoundException:
        msg = f"The requested secret {secret_name} was not found."
        # logger.info(msg)
        return msg
    except Exception as e:
        # logger.error(f"An unknown error occurred: {str(e)}.")
        raise

def call_GCP_models(prompt, want_json = True,max_try_for_json=3):
    # 1. Service account JSON path
    # SERVICE_ACCOUNT_FILE = r"C:\Users\Administrator\Desktop\worko_working\worko_code_chainged_files\vertex-sa.json"

    # 2. Load and refresh credentials
    # credentials = service_account.Credentials.from_service_account_file(
    #     service_account_info,
    #     scopes=["https://www.googleapis.com/auth/cloud-platform"]
    # )


    service_account_info = get_secret("GCP-secrect")

    credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())

    # 3. Prepare API endpoint
    project_id = "worko-dev"
    location = "us-central1"
    model_name = "gemini-2.5-flash"

    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:generateContent"

    # 4. Prepare headers and payload
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

def invoke_model(prompt):
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10000,
            "temperature": 0.3,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
        })

        modelId = "arn:aws:bedrock:us-east-1:211125353899:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"

        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=modelId,
            accept='*/*',
            contentType='application/json'
        )

        # Parse the Bedrock envelope
        model_output = json.loads(response['body'].read())
        llm_text = model_output.get("content", [{}])[0].get("text", "").strip()

        if not llm_text:
            raise ValueError("Model returned empty text.")

        # Extract JSON from code block if present
        json_match = re.search(r'```json\s*(.*?)\s*```', llm_text, re.DOTALL)
        json_str = json_match.group(1).strip() if json_match else llm_text.strip()

        if not json_str:
            raise ValueError("No JSON found in model output.")

        # Clean control chars
        json_str = re.sub(r'[\x00-\x1F\x7F]', '', json_str)

        return json.loads(json_str)

    except Exception as e:
        print("Unexpected error:", str(e))
        return {"error": f"Unexpected error: {str(e)}"}

def lambda_handler(event, context):
    print(event)

    job_desc = event.get('JOB_DESC', "")
    job_desc = re.sub(r'[\x00-\x1F\x7F]', '', job_desc)  # Remove control characters
    job_desc = re.sub(r'<[^>]+>', '', job_desc)  # Remove HTML tags
    job_desc = re.sub(r'&nbsp;', ' ', job_desc)  # Replace HTML space entity with a space
    job_desc = re.sub(r'\s+', ' ', job_desc).strip()  # Normalize spaces and trim

    print ("Job description",job_desc)
    end_time = time.time()

    print(f"step 1 received and preporcessede the job description time took :- {end_time-start_time}")

    prompt = (
    f"**JOB DESCRIPTION EXTRACTION TASK**\n\n"
    
    f"**STEP 1 - Extract Basic Information:**\n"
    f"- Job Title\n"
    f"- Salary Range (Minimum and Maximum)\n"
    f"- Experience Range (Minimum and Maximum)\n"
    f"- Number of Openings\n"
    f"- Work Mode (WFH, WFO, HYBRID)\n"
    f"- Location\n"
    f"- Notice Period (Days)(Enter a numeric value. If a range is provided, use the higher value.)\n"
    f"- Type of Employment\n"
    f"- Department\n"
    f"- Core Skills (Each skill must be a maximum of 30 characters)\n"
    f"- Soft Skills (Each skill must be a maximum of 30 characters)\n"
    f"- Technical Skills (Include only IT skills as Technical Skill. Each skill must be a maximum of 30 characters)\n"
    f"- Good to Have Skills (Each skill must be a maximum of 30 characters)\n"
    f"- Must Have Skills (These are skills explicitly mentioned as 'must have' in the job description. Each skill must be a maximum of 30 characters)\n"
    f"- Mandatory Requirements (Identify all MANDATORY requirements in the job description - look for terms like \"required,\" \"must have,\" \"X years in [specific industry]\")\n"
    f"- Preferred Requirements (Identify all PREFERRED/NON-MANDATORY experience requirements - look for terms like \"preferred,\" \"nice to have,\" \"desirable\")\n\n"

    f"**STEP 2 - CRITICAL SKILL CLASSIFICATION RULES:**\n"
    f"**CORE SKILLS = Functional/Domain Expertise ONLY**\n"
    f"-INCLUDE in coreSkills: Specific job functions, domain knowledge, industry expertise\n"
    f"-Examples: 'Category Management', 'Supplier Relations', 'E-commerce Operations', 'Revenue Management', 'Market Research'\n"
    f"-EXCLUDE from coreSkills: Management abilities, thinking skills, interpersonal skills\n"
    f"-Examples: 'Team Leadership', 'Strategic Planning', 'Goal Setting', 'Performance Management', 'Stakeholder Management'\n\n"
    
    f"**SOFT SKILLS = Behavioral/Interpersonal Abilities**\n"
    f"-INCLUDE in softSkills: How you work, think, and interact\n"
    f"-Examples: 'Leadership', 'Communication', 'Strategic Thinking', 'Problem Solving', 'Team Management', 'Decision Making'\n\n"
    
    f"**TECHNICAL SKILLS = Tools/Software/Platforms**\n"
    f"INCLUDE in technicalSkills: Specific tools, software, platforms, systems\n"
    f"Examples: 'Microsoft Excel', 'CRM Systems', 'Analytics Tools', 'Database Management'\n\n"
    
    f"**MANDATORY SKILL MOVEMENT RULES:**\n"
    f"- 'Team Leadership' → softSkills (NOT coreSkills)\n"
    f"- 'Strategic Planning' → softSkills (NOT coreSkills)\n"
    f"- 'Stakeholder Management' → softSkills (NOT coreSkills)\n"
    f"- 'Goal Setting' → softSkills (NOT coreSkills)\n"
    f"- 'Performance Management' → softSkills (NOT coreSkills)\n"
    f"- 'Data Analysis' → technicalSkills if tool-based, softSkills if analytical thinking\n"
    f"- 'Process Development' → softSkills (NOT coreSkills)\n"
    f"- 'Problem Resolution' → softSkills (NOT coreSkills)\n"
    f"- 'Business Development' → coreSkills (NOT softSkills)\n"
    f"- 'Financial Analysis' → coreSkills (NOT technicalSkills)\n"
    f"- 'Market Research' → coreSkills (NOT softSkills)\n"
    f"- 'Sales Strategy' → coreSkills (NOT softSkills)\n"
    f"- 'Programming Languages (Python, Java, etc.)' → technicalSkills (NOT coreSkills)\n"
    f"- 'Cloud Platforms (AWS, Azure, GCP)' → technicalSkills (NOT coreSkills)\n"
    f"- 'Version Control (Git, SVN)' → technicalSkills (NOT coreSkills)\n"
    f"- 'Database Design/SQL' → technicalSkills (NOT coreSkills)\n"
    f"- 'Project Management' → softSkills (NOT coreSkills)\n"
    f"- 'Communication Skills' → softSkills (NEVER coreSkills or technicalSkills)\n"
    f"- 'Excel/Power BI/Visualization Tools' → technicalSkills (NOT coreSkills)\n"
    f"- 'Customer Relationship Management (CRM)' → technicalSkills (NOT coreSkills)\n\n"
    
    f"**STEP 3 - MANDATORY vs PREFERRED REQUIREMENTS:**\n"
    f"**Mandatory Requirements:** Look for exact phrases:\n"
    f"- 'Required', 'Must have', 'Necessary', 'Essential'\n"
    f"- Items under 'Requirements', 'Mandatory Requirements', 'Essential Criteria'\n"
    f"- Education requirements (BE/B.Tech Graduate)\n"
    f"- Experience requirements with specific years\n\n"
    
    f"**Preferred Requirements:** Look for exact phrases:\n"
    f"- 'Preferred', 'Nice to have', 'Desirable', 'Good to have'\n"
    f"- Items under 'Preferred Qualifications', 'Additional Skills'\n"
    f"- 'Experience with X is an added advantage'\n\n"
    
    f"**STEP 4 - MUST HAVE vs GOOD TO HAVE SKILLS:**\n"
    f"- mustHaveSkills: Extract skills from mandatory requirements\n"
    f"- goodToHaveSkills: Extract skills from preferred requirements\n\n"
    
    f"**STEP 5 - FINAL VALIDATION (CRITICAL):**\n"
    f"Before generating JSON, perform these checks:\n"
    f"1. Scan coreSkills - remove ANY management/leadership/planning skills\n"
    f"2. Move removed skills to softSkills\n"
    f"3. Check for duplicates across all skill arrays - remove duplicates\n"
    f"4. Ensure each skill is in ONLY ONE category\n"
    f"5. Verify coreSkills contains ONLY functional/domain expertise\n"
    f"6. keep only 20 most relavant skills with respect to job description in each catagory of skills\n"
    f"7. for Salary Range and Experience Range if min is given but max is not then don't put any value in max if both are not given do not return this entire field\n"
    f"8. Remove any redundaundt or repeating data\n\n"
    
    f"**EMPTY FIELD RULE:**\n"
    f"- If information is not explicitly mentioned, leave field empty (not 'Not Mentioned')\n\n"
    
    f"**PROCESSING THE JOB DESCRIPTION:**\n"
    f"Now analyze this job description step by step:\n\n"
    f"{job_desc}\n\n"
    
    f"**OUTPUT FORMAT:**\n"
    f"Return ONLY the JSON structure below with extracted values:\n\n"
    '{\n'
    '    "jobTitle": "",\n'
    '    "salaryRange": {"min": "", "max": ""},\n'
    '    "experienceRange": {"min": "", "max": ""},\n'
    '    "numberOfOpenings": "",\n'
    '    "workMode": "",\n'
    '    "location": "",\n'
    '    "noticePeriod": "",\n'
    '    "typeOfEmployment": "",\n'
    '    "department": "",\n'
    '    "coreSkills": [],\n'
    '    "softSkills": [],\n'
    '    "technicalSkills": [],\n'
    '    "goodToHaveSkills": [],\n'
    '    "mustHaveSkills": [],\n'
    '    "mandatoryRequirements": [],\n'
    '    "preferredRequirements": [],\n'
    '    "formattedHTML":  "<div>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Company Overview</h2>\\n"\n'
            '        "<p>[Company information from job description]</p>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Role Overview</h2>\\n"\n'
            '        "<p>[Role information from job description]</p>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Key Responsibilities</h2>\\n"\n'
            '        "<ul>\\n"\n'
            '        "[List of responsibilities from job description]\\n"\n'
            '        "</ul>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Requirements</h2>\\n"\n'
            '        "<ul>\\n"\n'
            '        "[List of requirements from job description]\\n"\n'
            '        "</ul>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Mandatory Requirements</h2>\\n"\n'
            '        "<ul>\\n"\n'
            '        "[List of mandatory requirements from job description]\\n"\n'
            '        "</ul>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Preferred Requirements</h2>\\n"\n'
            '        "<ul>\\n"\n'
            '        "[List of preferred requirements from job description]\\n"\n'
            '        "</ul>\\n"\n'
            '        "</section>\\n"\n'
            '        "<section>\\n"\n'
            '        "<h2>Additional Information</h2>\\n"\n'
            '        "<p>[Additional details from job description]</p>\\n"\n'
            '        "</section>\\n"\n'
            '        "</div>"\n'
            '}'
    
        )

    # response = invoke_model(prompt)
    response =  call_GCP_models(prompt)
    end_time = time.time()
    print(f"step 2 invoked ai and got response time took :- {end_time-start_time}")

    print("Response 2:", response)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)  # Convert the dictionary to a JSON string
    }