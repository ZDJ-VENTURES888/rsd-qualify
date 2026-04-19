// ─────────────────────────────────────────────────────────────
//  RSD Qualify — Google Drive Integration
//  Saves the HTML report into a per-prospect folder inside
//  the "RSD Qualifications" parent folder on Drive.
//
//  Setup:
//    1. Create a Google Cloud project
//    2. Enable the Google Drive API
//    3. Create a Service Account + download JSON key
//    4. Add GOOGLE_CLIENT_EMAIL + GOOGLE_PRIVATE_KEY to .env
//    5. Create "RSD Qualifications" folder in Drive
//    6. Share it with the service account email (Editor)
//    7. Paste the folder ID into GOOGLE_DRIVE_PARENT_FOLDER_ID in .env
// ─────────────────────────────────────────────────────────────

const { google } = require('googleapis');
const { Readable } = require('stream');

function getAuth() {
  return new google.auth.JWT(
    process.env.GOOGLE_CLIENT_EMAIL,
    null,
    // Newlines in env vars are stored as \n — replace back
    (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
    ['https://www.googleapis.com/auth/drive']
  );
}

/**
 * Creates a subfolder inside the parent "RSD Qualifications" folder.
 * Folder name format: "FirstName LastName — BusinessName — Apr 19 2026"
 */
async function createProspectFolder(drive, name) {
  const parentId = process.env.GOOGLE_DRIVE_PARENT_FOLDER_ID;
  const res = await drive.files.create({
    requestBody: {
      name,
      mimeType: 'application/vnd.google-apps.folder',
      parents: [parentId],
    },
    fields: 'id',
  });
  return res.data.id;
}

/**
 * Uploads the HTML report string as a .html file to a Drive folder.
 * Returns a shareable view link.
 */
async function uploadReport(htmlContent, fileName, folderId, drive) {
  const stream = Readable.from([htmlContent]);
  const res = await drive.files.create({
    requestBody: {
      name: fileName,
      mimeType: 'text/html',
      parents: [folderId],
    },
    media: {
      mimeType: 'text/html',
      body: stream,
    },
    fields: 'id, webViewLink',
  });

  // Make the file readable by anyone with the link
  await drive.permissions.create({
    fileId: res.data.id,
    requestBody: { role: 'reader', type: 'anyone' },
  });

  return res.data.webViewLink;
}

/**
 * Main export: saves report to Drive, returns the file link.
 * Returns null on failure (non-blocking — form still submits to GHL).
 */
async function saveReportToDrive(htmlContent, contact) {
  if (!process.env.GOOGLE_CLIENT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY || !process.env.GOOGLE_DRIVE_PARENT_FOLDER_ID) {
    console.warn('[Drive] Env vars not set — skipping Drive upload.');
    return null;
  }

  try {
    const auth  = getAuth();
    const drive = google.drive({ version: 'v3', auth });

    const now       = new Date();
    const dateLabel = now.toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' });
    const fullName  = `${contact.firstName || ''} ${contact.lastName || ''}`.trim() || 'Unknown';
    const bizName   = contact.businessName || 'No Business Name';

    const folderName = `${fullName} — ${bizName} — ${dateLabel}`;
    const fileName   = `RSD-Fit-Report-${fullName.replace(/\s+/g,'-')}-${now.toISOString().slice(0,10)}.html`;

    const folderId  = await createProspectFolder(drive, folderName);
    const fileLink  = await uploadReport(htmlContent, fileName, folderId, drive);

    console.log(`[Drive] Report saved: ${fileLink}`);
    return fileLink;

  } catch (err) {
    console.error('[Drive] Upload failed:', err.message);
    return null;
  }
}

module.exports = { saveReportToDrive };
