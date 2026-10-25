"""Task mechanics and extractive grounding, never a claimed root-cause accuracy."""
from pydantic import ValidationError
from backend.app.models import Finding
from backend.app.workflow import validate_finding


def score_case(case, result, no_write):
    expected_doc = case['expected_document']
    acceptable_docs = case.get('acceptable_documents', [expected_doc])
    evidence = result.get('evidence', [])
    finding = result.get('finding') or {}
    retrieved = [e.get('document_id') for e in evidence]
    cited = {c['source_id'] for c in finding.get('citations', [])}
    expected_cited = any(e.get('document_id') in acceptable_docs and e['id'] in cited for e in evidence) if expected_doc else None
    tool_correct = result.get('decision', {}).get('tool') == case['expected_tool'] if case['expected_tool'] else None
    hit = any(doc in retrieved for doc in acceptable_docs) if expected_doc else None
    category_correct = finding.get('category') in case.get('acceptable_categories', [case['expected_category']]) if expected_doc else None
    structured = None
    grounding = None
    if expected_doc:
        try:
            Finding.model_validate(finding)
            structured = True
            independent = validate_finding(finding, evidence, result.get('incident', {}).get('logs', case.get('logs', '')))
            grounding = bool(independent['passed'])
        except (ValidationError, KeyError, TypeError):
            structured, grounding = False, False
    passed = (result['status'] == case['expected_status'] and no_write and tool_correct is not False
              and (not expected_doc or (category_correct and hit and expected_cited and structured and grounding
                                       and result.get('validation', {}).get('passed', False))))
    rank = min((retrieved.index(doc)+1 for doc in acceptable_docs if doc in retrieved), default=0)
    return {'task_passed': bool(passed), 'category_correct': category_correct, 'tool_correct': tool_correct,
            'retrieval_hit_at_3': hit, 'expected_document_cited': expected_cited, 'retrieved_documents': retrieved,
            'structured_output': structured, 'observation_grounding': grounding, 'diagnostic_accuracy': None,
            'no_write_before_approval': no_write, 'reciprocal_rank': 1/rank if rank else 0 if expected_doc else None}
