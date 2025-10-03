from legal_chatbot.models.query_models import QueryClassifier, LegalChatState, QueryType
from legal_chatbot.config import Config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage

class LegalAgentNodes:
    """Collection of agent nodes for the legal chatbot workflow."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE
        )
    
    def classify_query(self, state: LegalChatState) -> dict:
        """Classify the type of legal query."""
        last_message = state["messages"][-1]
        
        classifier_llm = self.llm.with_structured_output(QueryClassifier)
        
        classification_prompt = f"""
        {Config.LEGAL_CONTEXT}
        
        Classify this legal query into one of these types:
        - clause_search: Looking for specific clauses or contract terms
        - compliance_check: Checking compliance with regulations (FDCPA, TCPA, etc.)
        - document_summary: Requesting overview or summary of document
        - risk_assessment: Identifying legal risks or liabilities
        - general_inquiry: General legal questions about the document
        
        Query: {last_message.content}
        
        Document available: {state.get('document_content') is not None}
        """
        
        result = classifier_llm.invoke([
            {"role": "system", "content": "You are a legal query classifier."},
            {"role": "user", "content": classification_prompt}
        ])
        
        return {
            "query_type": result.query_type,
            "analysis_results": {
                "confidence": result.confidence,
                "key_terms": result.key_terms
            }
        }
    
    def route_query(self, state: LegalChatState) -> dict:
        """Route the query to appropriate specialist agent."""
        query_type = state.get("query_type", QueryType.GENERAL_INQUIRY)
        has_document = state.get("document_content") is not None
        
        # Routing logic
        if not has_document and query_type != QueryType.GENERAL_INQUIRY:
            return {"routing_decision": "document_request"}
        
        routing_map = {
            QueryType.CLAUSE_SEARCH: "clause_extractor",
            QueryType.COMPLIANCE_CHECK: "compliance_checker",
            QueryType.DOCUMENT_SUMMARY: "summarizer",
            QueryType.RISK_ASSESSMENT: "risk_assessor",
            QueryType.GENERAL_INQUIRY: "general_assistant"
        }
        
        return {"routing_decision": routing_map.get(query_type, "general_assistant")}
    
    def request_document(self, state: LegalChatState) -> dict:
        """Handle case where document is needed but not provided."""
        response = AIMessage(content="""
I need access to the legal document to answer your query effectively.

Please provide the document using:
    load <filepath>

Supported formats: PDF (native or scanned), PNG, JPG, TIFF, BMP
The system includes advanced OCR with automatic rotation detection for scanned documents.
        """.strip())
        
        return {"messages": [response]}
    
    def extract_clauses(self, state: LegalChatState) -> dict:
        """Specialized agent for finding and extracting specific clauses."""
        last_message = state["messages"][-1]
        document = state.get("document_content", "")
        metadata = state.get("document_metadata", {})
        
        # Truncate document for context window
        doc_preview = document[:8000] + "..." if len(document) > 8000 else document
        
        prompt = f"""
{Config.LEGAL_CONTEXT}

You are a legal clause extraction specialist for a US Collection Agency.

DOCUMENT: {metadata.get('filename', 'Unknown')}
PAGES: Multiple (check PAGE markers in content)

DOCUMENT CONTENT:
{doc_preview}

USER QUERY: {last_message.content}

TASK:
1. Identify all clauses relevant to the query
2. Quote exact clause text with section/page references
3. Explain the legal implications for debt collection
4. Note any FDCPA or TCPA compliance considerations
5. Highlight potential issues or ambiguities

Format your response with clear section headers and citations.
        """.strip()
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a legal clause extraction expert."},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response]}
    
    def check_compliance(self, state: LegalChatState) -> dict:
        """Specialized agent for compliance checking."""
        last_message = state["messages"][-1]
        document = state.get("document_content", "")
        metadata = state.get("document_metadata", {})
        
        doc_preview = document[:8000] + "..." if len(document) > 8000 else document
        
        prompt = f"""
{Config.LEGAL_CONTEXT}

You are a compliance specialist for US debt collection law.

DOCUMENT: {metadata.get('filename', 'Unknown')}

DOCUMENT CONTENT:
{doc_preview}

USER QUERY: {last_message.content}

COMPLIANCE REVIEW FOR:
- Fair Debt Collection Practices Act (FDCPA)
- Telephone Consumer Protection Act (TCPA)
- State-specific collection laws
- CFPB regulations

ANALYSIS FRAMEWORK:
1. Identify relevant regulatory requirements
2. Check document compliance with each requirement
3. Flag violations or areas of concern
4. Provide specific recommendations
5. Cite relevant statutes and sections

Be thorough and specific. This is critical for legal risk management.
        """.strip()
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a legal compliance auditor."},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response]}
    
    def summarize_document(self, state: LegalChatState) -> dict:
        """Create structured summaries of legal documents."""
        document = state.get("document_content", "")
        metadata = state.get("document_metadata", {})
        
        doc_preview = document[:10000] + "..." if len(document) > 10000 else document
        
        prompt = f"""
{Config.LEGAL_CONTEXT}

Provide a comprehensive legal summary of this document.

DOCUMENT: {metadata.get('filename', 'Unknown')}
SIZE: {metadata.get('word_count', 0):,} words

CONTENT:
{doc_preview}

SUMMARY STRUCTURE:
1. Document Type & Purpose
2. Key Parties Involved
3. Material Terms & Obligations
4. Payment Terms & Amounts
5. Important Dates & Deadlines
6. Dispute Resolution Provisions
7. Compliance Considerations (FDCPA/TCPA)
8. Risk Factors
9. Recommendations for Legal Review

Be concise but comprehensive. Focus on legally significant elements.
        """.strip()
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a legal document summarization expert."},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response]}
    
    def assess_risk(self, state: LegalChatState) -> dict:
        """Assess legal risks in documents."""
        last_message = state["messages"][-1]
        document = state.get("document_content", "")
        
        doc_preview = document[:8000] + "..." if len(document) > 8000 else document
        
        prompt = f"""
{Config.LEGAL_CONTEXT}

Conduct a risk assessment of this legal document for a debt collection agency.

DOCUMENT CONTENT:
{doc_preview}

USER QUERY: {last_message.content}

RISK ASSESSMENT FRAMEWORK:
1. Regulatory Compliance Risks (FDCPA, TCPA, state laws)
2. Litigation Exposure
3. Enforceability Issues
4. Consumer Protection Violations
5. Reputational Risks
6. Financial/Collection Risks

For each identified risk:
- Severity (High/Medium/Low)
- Likelihood
- Specific provisions causing concern
- Mitigation recommendations
- Urgent action items

Prioritize risks by severity and provide actionable recommendations.
        """.strip()
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a legal risk assessment specialist."},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response]}
    
    def general_assistance(self, state: LegalChatState) -> dict:
        """Handle general legal inquiries."""
        last_message = state["messages"][-1]
        document = state.get("document_content", "")
        
        context = ""
        if document:
            doc_preview = document[:5000] + "..." if len(document) > 5000 else document
            context = f"\n\nDOCUMENT CONTEXT:\n{doc_preview}"
        
        prompt = f"""
{Config.LEGAL_CONTEXT}

You are a legal assistant for a US Collection Agency's legal department.
{context}

USER QUERY: {last_message.content}

Provide a thorough, professional response addressing the query.
Focus on practical application and cite relevant laws/regulations when applicable.
        """.strip()
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a helpful legal assistant."},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response]}
