import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging to display output in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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

# Call the function and test it
if __name__ == "__main__":
    drive_service = setup_google_drive()
    if drive_service:
        logger.info("Drive service is set up successfully!")
    else:
        logger.error("Failed to set up Drive service.")