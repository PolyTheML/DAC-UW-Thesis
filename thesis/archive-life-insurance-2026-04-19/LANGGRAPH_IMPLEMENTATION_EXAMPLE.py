"""
LangGraph Implementation Example: Phase 1 - Intelligent Routing

Shows how to upgrade your existing underwriting workflow from hard-coded
routing to agentic reasoning using LangGraph + Claude.

This is a SKETCH — meant to illustrate the architecture.
Real implementation requires full integration with UnderwritingState.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from medical_reader.state import UnderwritingState
from anthropic import Anthropic

# ============================================================================
# SETUP
# ============================================================================

client = Anthropic()

# Example: Current hard-coded logic (what we're replacing)
def old_decision_logic(state: UnderwritingState) -> str:
    """
    Current approach: rigid rules.
    Problem: Can't reason about edge cases.
    """
    if state.risk_level == "DECLINE":
        return "DECLINE"
    elif state.risk_level == "HIGH":
        return "HITL"  # Always HITL for HIGH
    elif state.risk_level == "MEDIUM":
        if any(f in state.flags for f in ["occupational", "endemic"]):
            return "HITL"
        else:
            return "STP"
    else:
        return "STP"


# ============================================================================
# PHASE 1: INTELLIGENT DECISION NODE
# ============================================================================

def intelligent_decision_node(state: UnderwritingState) -> dict:
    """
    NEW: Claude reasons about the case before making a decision.

    Returns: {
        "decision": "DECLINE" | "STP" | "HITL" | "ESCALATE",
        "reasoning": str,
        "confidence": float (0.0-1.0),
        "recommendation": str,
    }
    """

    # Build context for Claude
    applicant_summary = f"""
    **Applicant Profile**
    - Name: {state.extracted_data.applicant_name} (extracted)
    - Age: {state.extracted_data.age}, Gender: {state.extracted_data.gender}
    - Occupation: {state.extracted_data.occupation_type}
    - Province: {state.extracted_data.province}
    - Healthcare Tier: {state.extracted_data.healthcare_tier}

    **Health Profile**
    - BMI: {state.extracted_data.bmi:.1f}
    - Blood Pressure: {state.extracted_data.systolic}/{state.extracted_data.diastolic}
    - Conditions: {[c for c in [
        'Smoker' if state.extracted_data.smoker else None,
        'Diabetes' if state.extracted_data.diabetes else None,
        'Hypertension' if state.extracted_data.hypertension else None,
        'High Cholesterol' if state.extracted_data.hyperlipidemia else None,
        'Family History (CHD)' if state.extracted_data.family_history_chd else None,
    ] if c]}

    **Risk Assessment**
    - Mortality Ratio: {state.actuarial.mortality_ratio:.2f}
    - Risk Tier: {state.risk_level}
    - Risk Score: {state.risk_score:.1f}/100
    - Annual Premium: ${state.actuarial.gross_annual_premium:,.2f}
    - Monthly Premium: ${state.actuarial.gross_monthly_premium:,.2f}

    **Flags**
    - Extraction Confidence: {min(state.extracted_data.confidence_scores.values()):.1%}
    - Flags: {state.flags}
    - Occupational Multiplier: {state.occupation_risk.risk_multiplier:.2f}x
    - Endemic Multiplier: {state.region_risk.endemic_risk_multiplier:.2f}x

    **Risk Factor Breakdown**
    {', '.join(f"{k}: {v:.2f}x" for k, v in state.actuarial.factor_breakdown.items())}
    """

    # Prompt Claude to reason about the case
    prompt = f"""
    You are an experienced actuarial underwriter reviewing a life insurance application
    for the Cambodian market. Your job is to decide the underwriting action.

    {applicant_summary}

    CONTEXT: You're evaluating a case for a digital life insurance platform serving Cambodia.
    Risk tolerances:
    - STP (Straight-Through Processing): Approve automatically for low-risk, high-confidence cases
    - HITL (Human-In-The-Loop): Route to human underwriter for review (expected: 30% of cases)
    - ESCALATE: Get expert underwriter for edge cases (expected: 5% of cases)
    - DECLINE: Reject (only for very high risk or missing data)

    Consider:
    1. Is the risk tier appropriate given the applicant's profile?
    2. Are the Cambodia-specific multipliers reasonable?
       - Motorbike couriers are the #1 concern (45% surcharge is high)
       - Mondulkiri/Ratanakiri provinces have high endemic disease (+30%)
    3. Are there any red flags?
       - Extraction confidence <70%? (data quality issue)
       - Occupational + endemic flags together? (compounding risk)
       - Unusual age/occupation combination? (potential fraud?)
    4. What's the business precedent?
       - We typically STP MEDIUM tier cases without occupational flags
       - We HITL MEDIUM tier if occupational OR endemic flag present
       - We DECLINE if MR > 4.0 (uninsurable at standard rates)

    Your decision:
    - DECIDE: Pick one of [DECLINE, STP, HITL, ESCALATE]
    - EXPLAIN: 1-2 sentences on why
    - CONFIDENCE: How confident are you? (0.0-1.0)
    - RECOMMENDATION: Any special instructions for the reviewer (if HITL/ESCALATE)?

    Format your response as JSON:
    {{
        "decision": "STP" | "HITL" | "ESCALATE" | "DECLINE",
        "explanation": "1-2 sentences explaining the decision",
        "confidence": 0.85,
        "recommendation": "If HITL/ESCALATE, specific guidance for reviewer (e.g., 'Request additional occupational verification')",
        "reasoning": "Detailed reasoning (3-4 sentences). Why this decision?"
    }}
    """

    # Call Claude
    response = client.messages.create(
        model="claude-opus-4-6",  # Use latest model for best reasoning
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse response
    import json
    try:
        result = json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        # Fallback if Claude doesn't return JSON
        result = {
            "decision": "HITL",
            "explanation": "Claude reasoning failed; defaulting to human review",
            "confidence": 0.0,
            "recommendation": "Review logic error; escalate",
            "reasoning": response.content[0].text,
        }

    return result


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_intelligent_underwriting_graph():
    """
    Create a LangGraph workflow with intelligent routing.

    FLOW:
    INTAKE → PRICING → REVIEW → INTELLIGENT_DECISION →
      {DECLINE, STP, HITL, ESCALATE}
    """

    graph = StateGraph(UnderwritingState)

    # ====== NODES ======

    # Existing nodes (from your codebase)
    # graph.add_node("intake", intake_node)
    # graph.add_node("pricing", pricing_node)
    # graph.add_node("review", review_node)
    # (These are pre-existing; we're replacing the decision logic)

    # NEW: Intelligent decision node
    graph.add_node("intelligent_decision", intelligent_decision_node)

    # Terminal nodes (stub implementation)
    graph.add_node("decline", lambda state: {"status": "declined"})
    graph.add_node("stp", lambda state: {"status": "approved_stp"})
    graph.add_node("hitl", lambda state: {"status": "pending_review"})
    graph.add_node("escalate", lambda state: {"status": "escalated_to_expert"})

    # ====== EDGES ======

    # Linear flow to decision node
    graph.add_edge("intake", "pricing")
    graph.add_edge("pricing", "review")
    graph.add_edge("review", "intelligent_decision")

    # Conditional edges: Route based on Claude's decision
    def route_decision(state: UnderwritingState) -> Literal["decline", "stp", "hitl", "escalate"]:
        """
        Extract decision from state (set by intelligent_decision_node).
        Route to terminal node.
        """
        # The intelligent_decision_node sets state.decision
        decision = state.decision.lower()

        if decision == "decline":
            return "decline"
        elif decision == "stp":
            return "stp"
        elif decision == "hitl":
            return "hitl"
        elif decision == "escalate":
            return "escalate"
        else:
            return "hitl"  # Default to HITL if unclear

    graph.add_conditional_edges(
        "intelligent_decision",
        route_decision,
        {
            "decline": "decline",
            "stp": "stp",
            "hitl": "hitl",
            "escalate": "escalate",
        }
    )

    # Terminal edges
    graph.add_edge("decline", END)
    graph.add_edge("stp", END)
    graph.add_edge("hitl", END)
    graph.add_edge("escalate", END)

    return graph.compile()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def run_example():
    """
    Example: Process a single applicant through the intelligent workflow.
    """

    # Create the graph
    workflow = create_intelligent_underwriting_graph()

    # Example applicant (mimics UnderwritingState)
    example_state = {
        "applicant_name": "Sokha",
        "extracted_data": {
            "age": 45,
            "gender": "M",
            "bmi": 32.0,
            "smoker": False,
            "systolic": 145,
            "diastolic": 90,
            "diabetes": True,
            "hypertension": True,
            "hyperlipidemia": False,
            "family_history_chd": False,
            "occupation_type": "Motorbike Courier",
            "province": "Kandal",
            "healthcare_tier": "Clinic",
            "confidence_scores": {"age": 0.95, "bmi": 0.85, "occupation": 0.70},
        },
        "actuarial": {
            "mortality_ratio": 1.80,
            "gross_annual_premium": 1293.45,
            "gross_monthly_premium": 107.79,
            "factor_breakdown": {
                "motorbike_courier": 1.45,
                "diabetes": 1.40,
                "hypertension": 1.25,
                "kandal_endemic": 1.03,
            },
        },
        "risk_level": "MEDIUM",
        "risk_score": 45.0,
        "flags": ["occupational", "endemic", "hypertension"],
        "occupation_risk": {
            "occupation_type": "Motorbike Courier",
            "risk_multiplier": 1.45,
        },
        "region_risk": {
            "province": "Kandal",
            "endemic_risk_multiplier": 1.03,
        },
    }

    # Run the workflow
    print("=" * 80)
    print("INTELLIGENT UNDERWRITING WORKFLOW")
    print("=" * 80)
    print(f"\nApplicant: {example_state['applicant_name']}")
    print(f"Risk Level: {example_state['risk_level']}")
    print(f"Premium: ${example_state['actuarial']['gross_annual_premium']:,.2f}/year")
    print(f"Flags: {', '.join(example_state['flags'])}")

    # This would actually invoke the graph
    # result = workflow.invoke(example_state)
    # print(f"\nDecision: {result['decision']}")
    # print(f"Reasoning: {result['reasoning']}")
    # print(f"Confidence: {result['confidence']:.1%}")

    # For this example, we'll call intelligent_decision_node directly
    print("\n" + "-" * 80)
    print("CLAUDE'S REASONING")
    print("-" * 80)

    decision_result = intelligent_decision_node(example_state)
    print(f"\nDecision: {decision_result['decision']}")
    print(f"Explanation: {decision_result['explanation']}")
    print(f"Confidence: {decision_result['confidence']:.1%}")
    print(f"Reasoning: {decision_result['reasoning']}")
    if decision_result['recommendation']:
        print(f"Recommendation: {decision_result['recommendation']}")


# ============================================================================
# KEY DIFFERENCES FROM CURRENT SYSTEM
# ============================================================================

"""
OLD (Hard-coded logic):
  if risk_level == "HIGH":
      return "HITL"

  Problem: Can't handle "HIGH but with explanations that justify STP"

