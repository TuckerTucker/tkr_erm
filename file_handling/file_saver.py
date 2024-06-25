import re
from tkr_utils import setup_logging, logs_and_exceptions
from tkr_utils import AppPaths

logger = setup_logging(__file__)

@logs_and_exceptions(logger)
def save_er_model_to_markdown(er_model: str, url: str) -> None:
    url_path = re.sub(r'https?://(www\.)?', '', url).replace('/', '_').replace('.', '_')
    erm_path = AppPaths.ERM_STORE / f"{url_path}.md"
    with erm_path.open("w") as file:
        file.write(f"# ERM for {url}\n\n")
        file.write(er_model)
    logger.info(f"ERM saved to {erm_path}")
