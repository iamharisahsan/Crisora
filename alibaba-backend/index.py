import json
import os
import urllib.request

def handler(event, context):
    """
    Alibaba Cloud Function Compute Handler for Crisora Qwen Relay
    """
    try:
        # Parse payload from Alibaba FC event
        evt = json.loads(event.decode('utf-8')) if isinstance(event, (bytes, bytearray)) else json.loads(event)
        body = json.loads(evt.get('body', '{}')) if isinstance(evt.get('body'), str) else evt.get('body', {})
        
        prompt = body.get('prompt', 'Crisis response simulation status check.')
        api_key = os.environ.get('QWEN_API_KEY')

        # Request to Alibaba Cloud DashScope Qwen API
        req_data = json.dumps({
            "model": "qwen-max",
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
            data=req_data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            reply = res_body['choices'][0]['message']['content']

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "success", "response": reply})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }