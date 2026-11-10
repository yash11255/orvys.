/**
 * Orvys website → Google Sheets
 * Receives form submissions from the website and appends them to a tab
 * named after the form: "Enquiries", "Partnerships", "Report Downloads", "Newsletter".
 * Tabs and header columns are created automatically.
 *
 * Setup: see SETUP.md in the website folder.
 * Security: honeypot spam trap, formula-injection protection, and generous
 * rate limits. Real submissions are never discarded: anything unusual goes to
 * a "Flagged" tab for review.
 */

// Optional: an email address to notify on every new submission (leave "" to disable).
var NOTIFY_EMAIL = "";

// Only these tab names are accepted (prevents arbitrary sheet creation).
var ALLOWED_FORMS = ["Enquiries", "Partnerships", "Report Downloads", "Newsletter", "Research Registry", "NGO Suggestions"];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var p = (e && e.parameter) || {};
    var formType = ALLOWED_FORMS.indexOf(p.formType) >= 0 ? p.formType : "Enquiries";

    // Honeypot: only bots fill this hidden field. Drop silently.
    if (p.website) return json_({ ok: true });
    if (Object.keys(p).length > 30) return json_({ ok: false, error: "too many fields" });

    // Checks that never discard a real person's submission. Anything unusual is
    // saved to a "Flagged" tab for review instead of the normal tab.
    var flag = "";
    if (p.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(p.email)) flag = "email looks invalid";
    else if (formType !== "Newsletter" && !String(p.name || "").trim()) flag = "name missing";

    // Rate limit keyed on the whole identity (contact + name + organisation), so
    // two different people with the same name are never counted together.
    // Generous limits: 10 per person per hour, 500 per hour overall.
    var cache = CacheService.getScriptCache();
    var who = [p.email, p.phone, p.name, p.organisation].map(function (v) { return String(v || "").trim().toLowerCase(); }).join("|");
    var key = "rl_" + Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, who)).slice(0, 40);
    var n = Number(cache.get(key) || 0) + 1, all = Number(cache.get("rl_all") || 0) + 1;
    cache.put(key, String(n), 3600);
    cache.put("rl_all", String(all), 3600);
    if (!flag && n > 10) flag = "more than 10 submissions in an hour from the same person";
    if (!flag && all > 500) flag = "unusually high traffic (over 500 submissions in an hour)";

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var tab = flag ? "Flagged" : formType;
    if (flag) { p.flagReason = flag; p.originalForm = formType; }
    var sheet = ss.getSheetByName(tab) || ss.insertSheet(tab);

    // Build/extend the header row from incoming fields.
    var fields = Object.keys(p).filter(function (k) { return k !== "formType" && k !== "website"; });
    var lastCol = sheet.getLastColumn();
    var headers = lastCol ? sheet.getRange(1, 1, 1, lastCol).getValues()[0] : [];
    if (headers.length === 0) {
      headers = ["Received At"];
    }
    fields.forEach(function (f) { if (headers.indexOf(f) < 0) headers.push(f); });
    sheet.getRange(1, 1, 1, headers.length).setValues([headers])
      .setFontWeight("bold").setBackground("#0e1a29").setFontColor("#ffffff");
    sheet.setFrozenRows(1);

    var row = headers.map(function (h) {
      if (h === "Received At") return new Date();
      var v = p[h] == null ? "" : String(p[h]);
      // Prevent spreadsheet formula injection.
      return /^[=+\-@]/.test(v) ? "'" + v : v.slice(0, 5000);
    });
    sheet.appendRow(row);

    if (NOTIFY_EMAIL && !flag) {
      var body = fields.map(function (f) { return f + ": " + p[f]; }).join("\n");
      MailApp.sendEmail(NOTIFY_EMAIL, "New website submission: " + formType, body);
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Visit the web app URL in a browser to confirm it is live.
function doGet() {
  return json_({ ok: true, service: "Orvys forms" });
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