NEW (Agentic reasoning):
  Claude analyzes the full context and decides:
  "45M motorbike courier in Kandal is HIGH risk, but extraction quality is good
   and the occupational/endemic multipliers are standard for the region.
   Recommend HITL but flag: 'Occupational risk is expected for this job.'"

  Benefit: Nuanced reasoning, context-aware decisions, less false positives

INTEGRATION WITH STRESS-TESTING:
  Run 10,000 synthetic scenarios through intelligent_workflow:
  - Measure: Does Claude's decision rate match old hard-coded rate?
  - Measure: Do HITL escalation rates align with PSI drift alerts?
  - Validate: Does intelligent routing catch the 3 failure modes better?
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
Phase 1 Implementation Checklist:

1. [ ] Integrate with UnderwritingState (update state model)
2. [ ] Update intelligent_decision_node to accept actual UnderwritingState
3. [ ] Test on 100 real application samples
4. [ ] Compare decision distribution vs old logic (sanity check)
5. [ ] Measure latency (should be <2s per case due to Claude API call)
6. [ ] Wire into REST API (/api/v1/underwrite with new routing)
7. [ ] Add to React dashboard: show Claude's reasoning alongside decision
8. [ ] Validate on stress_testing/ synthetic batches
9. [ ] Measure: HITL escalation rate vs PSI alerts (do they correlate?)
10. [ ] Document in thesis as "Appendix: Intelligent Routing Implementation"

Phase 2 (after Phase 1 working):
  - Add anomaly_detector node
  - Add expert_agent node for ESCALATE path
  - Persistent memory of case outcomes
"""


if __name__ == "__main__":
    print("This is a sketch of Phase 1 LangGraph implementation.")
    print("To run it, you'd need actual UnderwritingState objects.")
    print("\nKey files to integrate:")
    print("  - medical_reader/state.py (use UnderwritingState)")
    print("  - langgraph library (pip install langgraph anthropic)")
    print("\nSee THESIS_END_TO_END_EXPLANATION.md for context.")
