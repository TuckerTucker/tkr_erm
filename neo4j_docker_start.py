import subprocess
from tkr_utils import logs_and_exceptions, setup_logging, AppPaths

logger = setup_logging(__file__)

# Add Neo4j paths
AppPaths.add("neo4j", storage=True)

# Define the Docker command with the new volume path
docker_command = [
    "docker", "run",
    "--publish=7474:7474",
    "--publish=7687:7687",
    f"--volume={AppPaths.NEO4J_STORE}:/data",
    "neo4j"
]

# Run the Docker command
@logs_and_exceptions(logger)
def start_neo4j_docker() -> None:
    """
    Start the Neo4j Docker container.
    """
    logger.info("Starting Neo4j Docker container.")
    try:
        subprocess.Popen(docker_command)
        logger.info("Docker container started successfully in the background.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    start_neo4j_docker()
