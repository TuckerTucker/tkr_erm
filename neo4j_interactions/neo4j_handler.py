from typing import Dict, Any
from py2neo import Graph, NodeMatcher, RelationshipMatcher
from tkr_utils import setup_logging, logs_and_exceptions
import json

logger = setup_logging(__file__)
@logs_and_exceptions(logger)
def save_erm_to_neo4j(cypher_json: Dict[str, Any], uri: str, user: str, password: str) -> None:
    try:
        cypher_commands = cypher_json.get("cypher_commands", [])
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return

    graph = Graph(uri, auth=(user, password))
    tx = graph.begin()
    for command in cypher_commands:
        description = command.get("description", "No description")
        statement = command.get("statement")
        parameters = command.get("parameters", {})
        if statement:
            logger.info(f"Executing: {description}")
            try:
                tx.run(statement, parameters)
                logger.info(f"Successfully executed: {statement}")
            except Exception as e:
                logger.error(f"Failed to execute statement: {statement} - Error: {e}")

    try:
        tx.commit()
        logger.info("ERM saved to Neo4j")
    except Exception as e:
        logger.error(f"Failed to commit transaction: {e}")
        tx.rollback()

@logs_and_exceptions(logger)
def check_new_erm_against_existing_graph(uri: str, user: str, password: str, erm: Dict[str, Any]) -> Dict[str, Any]:
    graph = Graph(uri, auth=(user, password))
    node_matcher = NodeMatcher(graph)
    relationship_matcher = RelationshipMatcher(graph)
    cypher_commands = []

    entities = erm["ERM"]["entities"]
    relationships = erm["ERM"]["relationships"]

    for entity in entities:
        entity_name = entity.get("name", "UnnamedEntity")
        attributes = entity.get("attributes", [])
        logger.info(f"Checking entity: {entity_name}")
        logger.debug(f"Attributes for {entity_name}: {attributes}")

        attributes_str = ", ".join([f"n.{attr.get('name', 'unknown')} = ${attr.get('name', 'unknown')}" for attr in attributes])
        attributes_values = {attr.get('name', 'unknown'): '' for attr in attributes}

        merge_command = f"MERGE (n:{entity_name} {{name: $name}}) SET {attributes_str}"
        
        cypher_commands.append({
            "description": f"Create or merge a node representing {entity_name}",
            "statement": merge_command,
            "parameters": {"name": entity_name, **attributes_values}
        })
        logger.info(f"Generated Cypher for {entity_name}: {merge_command}")

    for relationship in relationships:
        rel_type = relationship.get("name", "UNKNOWN_RELATIONSHIP")
        start_node_label = relationship.get("from", "UNKNOWN_FROM")
        end_node_label = relationship.get("to", "UNKNOWN_TO")
        logger.info(f"Checking relationship: {start_node_label}-[:{rel_type}]->{end_node_label}")

        start_node = node_matcher.match(start_node_label).first()
        end_node = node_matcher.match(end_node_label).first()

        if start_node and end_node:
            if not relationship_matcher.match((start_node, end_node), rel_type).first():
                create_rel_command = (
                    f"MATCH (a:{start_node_label} {{name: $start_name}}), (b:{end_node_label} {{name: $end_name}}) "
                    f"MERGE (a)-[r:{rel_type}]->(b)"
                )
                cypher_commands.append({
                    "description": f"Create or merge a relationship between {start_node_label} and {end_node_label}",
                    "statement": create_rel_command,
                    "parameters": {"start_name": start_node["name"], "end_name": end_node["name"]}
                })
                logger.info(f"Generated Cypher for relationship {start_node_label}-[:{rel_type}]->{end_node_label}: {create_rel_command}")
        else:
            logger.warning(f"Could not find matching nodes for relationship {start_node_label}-[:{rel_type}]->{end_node_label}")

    return {"cypher_commands": cypher_commands}