from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config import MODEL_NAME

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def call_llm(messages):
    prompt = ""
    for m in messages:
        if m["role"] == "user":
            prompt += f"User: {m['content']}\n"
        else:
            prompt += f"Assistant: {m['content']}\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=False
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
