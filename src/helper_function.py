def clean_html_response(text):
    # Remove leading/trailing code block markers if present
    text = text.strip()
    if text.startswith("```html"):
        text = text[len("```html"):].strip()
    if text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text