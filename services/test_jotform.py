import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("JOTFORM_API_KEY")
form_id = "261964341015958"

r = requests.get(
    f"https://apec-rise.jotform.com/API/form/{form_id}/submissions",
    headers={"APIKEY": api_key},
    timeout=15
)

print(r.status_code)
print(r.text)