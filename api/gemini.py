# api/gemini.py
from http.server import BaseHTTPRequestHandler
import json
import logging
import os
from dotenv import load_dotenv
from .assessment_manager import AssessmentManager
from .prompt_manager import extract_career_goal, generate_topic_reports
from .gemini_client import setup_gemini_api
from .report_builder import build_report_data
from .pdf_generator import generate_pdf_report
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload
from io import BytesIO
import re
from urllib.parse import unquote

# Load environment variables from .env file
load_dotenv()

# Configure logging for Vercel deployment
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Initialize the assessment manager for processing answers
assessment_manager = AssessmentManager()

# Configure and initialize the Gemini API on startup
try:
    setup_gemini_api()
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {str(e)}")
    raise

def setup_google_drive():
    try:
        credentials_info = {
            "type": "service_account",
            "project_id": "my-project-2454-414517",
            "private_key_id": "a58d63a721929ca634f4ef69207067bb978a02c2",
            "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCDM+Jqbj6FOnWn
4zugTyjPqAmSBbYEnf50B5rAgzzAoTkKkg9lNWiUu6OAgyaLbtEk9nIN8Ek0YAR/
o/UdX+B1pqFb80X28pE3T71AlXX4W81KdqOUKoJsp1GysSdLvuXrB5snw6mTVvbW
3qOijyqT/zchI4GBzKZKh1xG+gyqQLtuLAdxHJuPmv+Vb6AAX66UnRK0Z6dXDXzM
aemjtJ4v5zd+8UqB4RSGqqvqxQKxo2JMQKYJsa1acGchIlM5W8Po+pkw6mXf/tbK
v/rchATY2x3OOjD6MVy8+KxmklFgfAA1hUc8lHD3L4xxK9968G2JQtbgOI1qrhh5
qHMTFJxzAgMBAAECggEAAQ5uOJcnT7ahyIvu001FMdl+LOZ43wlP9CqKLMShvOyk
uJi7y6p7a2nQrjHgIefu19JYJr6UMvoW7y7TGWfH4d/z6qPxy0Q2tnBLlh/d8aBO
Qyw4svJeAcvzFMeSXmzCDdC43MAZjG3QfPhmmYzM4KDXFnWNDw4mb0aEZVnmt4mH
mp9/Fus5OohVY6TdnWKnLhQgeLBzZZjkvGM6j5snWtbrtUS37r4fC97YeVOEpIC/
stsIj+HYk/iEV/k4iBUPi9FGaZ/yYphjFRe3qt8zKtAvy48VwB9KZ2rDcXvhJpNQ
u4DOvnwCo73QsFuNQw3WP3KpByLJGl9Nn13RQTeQIQKBgQC3bRrxmQpOfqUQ39RP
0m18II2MPlFLP2ifmUr0fljEBZ0KJJUscIO7isBrnWjJop1v1zFDa7gUKi5SwKe5
rwf7azcZQYQnHOim3oZUHjAI/GDJTuqFKk7pKfOC2DMRGGz6abSVwZJGXptXhQ0n
dajPNjRJwq9/AuXAc2vupVOwAwKBgQC3HSgwU3jrqyD8yi7WH0LxkqNkbY3T5vzW
wZyjPCNFEHFe6KBtP22fLHuhaVdi7vmPB95X/A8LnLmZO6ge+PqIgopNNEdaJyOa
v11YgmUbY9N3ERPY1LdXQPKh6o59B06XG3Eo2T9lvlywtvWqTdfi6qGlT29jjemp
CzKsrgtO0QKBgHguaIT7vSEJIaYYwcc7HLlDqvrEqgcfmLFZgx8G2ao181r99S+U
2Ps8Qi9Ah7P1dCofWQvPvGCZ8pgN2tdys0wsR4Gox6nI6zbKfkEHNnnswo2jw01V
Fzb2YbLNbUg6NM0uDUBCAFFTE30YlDHSibSa00+w28PgZiDef01xzY95AoGAHk3m
/shxtJ7noK5dPfaCf7RC8jXnSPBrW6dDIwiq1Z05Bfn9wtbCb5tPApGKcscV6gPl
Wi5O1x8i4CctVaLi44CnHsvOGy9rBwswiZta3EOTFZtv62yYwwnunblRx4NUEFHs
UlRR16a/dEdzNLIZTmaCRfd1ecZcqys9QbK0EGECgYEAnW0T9OCIaNnAWhGQM3GX
Cyn+L70YAjMmZFUcHUscIwHBOqy6CDGaAvco9Bu/x9YtaIH8aC5xq4Gl8h0QLHqY
y94UTT8WCNi8/bQweMrsYmPKPSSeWasvM+vE/yvQKWyVI+hmJPJE5yz2vR9tpN6u
AzX5gOBIjP3hV5Kfze2ybnw=
-----END PRIVATE KEY-----""",
            "client_email": "new-carrer-guide@my-project-2454-414517.iam.gserviceaccount.com",
            "client_id": "103543992193957982622",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/new-carrer-guide%40my-project-2454-414517.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        drive_service = build('drive', 'v3', credentials=credentials)
        logger.info("Google Drive API initialized successfully")
        return drive_service
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive API: {str(e)}", exc_info=True)
        return None

def upload_to_drive(drive_service, file_content, filename, folder_id=None):
    """Upload a PDF file to Google Drive and return its shareable link."""
    try:
        # Define file metadata
        file_metadata = {
            'name': filename,
            'mimeType': 'application/pdf'
        }
        
        # Optionally add the folder ID if specified
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Create media upload object with raw bytes from BytesIO
        media = MediaInMemoryUpload(file_content.getvalue(), mimetype='application/pdf')
        
        # Upload the file to Google Drive
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        # Make the file publicly accessible via a shareable link
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        logger.info(f"File uploaded successfully: {filename}")
        return {
            'id': file.get('id'),
            'webViewLink': file.get('webViewLink')
        }
    except Exception as e:
        logger.error(f"Failed to upload file to Google Drive: {str(e)}", exc_info=True)
        return None

def download_from_drive(drive_service, filename):
    """
    Download a file from Google Drive by its filename and return file content.
    
    Args:
        drive_service: Google Drive API service
        filename: The name of the file to download
        
    Returns:
        Tuple of (file_content, mime_type) or (None, None) if not found
    """
    try:
        # Search for the file by name (case-insensitive for robustness, but exact match for simplicity)
        response = drive_service.files().list(
            q=f"name='{filename}' and trashed=false",
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()
        
        files = response.get('files', [])
        if not files:
            logger.error(f"File not found in Google Drive: {filename}")
            return None, None
            
        # Get the first matching file
        file_id = files[0]['id']
        mime_type = files[0]['mimeType']
        
        # Download the file content
        request = drive_service.files().get_media(fileId=file_id)
        file_content = BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        file_content.seek(0)
        logger.info(f"File downloaded successfully from Google Drive: {filename}")
        return file_content, mime_type
    except Exception as e:
        logger.error(f"Failed to download file from Google Drive: {str(e)}", exc_info=True)
        return None, None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle /api/submit-assessment (POST) endpoint for submitting assessments and generating reports."""
        if self.path != '/api/submit-assessment':
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Route not found"}).encode())
            return

        try:
            # Read and parse the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Validate input data
            if not data or 'answers' not in data:
                return self._send_error(400, "Missing answers data")
            
            if not isinstance(data['answers'], dict):
                return self._send_error(400, "Invalid answers format")
            
            # Process assessment data
            trait_scores = assessment_manager.calculate_scores(data['answers'])
            
            # Extract student details
            student_name = data.get('studentName', 'Student').strip()
            student_info = {
                'name': student_name,
                'age': str(data.get('age', 'Not provided')),
                'academic_info': str(data.get('academicInfo', 'Not provided')),
                'interests': str(data.get('interests', 'Not provided')),
                'achievements': [
                    str(data.get('answers', {}).get('question13', 'None')),
                    str(data.get('answers', {}).get('question30', 'None'))
                ]
            }
            
            # Extract career goal from answers
            career_goal = extract_career_goal(list(data['answers'].values()))
            if not career_goal:
                return self._send_error(500, "Failed to extract career goal")
            
            # Generate report sections using Gemini API
            context = f"""
            Trait Scores: {json.dumps(trait_scores)}
            Student Info: {json.dumps(student_info)}
            """
            report_sections = generate_topic_reports(context.strip(), career_goal, student_info['name'])
            
            if not report_sections:
                return self._send_error(500, "Failed to generate report sections")
            
            # Build the final report data
            report_data = build_report_data(student_info['name'], career_goal, report_sections)

            # Generate PDF report (returns bytes)
            pdf_filename = f"{student_name.replace(' ', '_')}_Career_Report.pdf"
            pdf_content = generate_pdf_report(report_data)  # Already returns bytes

            # Initialize Google Drive client
            drive_service = setup_google_drive()
            if not drive_service:
                return self._send_error(500, "Failed to initialize Google Drive API")
            
            # Get the Google Drive folder ID from environment variables
            folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
            
            # Upload PDF to Google Drive
            upload_result = upload_to_drive(drive_service, BytesIO(pdf_content), pdf_filename, folder_id)
            
            if not upload_result:
                return self._send_error(500, "Failed to upload PDF to Google Drive")

            # Send success response with report details
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Report generated successfully",
                "report_url": upload_result['webViewLink'],
                "file_id": upload_result['id'],
                "file_name": pdf_filename, 
                "student_name": student_name,
                "career_goal": career_goal
            }).encode())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON data")
        except Exception as e:
            logger.error(f"Assessment submission error: {str(e)}", exc_info=True)
            self._send_error(500, f"Assessment processing failed: {str(e)}")

    def do_GET(self):
        """Handle GET endpoints including the download-report endpoint."""
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "message": "Career Guide API is running"
            }).encode())
            return
        
        # Handle file download endpoint
        if self.path.startswith('/api/download-report/'):
            try:
                # Parse the filename from the path
                match = re.match(r'/api/download-report/(.*)', self.path)
                if not match:
                    return self._send_error(400, "Invalid file path")
                
                filename = unquote(match.group(1))
                
                # Check authorization header (optional but recommended)
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return self._send_error(401, "Authorization required")
                
                # Initialize Google Drive API
                drive_service = setup_google_drive()
                if not drive_service:
                    return self._send_error(500, "Failed to connect to Google Drive")
                
                # Download the file from Google Drive
                file_content, mime_type = download_from_drive(drive_service, filename)
                
                if not file_content:
                    return self._send_error(404, "File not found")
                
                # Send the file content as response
                self.send_response(200)
                self.send_header('Content-type', mime_type or 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                self.wfile.write(file_content.getvalue())
                
                return
            except Exception as e:
                logger.error(f"File download error: {str(e)}", exc_info=True)
                return self._send_error(500, f"Failed to download file: {str(e)}")

        # Handle 404 for other routes
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Route not found"}).encode())

    def _send_error(self, status, message):
        """Helper method to send error responses in JSON format."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
        return False

# Ensure Gemini API is initialized on Vercel cold start
try:
    setup_gemini_api()
except Exception as e:
    logger.error(f"Failed to initialize Gemini API on Vercel: {str(e)}")
    raise