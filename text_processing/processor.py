import re
from tkr_utils import setup_logging, logs_and_exceptions
logger = setup_logging(__file__)

@logs_and_exceptions(logger)
def preprocess_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'\[.*?\]', '', text)  # Remove citations or bracketed text
    return text.strip()