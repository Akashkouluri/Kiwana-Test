"""
System and Operational Guardrails
Defines the technical rules spanning conversational routing, memory retention, and data reporting.
"""

ROUTING_CONTEXT_GUARDRAIL = """
Routing must use the latest available conversation context, not only the latest sentence in isolation. 
Its purpose is to make sure the system routes users based on the full meaning of the ongoing journey, not based on a narrow reading of the most recent line alone.
"""

SOURCE_ATTRIBUTION_GUARDRAIL = """
Source attribution must remain intact throughout the journey. 
Its purpose is to make sure the system never loses where the user originally came from, even if the conversation later moves across channels, sessions, or handling paths. 
This guardrail is important for measurement, reporting, collaborator performance, and optimization.
"""

RETENTION_AND_LIFECYCLE_GUARDRAIL = """
Retention logic must track actual user behavior, not assumptions. 
Its purpose is to make sure follow-up, re-engagement, retargeting, and lifecycle updates are based on what the user really did, not on what the system guesses they probably did. 

Retention and lifecycle handling must keep CRM and system data clean. 
Its purpose is to make sure the system’s records remain reliable, structured, deduplicated, traceable, and usable for routing, reporting, support, and optimization.
"""
