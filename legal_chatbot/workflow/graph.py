from legal_chatbot.agents.classifier import LegalAgentNodes
from legal_chatbot.models.query_models import LegalChatState
from langgraph.graph import StateGraph, START, END


def build_legal_graph() -> StateGraph:
    """Construct the legal chatbot workflow graph."""
    
    nodes = LegalAgentNodes()
    graph_builder = StateGraph(LegalChatState)
    
    # Add nodes
    graph_builder.add_node("classifier", nodes.classify_query)
    graph_builder.add_node("router", nodes.route_query)
    graph_builder.add_node("document_request", nodes.request_document)
    graph_builder.add_node("clause_extractor", nodes.extract_clauses)
    graph_builder.add_node("compliance_checker", nodes.check_compliance)
    graph_builder.add_node("summarizer", nodes.summarize_document)
    graph_builder.add_node("risk_assessor", nodes.assess_risk)
    graph_builder.add_node("general_assistant", nodes.general_assistance)
    
    # Define edges
    graph_builder.add_edge(START, "classifier")
    graph_builder.add_edge("classifier", "router")
    
    # Conditional routing
    graph_builder.add_conditional_edges(
        "router",
        lambda state: state.get("routing_decision"),
        {
            "document_request": "document_request",
            "clause_extractor": "clause_extractor",
            "compliance_checker": "compliance_checker",
            "summarizer": "summarizer",
            "risk_assessor": "risk_assessor",
            "general_assistant": "general_assistant"
        }
    )
    
    # All paths lead to END
    graph_builder.add_edge("document_request", END)
    graph_builder.add_edge("clause_extractor", END)
    graph_builder.add_edge("compliance_checker", END)
    graph_builder.add_edge("summarizer", END)
    graph_builder.add_edge("risk_assessor", END)
    graph_builder.add_edge("general_assistant", END)
    
    return graph_builder.compile()
