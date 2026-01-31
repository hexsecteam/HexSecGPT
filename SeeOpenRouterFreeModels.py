import requests

API_KEY = "paste your api"
url = "https://openrouter.ai/api/v1/models"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

r = requests.get(url, headers=headers)
data = r.json()["data"]

free_models = []

for m in data:
    model_id = m["id"]
    pricing = m.get("pricing", {})

    is_free_suffix = model_id.endswith(":free")
    is_free_pricing = (
        pricing.get("prompt", 1) == 0 and
        pricing.get("completion", 1) == 0
    )

    if is_free_suffix or is_free_pricing:
        free_models.append(model_id)


for model in sorted(free_models):
    print(model)