from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config import MODEL_NAME, MAX_NEW_TOKENS

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[INFO] Loading model: {MODEL_NAME}")
print(f"[INFO] MAX_NEW_TOKENS: {MAX_NEW_TOKENS}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def call_llm(messages):
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )

    generated = outputs[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()
