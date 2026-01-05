# YouTube OAuth Setup

## Steps to Enable YouTube Upload

### 1. Go to Google Cloud Console
https://console.cloud.google.com/

### 2. Select Your Project (or create one)
- Should be the same project where you enabled YouTube Data API v3

### 3. Enable YouTube Data API v3 (if not already)
- Go to: APIs & Services → Library
- Search "YouTube Data API v3"
- Click Enable

### 4. Create OAuth 2.0 Credentials
- Go to: APIs & Services → Credentials
- Click "Create Credentials" → "OAuth client ID"
- If prompted, configure OAuth consent screen first:
  - User Type: External
  - App name: "Video Uploader" (any name)
  - User support email: Your email
  - Developer contact: Your email
  - Click "Save and Continue" through all steps
- Back to Credentials → Create OAuth client ID
- Application type: **Desktop app**
- Name: "Video Uploader Desktop"
- Click Create

### 5. Download the Credentials
- Click the download icon (⬇️) next to your new OAuth client
- Save the file as: `youtube_oauth.json` in this folder

### 6. File Structure
After setup, you should have:
```
credentials/
├── README.md (this file)
├── youtube_oauth.json (your OAuth credentials - KEEP SECRET!)
└── youtube_token.json (auto-generated after first auth)
```

### 7. First Run Authentication
When you first upload a video:
1. A browser window will open
2. Sign in with your YouTube/Google account
3. Grant permissions to the app
4. The token will be saved for future use

## Quota Information
- Daily limit: 10,000 units
- Video upload: 1,600 units
- Caption upload: 200 units
- **You can upload ~5-6 videos per day with captions**

## Important Notes
- ⚠️ **Never commit youtube_oauth.json to git!**
- ⚠️ New/unverified projects have videos set to PRIVATE by default
- To make videos public, complete the API verification audit in Google Cloud Console
