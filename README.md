# Host 100% on GitHub (GitHub Pages + GitHub Actions Auto-Login)

1. Upload `index.html`, `scan_fyers_to_json.py`, and `.github/workflows/fyers_ohl_scan.yml` to your GitHub repository.
2. Go to **Settings -> Secrets and variables -> Actions -> New repository secret** and add:
   - `FYERS_USER_ID`
   - `FYERS_APP_ID`
   - `FYERS_SECRET_ID`
   - `FYERS_TOTP_KEY`
   - `FYERS_PIN`
   - `FYERS_REDIRECT_URI`
3. Go to **Settings -> Pages**, select Branch `main` (root `/`), and click **Save**.
4. In the **Actions** tab, click **FYERS 1-Min OHL Auto-Scan (09:16 IST)** -> **Run workflow** to test immediately.
