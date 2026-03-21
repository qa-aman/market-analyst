import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def get_groq_api_key() -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable is required. Copy .env.example to .env and set it.")
    return GROQ_API_KEY

LLM_MODEL = "llama-3.3-70b-versatile"
LLM_PROVIDER = "groq"

MAX_CONCURRENCY = 9

FINANCIAL_DOMAINS = [
    "moneycontrol.com",
    "economictimes.indiatimes.com",
    "livemint.com",
    "reuters.com",
    "bloomberg.com",
    "ndtvprofit.com",
]

STOCK_LIST = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "INFY.NS", "name": "Infosys", "sector": "IT"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
    {"symbol": "ITC.NS", "name": "ITC", "sector": "FMCG"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Finance"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Auto"},
    {"symbol": "TRENT.NS", "name": "Trent", "sector": "Retail"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "sector": "Pharma"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Cement"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "FMCG"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Power"},
    {"symbol": "NTPC.NS", "name": "NTPC", "sector": "Power"},
    {"symbol": "ONGC.NS", "name": "ONGC", "sector": "Energy"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Auto"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metals"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Metals"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Conglomerate"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "sector": "Infrastructure"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Finance"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "sector": "IT"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "sector": "Banking"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Mining"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Labs", "sector": "Pharma"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "sector": "Pharma"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "sector": "Pharma"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "sector": "Auto"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "sector": "Healthcare"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Auto"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "sector": "Cement"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Auto"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "sector": "FMCG"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "sector": "Insurance"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "sector": "Insurance"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "sector": "FMCG"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "sector": "Metals"},
    {"symbol": "BPCL.NS", "name": "BPCL", "sector": "Energy"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "sector": "Defence"},
]

SYMBOL_TO_NAME = {s["symbol"]: s["name"] for s in STOCK_LIST}
