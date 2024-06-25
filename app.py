import json
from webscraping.scraper import scrape_webpage
from text_processing.processor import preprocess_text
from entity_extraction.extractor import extract_entities, create_erm_json
from file_handling.file_saver import save_er_model_to_markdown
from neo4j_interactions.neo4j_handler import save_erm_to_neo4j, check_new_erm_against_existing_graph
from tkr_utils import setup_logging, logs_and_exceptions, AppPaths

logger = setup_logging(__file__)

# Add paths to AppPaths and log them
AppPaths.add("erm", storage=False)

@logs_and_exceptions(logger)
def main():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "tuckers_password"

    url = "https://www.offhourscreative.com/"
    webpage_text = scrape_webpage(url)
    preprocessed_text = preprocess_text(webpage_text)

    the_erm = extract_entities(preprocessed_text)
    if not the_erm:
        logger.error("The extracted ERM is empty.")
        return

    save_er_model_to_markdown(the_erm, url)
    logger.info(f"the_erm: {the_erm}")

    erm_json = create_erm_json(the_erm)
    if not erm_json:
        logger.error("Failed to create ERM JSON.")
        return

    cypher_json = check_new_erm_against_existing_graph(uri, user, password, json.loads(erm_json))
    save_erm_to_neo4j(cypher_json, uri, user, password)

if __name__ == "__main__":
    main()