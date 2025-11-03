import requests
import json
import gradio as gr
import speech_recognition as sr

url = "http://localhost:11434/api/generate"

headers={
    'Content-Type':'application/json'
}

history = []


# Function to transcribe speech to text
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        return f"(Could not recognize speech: {e})"



# Generating Model Response
def generate_response(prompt,audio_file=None):
    if audio_file is not None:
        spoken_text = transcribe_audio(audio_file)
        prompt = f"{prompt}\nUser (voice): {spoken_text}"


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
    inputs=[gr.Textbox(lines=4,placeholder='Enter your prompt'),gr.Audio(sources="microphone", type="filepath")],
    outputs=gr.Textbox(lines=15,label="Output",autoscroll=True),
    title="MasterCoder Chat",
    description="Ask your local Ollama model by typing or speaking — live streamed responses!",
    theme="soft",
    examples=[
        ["Write a Python function for binary search",None],
        ["Explain recursion with code",None],
        ["Generate SQL query to find employees earning above average salary",None]
    ],
    css=css,
    
)

interface.launch(share=True)