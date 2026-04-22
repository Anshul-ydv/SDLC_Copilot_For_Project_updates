import os
import json
from typing import Dict, List, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


class MCPAgent:
    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.llm = ChatOpenAI(
            model="google/gemma-2-27b-it:free",
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.2,
            max_completion_tokens=16000,
            model_kwargs={
                "headers": {
                    "HTTP-Referer": "https://sdlc-copilot.app",
                    "X-Title": "SDLC MCP Pipeline"
                }
            }
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement process()")

    def _invoke_llm(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return json.dumps({"error": str(e), "agent": self.agent_name})


class DocumentReaderAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Document Reader Agent in an MCP pipeline.
Your job is to parse the input document completely and output structured JSON.
You must NOT summarise or paraphrase. Extract everything verbatim where possible.
Tables must be extracted as structured JSON arrays, never as plain text.
Assign each table a unique ID: T1, T2, T3 ... Tn in order of appearance.
Assign each section a unique ID: S1, S2, S3 ... Sn in order of appearance.
Output only valid JSON matching the schema provided."""
        super().__init__("document_reader", system_prompt)

    def process(self, document_content: str, filename: str) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

DOCUMENT TO PARSE:
{document_content}

REQUIRED OUTPUT SCHEMA:
{{
  "document_metadata": {{
    "title": "exact title from document",
    "version": "e.g. V1.1",
    "date": "YYYY-MM-DD",
    "author": "",
    "project_code": "",
    "filename": "{filename}"
  }},
  "sections": [
    {{
      "id": "S1",
      "heading": "exact heading text",
      "content": "full text of section",
      "page_start": 1
    }}
  ],
  "tables": [
    {{
      "table_id": "T1",
      "location": "S3",
      "caption": "table title or heading above it",
      "headers": ["Column A", "Column B"],
      "rows": [
        ["row1_val1", "row1_val2"]
      ],
      "merged_cells": [],
      "notes": "any footnotes below the table"
    }}
  ],
  "raw_text": "full document text as fallback"
}}

Extract all content and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "document_metadata": {
                    "title": filename,
                    "version": "1.0",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "filename": filename
                },
                "sections": [],
                "tables": [],
                "raw_text": response
            }


class RequirementsAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Requirements Agent. You receive a parsed document JSON.
Extract every requirement — functional, non-functional, and constraint.
Each requirement must have: a unique ID (REQ-001, REQ-002...), type, description, priority, and the section ID it came from.
If a requirement does not have an explicit ID in the document, generate one sequentially.
Output only valid JSON."""
        super().__init__("requirements", system_prompt)

    def process(self, reader_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

INPUT DOCUMENT:
{json.dumps(reader_output, indent=2)}

REQUIRED OUTPUT SCHEMA:
{{
  "agent": "requirements",
  "requirements": [
    {{
      "id": "REQ-001",
      "type": "functional | non-functional | constraint",
      "description": "",
      "priority": "high | medium | low",
      "source_section": "S3",
      "linked_table": "T2 or null"
    }}
  ]
}}

Extract all requirements and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"agent": "requirements", "requirements": [], "error": "Failed to parse response"}


class TableAnalyzerAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Table Analyzer Agent. You receive a parsed document JSON.
Analyze every table in the `tables` array.
For each table: infer column data types, detect merged cells, identify sub-headers, flag anomalies.
Do not modify the table data — only add schema metadata.
Output only valid JSON."""
        super().__init__("table_analyzer", system_prompt)

    def process(self, reader_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

INPUT DOCUMENT (focus on tables array):
{json.dumps(reader_output.get('tables', []), indent=2)}

REQUIRED OUTPUT SCHEMA:
{{
  "agent": "table_analyzer",
  "tables": [
    {{
      "table_id": "T1",
      "column_schemas": [
        {{ "name": "Column A", "type": "string | number | date | boolean | enum", "nullable": false, "alignment": "left | right | center" }}
      ],
      "row_count": 0,
      "has_merged_cells": false,
      "has_sub_headers": false,
      "anomalies": [
        {{ "row": 3, "col": 1, "issue": "empty required field" }}
      ]
    }}
  ]
}}

Analyze all tables and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"agent": "table_analyzer", "tables": [], "error": "Failed to parse response"}


class BusinessLogicAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Business Logic Agent. You receive a parsed document JSON.
Extract every business rule, process flow, decision point, and system integration mentioned.
Business rules are IF/THEN statements, conditions, or constraints on behaviour.
Flows are ordered sequences of steps or actions.
Output only valid JSON."""
        super().__init__("business_logic", system_prompt)

    def process(self, reader_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

INPUT DOCUMENT:
{json.dumps(reader_output, indent=2)}

REQUIRED OUTPUT SCHEMA:
{{
  "agent": "business_logic",
  "rules": [
    {{
      "id": "BR-01",
      "condition": "IF ...",
      "action": "THEN ...",
      "source_section": "S4",
      "priority": "mandatory | optional"
    }}
  ],
  "flows": [
    {{
      "id": "FL-01",
      "name": "flow name",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "source_section": "S5"
    }}
  ]
}}

Extract all business logic and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"agent": "business_logic", "rules": [], "flows": [], "error": "Failed to parse response"}


class ChangeRequestAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Change Request Agent. You receive a parsed document JSON.
Extract every change request reference, version delta, or scope change.
Change requests are tagged as CR-XXXXX or described as additions, removals, or modifications to previous versions.
Output only valid JSON."""
        super().__init__("change_request", system_prompt)

    def process(self, reader_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

INPUT DOCUMENT:
{json.dumps(reader_output, indent=2)}

REQUIRED OUTPUT SCHEMA:
{{
  "agent": "change_request",
  "change_requests": [
    {{
      "cr_id": "CR-17234",
      "description": "",
      "delta_type": "addition | removal | modification",
      "impacted_sections": ["S3", "S5"],
      "impacted_tables": ["T2"],
      "impacted_requirements": ["REQ-004"]
    }}
  ]
}}

Extract all change requests and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"agent": "change_request", "change_requests": [], "error": "Failed to parse response"}


class ValidationAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Validation Agent. You receive a parsed document JSON.
Your job is to find inconsistencies, missing data, duplicate IDs, and structural problems.
Check: all table references exist, all requirement IDs are unique, all CR references trace back to requirements, all mandatory table fields are populated.
Output only valid JSON. passed = true only if there are zero errors (warnings are allowed)."""
        super().__init__("validation", system_prompt)

    def process(self, reader_output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

INPUT DOCUMENT:
{json.dumps(reader_output, indent=2)}

REQUIRED OUTPUT SCHEMA:
{{
  "agent": "validation",
  "passed": true,
  "warnings": [
    {{ "type": "empty_cell", "location": "T2 row 4 col 2", "detail": "Priority field is empty" }}
  ],
  "errors": [
    {{ "type": "duplicate_id", "location": "S3", "detail": "REQ-005 appears twice" }}
  ]
}}

Validate the document and output ONLY valid JSON:"""

        response = self._invoke_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"agent": "validation", "passed": False, "warnings": [], "errors": [{"type": "parse_error", "detail": "Failed to parse validation response"}]}


class MasterReceiverAgent(MCPAgent):
    def __init__(self):
        system_prompt = """You are the Master Receiver Agent.
You receive 5 JSON files from specialist agents plus the original reader_output.json.
Merge them into one unified payload.
Conflict resolution rules:
  1. Table Analyzer schema (s2) overrides Reader raw table data for schema fields
  2. Validation errors (s5) must always appear in the unified payload
  3. Change Request data (s4) annotates requirements — do not overwrite them
Output only valid JSON matching the unified payload schema."""
        super().__init__("master_receiver", system_prompt)

    def process(self, reader_output: Dict[str, Any], specialist_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        unified = {
            "document_metadata": reader_output.get("document_metadata", {}),
            "requirements": specialist_outputs.get("requirements", {}).get("requirements", []),
            "table_map": self._merge_tables(
                reader_output.get("tables", []),
                specialist_outputs.get("table_analyzer", {}).get("tables", [])
            ),
            "business_rules": specialist_outputs.get("business_logic", {}).get("rules", []),
            "flows": specialist_outputs.get("business_logic", {}).get("flows", []),
            "change_requests": specialist_outputs.get("change_request", {}).get("change_requests", []),
            "validation_summary": specialist_outputs.get("validation", {})
        }
        return self._link_change_requests(unified)

    def _merge_tables(self, reader_tables: List[Dict], analyzer_tables: List[Dict]) -> List[Dict]:
        table_map = []
        for reader_table in reader_tables:
            table_id = reader_table.get("table_id")
            analyzer_data = next((t for t in analyzer_tables if t.get("table_id") == table_id), {})
            table_map.append({
                "table_id": table_id,
                "caption": reader_table.get("caption", ""),
                "location_section": reader_table.get("location", ""),
                "headers": reader_table.get("headers", []),
                "rows": reader_table.get("rows", []),
                "schema": analyzer_data.get("column_schemas", []),
                "row_count": analyzer_data.get("row_count", len(reader_table.get("rows", []))),
                "has_merged_cells": analyzer_data.get("has_merged_cells", False),
                "anomalies": analyzer_data.get("anomalies", []),
                "linked_requirements": [],
                "linked_cr": []
            })
        return table_map

    def _link_change_requests(self, unified: Dict[str, Any]) -> Dict[str, Any]:
        cr_map = {cr.get("cr_id"): cr for cr in unified.get("change_requests", [])}
        for req in unified.get("requirements", []):
            req["linked_cr"] = [cr_id for cr_id, cr in cr_map.items() if req.get("id") in cr.get("impacted_requirements", [])]
        for table in unified.get("table_map", []):
            table["linked_cr"] = [cr_id for cr_id, cr in cr_map.items() if table.get("table_id") in cr.get("impacted_tables", [])]
        return unified


class MCPPipeline:
    def __init__(self):
        self.reader = DocumentReaderAgent()
        self.requirements = RequirementsAgent()
        self.table_analyzer = TableAnalyzerAgent()
        self.business_logic = BusinessLogicAgent()
        self.change_request = ChangeRequestAgent()
        self.validation = ValidationAgent()
        self.master_receiver = MasterReceiverAgent()

    def process_document(self, document_content: str, filename: str, output_dir: str = "/tmp/mcp_outputs") -> Dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)

        print(f"[MCP Pipeline] Phase 1: Document Reader processing '{filename}'...")
        reader_output = self.reader.process(document_content, filename)
        self._save_json(reader_output, os.path.join(output_dir, "reader_output.json"))

        print("[MCP Pipeline] Phase 2: Running specialist agents...")
        specialist_outputs = {}

        print("  - S1: Requirements Agent")
        specialist_outputs["requirements"] = self.requirements.process(reader_output)
        self._save_json(specialist_outputs["requirements"], os.path.join(output_dir, "s1_requirements.json"))

        print("  - S2: Table Analyzer Agent")
        specialist_outputs["table_analyzer"] = self.table_analyzer.process(reader_output)
        self._save_json(specialist_outputs["table_analyzer"], os.path.join(output_dir, "s2_table_schemas.json"))

        print("  - S3: Business Logic Agent")
        specialist_outputs["business_logic"] = self.business_logic.process(reader_output)
        self._save_json(specialist_outputs["business_logic"], os.path.join(output_dir, "s3_business_logic.json"))

        print("  - S4: Change Request Agent")
        specialist_outputs["change_request"] = self.change_request.process(reader_output)
        self._save_json(specialist_outputs["change_request"], os.path.join(output_dir, "s4_change_requests.json"))

        print("  - S5: Validation Agent")
        specialist_outputs["validation"] = self.validation.process(reader_output)
        self._save_json(specialist_outputs["validation"], os.path.join(output_dir, "s5_validation.json"))

        print("[MCP Pipeline] Phase 3: Master Receiver merging outputs...")
        unified_payload = self.master_receiver.process(reader_output, specialist_outputs)
        self._save_json(unified_payload, os.path.join(output_dir, "unified_payload.json"))

        print(f"[MCP Pipeline] ✓ Pipeline complete. Outputs saved to: {output_dir}")
        return unified_payload

    def _save_json(self, data: Dict[str, Any], filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Singleton instance
mcp_pipeline = MCPPipeline()
