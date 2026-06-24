/**
 * ROBARK whitelist collector — Google Apps Script.
 *
 * Setup (5 min, free, unlimited):
 *  1. Go to https://sheets.google.com → create a new sheet, name it "ROBARK Whitelist".
 *  2. Extensions → Apps Script. Delete any code, paste THIS file, click Save (💾).
 *  3. Click "Deploy" → "New deployment".
 *       - Select type: "Web app"
 *       - Execute as: "Me"
 *       - Who has access: "Anyone"
 *     Click Deploy → Authorize (allow your own account).
 *  4. Copy the "Web app URL" (it ends in /exec).
 *  5. In Railway → your service → Variables, add:
 *       WHITELIST_WEBHOOK_URL = <that /exec URL>
 *     Redeploy.
 *
 * Every /whitelist submission now appends a row here. To build the allowlist,
 * filter/copy the "Wallet" column.
 */
function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Submissions") || ss.insertSheet("Submissions");
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["Timestamp", "X Username", "Wallet", "Quote Tweet", "IP"]);
  }
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) {}
  sheet.appendRow([
    d.at || new Date().toISOString(),
    d.xUsername || "",
    d.wallet || "",
    d.quoteUrl || "",
    d.ip || "",
  ]);
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Lets you open the /exec URL in a browser to confirm it's live.
function doGet() {
  return ContentService
    .createTextOutput("ROBARK whitelist collector is live.")
    .setMimeType(ContentService.MimeType.TEXT);
}
