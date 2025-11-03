import requests
import json
import gradio as gr

url = "http://localhost:11434/api/generate"

headers={
    'Content-Type':'application/json'
}

history = []

def generate_response(prompt):
    history.append(prompt)
    final_prompt = "\n".join(history)

    data = {
        "model":"MasterCoder",
        "prompt":final_prompt,
        "stream":True
        
    }
    

    with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
        if response.status_code == 200:
            full_reply = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        json_data = json.loads(decoded_line)
                        if "response" in json_data:
                            full_reply += json_data["response"]
                            yield full_reply
                    except json.JSONDecodeError:
                        pass
            history.append(full_reply)
        else:
            yield f"Error: {response.text}"


css = """
body {
    background: linear-gradient(135deg, #b5d0ff 0%, #e8e3ff 60%, #ffffff 100%) !important;
}
"""


# Gradio Interface
interface=gr.Interface(
    fn=generate_response,
    inputs=gr.Textbox(lines=4,placeholder='Enter your prompt'),
    outputs=gr.Textbox(lines=15,label="Output"),
    title="MasterCoder Chat",
    description="Ask your Ollama model anything. Responses stream live!",
    theme="soft",
    css=css
)

interface.launch(share=False)