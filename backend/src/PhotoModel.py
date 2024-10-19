import google.generativeai as genai
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class PhotoModel:
    def __init__(self):
        # Load the instruction from the external file
        instruction = self.load_system_instruction("system_instruction_photo_model.txt")

        # Initialize the Gemini model with multimodal capabilities
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,  # Allow for some creativity in responses
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 512,
                "response_mime_type": "text/plain",
            },
            system_instruction=instruction
        )

    @staticmethod
    def load_system_instruction(file_path: str) -> str:
        """Load system instruction from a file."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"System instruction file not found: {file_path}")

    def analyze_image(self, image_path: str) -> str:
        """Analyze the image and generate a description."""
        with open(image_path, "rb") as img:
            response = self.model.generate(
                inputs={"image": img},
                task="image-to-text",
                context="Analyze the provided photo and generate a description."
            )

        generated_text = response.get("generated_text", "").strip()

        if generated_text != "-1":
            return generated_text + " (Generated from photo)"
        return generated_text

