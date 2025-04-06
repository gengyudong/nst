import json
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configure the generative AI client
client = genai.configure(api_key="AIzaSyB-f0wwWOlfxVOgfpylwfI0aitBnSw17RA")

# Step 1: Extract text from a local PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Step 2: Generate flashcards from the extracted text using generative AI
def generate_flashcards(text):
    # Truncate text to avoid token limits
    max_length = 8000
    text = text[:max_length]
    
    print(f"Using {len(text)} characters of extracted text")

    prompt = (
        '''
        You are given the extracted text from a document. Your task is to randomly pick 30 concepts from it and generate flashcard-based content from them. For each concept, generate a concept/title such as "Thalamus" as well as the explanation for that question, such as "It is the major relay point and processing center for all sensory impulses". 
        Each concept and explanation should not exceed 40 words. 
        Attached to the answer is also a brief explanation of the concept.
        The output should be in JSON format with the following structure:
    
    Expected Output Structure:
    {
        "card1": 
            {
                "concept": "<concept>",
                "explanation": "<explanation>"
            },
        "card2": 
            {
                "concept": "<concept>",
                "explanation": "<explanation>"
            },
        ...
    }
    '''
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, text],
        )
        
        # Print raw response for debugging
        print("Raw response type:", type(response))
        
        # Try to get the content in different ways
        if hasattr(response, 'text'):
            response_text = response.text
        elif hasattr(response, 'parts') and len(response.parts) > 0:
            response_text = response.parts[0].text
        else:
            # Fallback to string representation
            response_text = str(response)
            
        print("Response preview:", response_text[:200])
        
        # Clean the response text
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to find JSON content
        import re
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Now parse the JSON
        return json.loads(response_text)
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        print(f"Response received: {response_text if 'response_text' in locals() else 'No response'}")
        return None

def save_flashcards_to_json(flashcards, output_path):
    if flashcards:
        try:
            print(f"Saving flashcards to {output_path}...")
            with open(output_path, "w") as json_file:
                json.dump(flashcards, json_file, indent=4)
            print("Flashcards successfully saved.")
        except Exception as e:
            print(f"Error saving flashcards to JSON: {e}")
    else:
        print("No flashcards to save.")

# Main workflow
pdf_path = "public/File.pdf"  # Replace with your PDF file path
output_json_path = "flashcards.json"  # Replace with your desired output path

try:
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Generate flashcards
    flashcards = generate_flashcards(pdf_text)
    
    # Save the flashcards to a JSON file
    save_flashcards_to_json(flashcards, output_json_path)
    
    if flashcards:
        print(f"Flashcards saved to {output_json_path}")
    else:
        print("Failed to generate flashcards.")
except Exception as e:
    print(f"An error occurred: {e}")