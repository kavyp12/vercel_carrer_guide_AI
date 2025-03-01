// E:\carrrer_guide_vercel_main_demo\api\downloadReport.js
const { verifyToken } = require('./middleware/authMiddleware.js'); // Adjust path if needed
const { GoogleAuth } = require('google-auth-library');
const { google } = require('googleapis');
const { connectDB } = require('./db.js'); // Adjust path if needed

module.exports = async (req, res) => {
  try {
    await connectDB(); // Connect to MongoDB if needed

    // Handle GET request for /api/download-report/<filename>
    if (req.method === 'GET' && req.url.startsWith('/api/download-report/')) {
      // Verify the token first
      verifyToken(req, res, async () => {
        const userId = req.user?.userId;

        if (!userId) {
          return res.status(401).json({ message: 'Unauthorized: No user ID found' });
        }

        // Extract the filename from the URL
        const pathParts = req.url.split('/');
        const filename = decodeURIComponent(pathParts[pathParts.length - 1]);

        if (!filename) {
          return res.status(400).json({ message: 'Invalid filename' });
        }

        // Initialize Google Drive API with service account credentials
        const credentials = JSON.parse(process.env.GOOGLE_DRIVE_CREDENTIALS || '{}');
        if (!credentials || !credentials.private_key) {
          console.error('Missing or invalid GOOGLE_DRIVE_CREDENTIALS');
          return res.status(500).json({ message: 'Missing or invalid Google Drive credentials' });
        }

        // Log the credentials for debugging (redact sensitive parts if needed)
        console.info(`Loading Google Drive credentials: ${JSON.stringify(credentials).substring(0, 20)}... (redacted)`);

        try {
          const auth = new GoogleAuth({
            credentials,
            scopes: ['https://www.googleapis.com/auth/drive.file'],
          });

          const drive = google.drive({ version: 'v3', auth });

          // Search for the file by name
          const response = await drive.files.list({
            q: `name='${filename}' and trashed=false`,
            spaces: 'drive',
            fields: 'files(id, name, mimeType)',
          });

          const files = response.data.files || [];
          if (!files.length) {
            return res.status(404).json({ message: 'File not found' });
          }

          const file = files[0];
          const fileId = file.id;
          const mimeType = file.mimeType || 'application/pdf';

          // Download the file
          const fileContent = await drive.files.get(
            { fileId, alt: 'media' },
            { responseType: 'stream' }
          );

          // Stream the file content to the response
          res.setHeader('Content-Type', mimeType);
          res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);

          fileContent.data
            .on('end', () => {
              console.log(`File downloaded successfully from Google Drive: ${filename}`);
            })
            .on('error', (err) => {
              console.error(`Failed to download file from Google Drive: ${err.message}`);
              return res.status(500).json({ message: 'Failed to download file' });
            })
            .pipe(res);
        } catch (authError) {
          console.error(`Google Drive authentication error: ${authError.message}`, authError);
          return res.status(500).json({ message: 'Failed to authenticate with Google Drive' });
        }

        return;
      });
      return;
    }

    // Handle 404 for other routes
    res.status(404).json({ error: 'Route not found' });
  } catch (error) {
    console.error('Download report route error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};