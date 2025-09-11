import httpx

async def trigger_webhook(payload: dict, webhook_url: str):
    """Webhook trigger karega jab event fire ho"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print("Webhook error:", e)