

import openai
import json
import time

class AmbiguityEngine:
    def __init__(self, api_key, model="gpt-4.1-mini", max_retries=3, retry_delay=5):
        openai.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _call_openai_api(self, prompt):
        for attempt in range(self.max_retries):
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a highly specialized AI designed to analyze song lyrics for ambiguity. Your output MUST be a JSON object."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print(f"Attempt {attempt + 1}: JSONDecodeError. Raw content: {content}")
                    # Attempt to fix incomplete JSON
                    if content.strip().endswith('}'):
                        try:
                            return json.loads(content + '}')
                        except json.JSONDecodeError:
                            pass
                    elif content.strip().endswith('}}'):
                        try:
                            return json.loads(content + '}')
                        except json.JSONDecodeError:
                            pass
                    elif content.strip().endswith(']'):
                        try:
                            return json.loads(content + ']')
                        except json.JSONDecodeError:
                            pass
                    elif content.strip().endswith(']]'):
                        try:
                            return json.loads(content + ']')
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback to extract JSON from markdown code block
                    if '```json' in content and '```' in content:
                        json_str = content.split('```json')[1].split('```')[0].strip()
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            pass
                    
                    print(f"Attempt {attempt + 1}: Failed to decode JSON. Retrying...")

            except openai.APIError as e:
                print(f"Attempt {attempt + 1}: OpenAI API Error: {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1}: An unexpected error occurred: {e}")

            time.sleep(self.retry_delay * (attempt + 1))
        return {"error": "Failed to get valid JSON response from OpenAI API after multiple retries."}

    def detect_ambiguity(self, song_title, artist, lyrics):
        prompt = f"""Analyze the following song lyrics for ambiguity. Provide a score from 0.0 to 1.0 (0.0 being no ambiguity, 1.0 being highly ambiguous). Explain your reasoning, identify multiple interpretations if they exist, and note any artistic intentional ambiguity.

Song Title: {song_title}
Artist: {artist}
Lyrics: {lyrics}

Provide the output as a JSON object with the following structure:
{{
  "ambiguity_score": float, // Score from 0.0 to 1.0
  "is_ambiguous": boolean, // True if score > 0.5, False otherwise
  "reasoning": string, // Detailed explanation of ambiguity
  "multiple_interpretations": array<string>, // List of distinct interpretations
  "artistic_intentional_ambiguity": boolean, // True if ambiguity is intentional
  "notes": string // Any additional notes
}}
"""
        
        response = self._call_openai_api(prompt)
        
        if "error" in response:
            return {
                "ambiguity_score": 0.0,
                "is_ambiguous": False,
                "reasoning": response["error"],
                "multiple_interpretations": [],
                "artistic_intentional_ambiguity": False,
                "notes": "Error during analysis."
            }
        
        # Ensure all expected keys are present and have correct types
        response["ambiguity_score"] = float(response.get("ambiguity_score", 0.0))
        response["is_ambiguous"] = bool(response.get("is_ambiguous", False))
        response["reasoning"] = str(response.get("reasoning", "No reasoning provided."))
        response["multiple_interpretations"] = response.get("multiple_interpretations", [])
        if not isinstance(response["multiple_interpretations"], list):
            response["multiple_interpretations"] = [str(response["multiple_interpretations"])]
        response["artistic_intentional_ambiguity"] = bool(response.get("artistic_intentional_ambiguity", False))
        response["notes"] = str(response.get("notes", "No additional notes."))

        return response

if __name__ == '__main__':
    # This part is for testing the AmbiguityEngine in isolation
    # Replace with your actual OpenAI API key
    # For testing, you can use a dummy key, but for actual use, it needs to be valid
    api_key = "YOUR_OPENAI_API_KEY"
    engine = AmbiguityEngine(api_key)

    print("\n--- Testing AmbiguityEngine with 'Bohemian Rhapsody' ---")
    lyrics_bohemian = """Is this the real life?
Is this just fantasy?
Caught in a landslide, no escape from reality.
Open your eyes, look up to the skies and see.
I'm just a poor boy, I need no sympathy.
Because I'm easy come, easy go, little high, little low.
Any way the wind blows doesn't really matter to me, to me.
"""
    result_bohemian = engine.detect_ambiguity("Bohemian Rhapsody", "Queen", lyrics_bohemian)
    print(json.dumps(result_bohemian, indent=2, ensure_ascii=False))

    print("\n--- Testing AmbiguityEngine with 'Twinkle Twinkle Little Star' ---")
    lyrics_twinkle = """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are.
"""
    result_twinkle = engine.detect_ambiguity("Twinkle Twinkle Little Star", "Traditional", lyrics_twinkle)
    print(json.dumps(result_twinkle, indent=2, ensure_ascii=False))

    print("\n--- Testing AmbiguityEngine with an instrumental piece (no lyrics) ---")
    lyrics_instrumental = ""
    result_instrumental = engine.detect_ambiguity("Instrumental Piece", "Composer X", lyrics_instrumental)
    print(json.dumps(result_instrumental, indent=2, ensure_ascii=False))
