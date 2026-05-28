from ollama import generate
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys

def ollama_model(ai_model, msg):
	try:
		res = generate(model=ai_model, prompt=msg, options={'temperature': 0.0}).response
	except Exception as e:
		res = e
	return res

def gemini_model(ai_model, msg):
	try:
		load_dotenv()
		client = genai.Client()
		config = types.GenerateContentConfig(temperature=0.0,)

		res = client.models.generate_content(model=ai_model, contents=msg, config=config).text
	except Exception as e:
		res = e
	return res

def prompt_model(model: str, prompt: str) -> str :
	match model:
		case "llama3.1"| "phi3"| "deepseek-r1:1.5b" | "llama3.2:3b":
			return ollama_model(model, prompt)
		case "gemini-2.5-flash" | "gemini-2.5-flash-lite" | "gemini-3-flash-preview" | "gemini-3.1-flash-lite":
			return gemini_model(model, prompt)
		case _:
			return(f"Error: model not found \"{model}\"")
	return "Error: unexpected error"

def main():
	argc = len(sys.argv)

	if argc not in [1, 3]:
		print("Usage: uv run main.py <model> <prompt>")
		return

	if argc == 1:
		model = "gemini-3.1-flash-lite"
		prompt = "introduce yourself"
	else:
		model = sys.argv[1]
		prompt = sys.argv[2]

	print("\n--- SENDING ---\n")
	result = prompt_model(model, prompt)
	print("\n--- RESPONSE ---\n")
	print(result)

if __name__ == "__main__":
	main()
