import json
from tkr_utils import setup_logging, logs_and_exceptions
from tkr_utils.helper_openai import OpenAIHelper
logger = setup_logging(__file__)

myChat = OpenAIHelper()

system_prompt = """
    You are an expert data modeller with a specialty in graph databases. 
    Your responses are concise and informative.

    Your project is a graph database built bottom-up from unstructured data. 
    - As new data is added, the graph grows and evolves
    - The schema is flexible and scalable, adapting to new data while ensuring consistency and clarity
    - You ensure data integrity by following ISO/IEC 11179 standards

    Schema Guidelines:
    - Ensure the model does not become over-normalized
    - Use practical normalization to balance detail and performance
    - Ensure names are descriptive and avoid ambiguity
    - Give meaningful names to relationships rather than just a pair of entities

    Examples of Well-formed Nodes and Relationships:
    - Node Example: (n:Person {name: "Alice", age: 30, email: "alice@example.com"})
    - Relationship Example: (a:Person {name: "Alice"})-[:WORKS_AT {since: "2020-01-01"}]->(b:Company {name: "Acme Corp"})

    Nodes, Edges, and Metadata:
    Define each node (entity) and edge (relationship) with clear metadata.
    When possible, provide the URI for the closest schema.org term (otherwise leave blank).
    - name: A unique name
    - schema_org_term
    - description: A brief description
    - attributes (for nodes) - An array with at least:
        - name: The name of the attribute
        - schema_org_term
        - dataType: Data type (e.g., String, DateTime)
        - mappedTo: A description of what the attribute represents
        - from (for edges): The source entity
        - to (for edges): The target entity

    Now, let's think through this step-by-step:
"""

json_prompt = """
    Task: return the given ERM as well-formed json

    - Return only json
        - Format: {"ERM": {  "entities": [ {"name": "User","schema_org_term": "https://schema.org/Person","description": "An individual who interacts with the Off-Hours Creative community.","attributes": [  { "name": "UserID", "schema_org_term": "https://schema.org/identifier", "dataType": "String", "mappedTo": "Unique identifier for the user"  },  { "name": "Email", "schema_org_term": "https://schema.org/email", "dataType": "String", "mappedTo": "User's email address"  },  { "name": "Name", "schema_org_term": "https://schema.org/name", "dataType": "String", "mappedTo": "User's full name"  }] }, {"name": "Membership","schema_org_term": "","description": "Different types of memberships offered by Off-Hours Creative.","attributes": [  { "name": "MembershipID", "schema_org_term": "https://schema.org/identifier", "dataType": "String", "mappedTo": "Unique identifier for the membership type"  },  { "name": "MembershipType", "schema_org_term": "", "dataType": "String", "mappedTo": "Type of membership (e.g., Free, Full)"  },  { "name": "Benefits", "schema_org_term": "", "dataType": "String", "mappedTo": "Description of membership benefits"  }] }, {"name": "Project","schema_org_term": "","description": "Creative projects that users are working on.","attributes": [  { "name": "ProjectID", "schema_org_term": "https://schema.org/identifier", "dataType": "String", "mappedTo": "Unique identifier for the project"  },  { "name": "ProjectType", "schema_org_term": "", "dataType": "String", "mappedTo": "Type of project (e.g., Writing, Music, Painting)"  },  { "name": "Description", "schema_org_term": "", "dataType": "String", "mappedTo": "Brief description of the project"  }] }, {"name": "Course","schema_org_term": "https://schema.org/Course","description": "Courses available to members.","attributes": [  { "name": "CourseID", "schema_org_term": "https://schema.org/identifier", "dataType": "String", "mappedTo": "Unique identifier for the course"  },  { "name": "CourseName", "schema_org_term": "", "dataType": "String", "mappedTo": "Name of the course"  },  { "name": "CourseDescription", "schema_org_term": "", "dataType": "String", "mappedTo": "Description of the course content"  }] }  ],  "relationships": [ {"name": "EnrolledIn","schema_org_term": "","description": "Relationship indicating that a user is enrolled in a course.","from": "User","to": "Course" }, {"name": "HasMembership","schema_org_term": "","description": "Relationship indicating the type of membership a user has.","from": "User","to": "Membership" }, {"name": "WorksOn","schema_org_term": "","description": "Relationship indicating that a user is working on a creative project.","from": "User","to": "Project" }  ]} }
        - No comments
        - No markdown wrappers i.e. ```json ```
"""

@logs_and_exceptions(logger)
def extract_entities(text: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Provide an ERM for the provided text: {text}"}
    ]

    logger.info("Identifying Entities")
    response = myChat.send_message(messages)
    logger.info(response)

    return response.choices[0].message.content


@logs_and_exceptions(logger)
def create_erm_json(erm: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{json_prompt}: {erm}"}
    ]

    logger.info("Creating ERM JSON")
    response = myChat.send_message(messages)
    raw_content = response.choices[0].message.content
    # logger.info(f"raw_content: {raw_content}")

    try:
        # Extract JSON from response content
        start_idx = raw_content.find('{')
        end_idx = raw_content.rfind('}') + 1
        json_content = raw_content[start_idx:end_idx]
        
        # Parse to validate the JSON content
        json.loads(json_content)

        logger.info(f"ERM JSON: {json_content}")
        return json_content
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse JSON: {e}")
        return ""