import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def get_llm_response(prompt):
    try:
        full_prompt = (
            "You are a scheduling assistant. Given the user's natural language request, "
            "return ONLY a JSON array of schedule objects with the fields: "
            "commitment, day, start_time (24hr), end_time (24hr), location. "
            "No extra explanation, just valid JSON.\n\nUser input: " + prompt
        )
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"
    
def parse_schedule_from_llm_resonse(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return []
    
       
