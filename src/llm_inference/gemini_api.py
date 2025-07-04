import google.generativeai as genai
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    MAX_GEMINI_OUTPUT_TOKENS,
    GEMINI_COST_WARNING_THRESHOLD_USD
)
from config.logging_config import logger
import json # For parsing structured responses if needed

# Configure the Google Generative AI client with your API key.
# This should be done once at the application's start.
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the GenerativeModel with the specified model name.
# This model instance will be used for all content generation requests.
_gemini_model_instance = genai.GenerativeModel(GEMINI_MODEL_NAME)

def estimate_gemini_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Estimates the cost of a Gemini API request based on token counts.
    NOTE: These are example prices and can change. Always refer to Google's
          official Gemini API pricing page for the most up-to-date information.

    Args:
        input_tokens (int): Number of input tokens.
        output_tokens (int): Number of output tokens.

    Returns:
        float: Estimated cost in USD.
    """
    # Example pricing for Gemini 1.5 Pro (check official docs for current rates)
    # Input: $7.00 per 1M tokens
    # Output: $21.00 per 1M tokens
    # Gemini 1.5 Flash (cheaper):
    # Input: $0.35 per 1M tokens
    # Output: $1.05 per 1M tokens

    # Adjust prices based on the selected model in settings.py
    if GEMINI_MODEL_NAME == "gemini-1.5-pro":
        input_price_per_million = 7.00
        output_price_per_million = 21.00
    elif GEMINI_MODEL_NAME == "gemini-1.5-flash":
        input_price_per_million = 0.35
        output_price_per_million = 1.05
    else: # Default or other models
        input_price_per_million = 1.00 # Placeholder for unknown models
        output_price_per_million = 3.00 # Placeholder for unknown models
        logger.warning(f"Using placeholder prices for unknown model: {GEMINI_MODEL_NAME}")


    cost = (input_tokens / 1_000_000) * input_price_per_million + \
           (output_tokens / 1_000_000) * output_price_per_million
    return cost

def generate_content_with_quota_check(prompt: str, max_tokens: int = MAX_GEMINI_OUTPUT_TOKENS) -> str | None:
    """
    Generates content using the Gemini API with a pre-flight token count and cost estimate.
    Warns the user if the estimated cost exceeds a predefined threshold.

    Args:
        prompt (str): The input prompt for the Gemini API.
        max_tokens (int): The maximum number of tokens to generate in the response.

    Returns:
        str | None: The generated text from the Gemini API, or None if the request
                    is cancelled or an error occurs.
    """
    logger.info(f"Preparing Gemini API request for prompt (max_tokens={max_tokens})...")
    try:
        # 1. Estimate Input Tokens
        # The count_tokens method is free and doesn't count against inference quota.
        count_response = _gemini_model_instance.count_tokens(prompt)
        input_token_count = count_response.total_tokens
        logger.info(f"Estimated input tokens: {input_token_count}")

        # 2. Estimate Cost
        # We need to estimate output tokens to get a full cost estimate.
        # A conservative estimate is to assume output tokens could be up to max_tokens.
        # Or, if you have a sense of typical response length, use that.
        estimated_output_tokens = max_tokens # Assume worst-case for cost estimation
        estimated_cost_usd = estimate_gemini_cost(input_token_count, estimated_output_tokens)

        logger.info(f"Estimated cost for this request: ${estimated_cost_usd:.4f} USD")

        # 3. Quota/Cost Warning
        if estimated_cost_usd > GEMINI_COST_WARNING_THRESHOLD_USD:
            print(f"\n--- Gemini API Cost Warning ---")
            print(f"This request is estimated to cost around ${estimated_cost_usd:.4f} USD.")
            print(f"Input tokens: {input_token_count}, Estimated output tokens: {estimated_output_tokens}")
            print(f"Current model: {GEMINI_MODEL_NAME}")
            user_input = input("Do you wish to proceed? (y/n): ").lower()
            if user_input != 'y':
                print("Gemini API request cancelled by user.")
                logger.info("Gemini API request cancelled by user due to cost warning.")
                return None

        # 4. Make the API Call
        logger.info("Sending request to Gemini API...")
        response = _gemini_model_instance.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens
            }
        )

        # 5. Process Response
        # Access the text from the response.
        # The 'text' attribute handles most common cases. For structured data, you might use .candidates[0].content.parts[0].text
        generated_text = response.text
        logger.info("Gemini API request completed successfully.")
        return generated_text

    except genai.types.BlockedPromptException as e:
        # Handle cases where the prompt or response is blocked due to safety policies.
        feedback = e.response.prompt_feedback
        logger.warning(f"Gemini API: Prompt blocked. Reason: {feedback.block_reason}, Safety Ratings: {feedback.safety_ratings}")
        print(f"\n--- Gemini API Blocked ---")
        print(f"Your request was blocked due to safety concerns: {feedback.block_reason}")
        for rating in feedback.safety_ratings:
            print(f"  Category: {rating.category.name}, Probability: {rating.probability.name}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the API call.
        logger.error(f"An unexpected error occurred during Gemini API call: {e}", exc_info=True)
        print(f"\n--- Gemini API Error ---")
        print(f"An error occurred while calling the Gemini API: {e}")
        return None

# Example usage for testing this module directly
if __name__ == "__main__":
    # This block will only run if you execute this file directly (e.g., python gemini_api.py)
    # It demonstrates how to use the generation function with quota check.
    print("--- Running Gemini API Sample Request ---")
    sample_prompt = "Write a short, inspiring paragraph about the future of AI in healthcare."
    response = generate_content_with_quota_check(sample_prompt, max_tokens=200)
    if response:
        print(f"\n--- Gemini Sample Response ---\nPrompt: {sample_prompt}\nResponse: {response}")

    print("\n--- Running Gemini API Sample Request (potentially higher cost) ---")
    # This prompt might trigger the cost warning if it's above your threshold
    long_prompt = "Write a comprehensive essay (approx. 1500 words) on the ethical implications of advanced generative AI, covering topics such as bias, misinformation, job displacement, and the philosophical questions of consciousness. Include a detailed introduction, several body paragraphs, and a concluding summary. Discuss potential regulatory frameworks and the role of international cooperation in mitigating risks."
    response_long = generate_content_with_quota_check(long_prompt, max_tokens=1500)
    if response_long:
        print(f"\n--- Gemini Long Sample Response ---\nPrompt: {long_prompt}\nResponse: {response_long[:500]}...") # Print first 500 chars
