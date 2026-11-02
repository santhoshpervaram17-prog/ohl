import os, json, time, base64, datetime
from urllib.parse import urlparse, parse_qs
import pyotp, requests
from fyers_apiv3 import fyersModel

SYMBOLS = [
    "NSE:RELIANCE-EQ", "NSE:TCS-EQ", "NSE:HDFCBANK-EQ", "NSE:ICICIBANK-EQ",
    "NSE:INFY-EQ", "NSE:SBIN-EQ", "NSE:BHARTIARTL-EQ", "NSE:LT-EQ",
    "NSE:TATAMOTORS-EQ", "NSE:AXISBANK-EQ", "NSE:SUNPHARMA-EQ", "NSE:NTPC-EQ",
    "NSE:BAJFINANCE-EQ", "NSE:M&M-EQ", "NSE:BEL-EQ", "NSE:TRENT-EQ",
    "NSE:MARUTI-EQ", "NSE:HINDALCO-EQ", "NSE:ITC-EQ", "NSE:HAL-EQ",
    "NSE:PERSISTENT-EQ", "NSE:COFORGE-EQ", "NSE:DIXON-EQ", "NSE:POLYCAB-EQ",
    "NSE:FEDERALBNK-EQ", "NSE:INDHOTEL-EQ", "NSE:CUMMINSIND-EQ", "NSE:LUPIN-EQ",
    "NSE:VOLTAS-EQ", "NSE:MAXHEALTH-EQ", "NSE:OBEROIRLTY-EQ", "NSE:ASHOKLEY-EQ",
    "NSE:BHARATFORG-EQ", "NSE:IDFCFIRSTB-EQ", "NSE:MPHASIS-EQ", "NSE:ASTRAL-EQ",
    "NSE:AUROPHARMA-EQ", "NSE:CONCOR-EQ",
    "MCX:GOLD26DECFUT", "MCX:SILVER26DECFUT", "MCX:CRUDEOIL26NOVFUT",
    "MCX:NATURALGAS26NOVFUT", "MCX:COPPER26NOVFUT", "MCX:ZINC26NOVFUT",
    "MCX:ALUMINIUM26NOVFUT"
]

def b64_encode(val):
    return base64.b64encode(str(val).encode("ascii")).decode("ascii")

def get_fyers_access_token():
    fy_id = os.environ["FYERS_USER_ID"].strip()
    app_id = os.environ["FYERS_APP_ID"].strip()
    secret_id = os.environ["FYERS_SECRET_ID"].strip()
    totp_key = os.environ["FYERS_TOTP_KEY"].strip().replace(" ", "")
    pin = os.environ["FYERS_PIN"].strip()
    redirect_uri = os.environ.get("FYERS_REDIRECT_URI", "https://127.0.0.1:5000/").strip()

    r1 = requests.post("https://api-t2.fyers.in/vagator/v2/send_login_otp_v2",
                       json={"fy_id": b64_encode(fy_id), "app_id": "2"}, timeout=15).json()
    if datetime.datetime.now().second % 30 > 27:
        time.sleep(4)
    otp_code = pyotp.TOTP(totp_key).now()
    r2 = requests.post("https://api-t2.fyers.in/vagator/v2/verify_otp",
                       json={"request_key": r1["request_key"], "otp": otp_code}, timeout=15).json()
    ses = requests.Session()
    r3 = ses.post("https://api-t2.fyers.in/vagator/v2/verify_pin_v2",
                  json={"request_key": r2["request_key"], "identity_type": "pin", "identifier": b64_encode(pin)}, timeout=15).json()
    trade_token = r3["data"]["access_token"]
    ses.headers.update({"authorization": f"Bearer {trade_token}"})
    base_app_id = app_id[:-4] if app_id.endswith("-100") else app_id
    r4 = ses.post("https://api-t1.fyers.in/api/v3/token", json={
        "fyers_id": fy_id, "app_id": base_app_id, "redirect_uri": redirect_uri,
        "appType": "100", "code_challenge": "", "state": "gh_actions", "scope": "",
        "nonce": "", "response_type": "code", "create_cookie": True
    }, timeout=15).json()
    auth_code = parse_qs(urlparse(r4["Url"]).query)["auth_code"][0]
    session = fyersModel.SessionModel(client_id=app_id, secret_key=secret_id,
                                      redirect_uri=redirect_uri, response_type="code",
                                      grant_type="authorization_code")
    session.set_token(auth_code)
    return session.generate_token()["access_token"]

def main():
    token = get_fyers_access_token()
    fyers = fyersModel.FyersModel(client_id=os.environ["FYERS_APP_ID"].strip(), is_async=False, token=token, log_path="")
    all_quotes = []
    for i in range(0, len(SYMBOLS), 50):
        batch = SYMBOLS[i:i + 50]
        resp = fyers.quotes(data={"symbols": ",".join(batch)})
        if resp.get("s") == "ok" and isinstance(resp.get("d"), list):
            all_quotes.extend(resp["d"])
        else:
            raise RuntimeError(f"Quotes API failed: {resp}")
    ist_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    payload = {"s": "ok", "scan_time_ist": ist_now.strftime("%H:%M:%S IST"), "d": all_quotes}
    with open("live_quotes.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

if __name__ == "__main__":
    main()
