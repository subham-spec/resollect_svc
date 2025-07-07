import re
import os

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="nebius",
    api_key=os.getenv("HUGGING_FACE_API_KEY", ''),
)

def call_hugging_face(input):
    completion = client.chat.completions.create(
        model="Qwen/Qwen3-14B",
        messages=[
            {
                "role": "user",
                "content": input
            }
        ],
    )

    final_response = completion.choices[0].message.content

    text = final_response
    print(text)
    matches = re.findall(r"\*\*(.*?)\*\*", text)
    if matches:
        return matches[0]
    elif text.split()[-1] in ["Low", "Medium", "High", "Critical"]:
        return text.split()[-1]
    else:
        return "No matches found"
