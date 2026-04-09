# Feedback Service for QA Document Quality Assessment
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

class FeedbackService:
    """Service for generating QA feedback and improvement suggestions for FRD/BRD documents."""
    
    def __init__(self):
        try:
            self.llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile")
        except Exception as e:
            print(f"Warning: LLM initialization failed: {e}")
            self.llm = None
    
    def generate_improvement_suggestions(self, document_content: str, doc_type: str, feedback_text: str = "") -> str:
        """
        Generate detailed improvement suggestions for a FRD or BRD document when marked as thumbs down.
        
        Args:
            document_content (str): The actual content of the FRD/BRD document
            doc_type (str): Type of document - 'FRD' or 'BRD'
            feedback_text (str): Optional user feedback
            
        Returns:
            str: Detailed improvement suggestions
        """
        if not self.llm:
            return "LLM service unavailable. Please try again later."
        
        if doc_type.upper() == "FRD":
            prompt = self._get_frd_improvement_prompt()
        elif doc_type.upper() == "BRD":
            prompt = self._get_brd_improvement_prompt()
        else:
            prompt = self._get_generic_improvement_prompt()
        
        full_prompt = f"""Document Type: {doc_type}
User Feedback: {feedback_text if feedback_text else "No specific feedback provided"}

Document Content:
{document_content[:5000]}  # Limit to first 5000 characters to avoid token overflow

{prompt}"""
        
        try:
            response = self.llm.invoke(full_prompt)
            return response.content
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return f"Error generating suggestions: {str(e)}"
    
    def _get_frd_improvement_prompt(self) -> str:
        """Return improvement prompt specific to FRD documents."""
        return """As a senior QA and Documentation expert, analyze this Functional Requirements Document (FRD) and provide:

1. **Critical Issues** (Must fix before approval)
   - List any missing functional specifications
   - Identify unclear or ambiguous requirements
   - Point out incomplete use cases or workflows

2. **Quality Gaps** (Should be addressed)
   - Missing input validations and error handling
   - Incomplete API specifications or data models
   - Insufficient test case coverage considerations
   - Missing role-based access control (RBAC) definitions
   - Lack of edge case handling

3. **Improvement Recommendations** (How to fix)
   - Specific sections to expand or clarify
   - Additional requirements to add
   - BDD scenarios to include
   - Test case templates to add
   - Data validation rules to define

4. **Priority Action Items**
   - Top 5 most critical improvements needed
   - Estimated effort for each

5. **Suggested Template/Structure**
   - Provide a sample structure for the missing sections
   - Include at least 2-3 examples of well-defined requirements

Format your response clearly with headers and bullet points for easy action."""

    def _get_brd_improvement_prompt(self) -> str:
        """Return improvement prompt specific to BRD documents."""
        return """As a senior Business Analyst and Documentation expert, analyze this Business Requirements Document (BRD) and provide:

1. **Strategic Issues** (Critical for business alignment)
   - Missing business objectives or goals clarity
   - Incomplete stakeholder mapping
   - Unclear ROI/success metrics
   - Missing business process flows

2. **Requirement Quality Gaps** (Should be addressed)
   - Vague or subjective requirements
   - Missing constraints or assumptions
   - Incomplete scope definition
   - Insufficient risk assessment
   - Missing regulatory or compliance requirements

3. **Improvement Recommendations** (How to fix)
   - Specific sections needing clarification
   - Quantifiable metrics to add
   - Business process diagrams or flows to include
   - Detailed actor/stakeholder descriptions
   - Use case scenarios to expand

4. **Priority Action Items**
   - Top 5 most critical improvements needed
   - Business impact of each improvement
   - Estimated effort

5. **Suggested Content Additions**
   - Sample well-written requirement examples
   - Template for missing sections
   - Metrics framework to include

Format your response clearly with headers and bullet points for easy action."""

    def _get_generic_improvement_prompt(self) -> str:
        """Return generic improvement prompt."""
        return """As a senior QA and Documentation expert, analyze this document and provide:

1. **Critical Issues** (Must fix)
   - Identify unclear or missing specifications
   - Point out inconsistencies or gaps
   - Note incomplete sections

2. **Quality Improvements** (Should address)
   - Clarity and completeness issues
   - Missing details or examples
   - Structural or formatting issues

3. **Specific Recommendations**
   - What exactly needs to be added or modified
   - How to improve the current content
   - Examples of improvements

4. **Priority Action Items**
   - Top 5 changes needed
   - Effort estimate for each

5. **Sample Improvements**
   - Provide 2-3 examples of how to rewrite weak sections

Format your response clearly with headers and bullet points."""


# Singleton instance
_feedback_service = None

def get_feedback_service() -> FeedbackService:
    """Get or create feedback service instance."""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
