import streamlit as st

st.set_page_config(page_title="Deceptive Design Detector", layout="centered")


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Centered Header Styles */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .custom-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.75rem;
    }
    
    .intro-text {
        color: #4b5563;
        font-size: 0.95rem;
        line-height: 1.6;
        max-width: 620px;
        margin: 0 auto;
        text-align: center;
    }
    
    /* Button Customization */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border-radius: 0.375rem;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def clear_text():
    st.session_state["input_text"] = ""

st.markdown('''
    <div class="header-container">
        <h1 class="custom-title">Deceptive Design Detector</h1>
        <div class="intro-text">
            Deceptive designs are user interfaces crafted to trick users into making unintended choices. 
            This tool audits interface copy using a 100-point base system, deducting points based on pattern severity 
            (-30 High, -25 Medium, -15 Low) to evaluate deception risk.
        </div>
    </div>
''', unsafe_allow_html=True)


if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

user_text = st.text_area(
    "Paste interface text or checkout flow copy here:", 
    key="input_text",
    height=150, 
    placeholder=""
)


def run_semantic_audit(text):
    text_lower = text.lower()
    score = 100
    detected_issues = []

    def has_any(token_list):
        return any(token in text_lower for token in token_list)

    def has_combination(list1, list2):
        return has_any(list1) and has_any(list2)

    # Confirmshaming
    refusal_tokens = ["no", "decline", "skip", "opt out", "without", "reject"]
    manipulation_tokens = ["savings", "save", "discount", "offer", "deal", "risk", "danger", "unprotected", "regret", "lose", "full price", "hate", "miss", "like savings"]
    if has_combination(refusal_tokens, manipulation_tokens) or has_any(["confirmshaming", "belittling", "derogatory", "guilt"]):
        detected_issues.append((
            "Confirmshaming",
            "Confirmshaming uses manipulative, fear- or guilt-inducing language on decline buttons to coerce compliance.",
            "Use neutral, unbiased language for both acceptance and rejection choices.",
            15
        ))
        score -= 15

    # Sneaking / Unconsented Add-on / Auto-subscription
    addon_tokens = ["assistance", "insurance", "protection", "fee", "handling", "service charge", "warranty", "membership", "extra", "add-on", "promotions", "marketing", "email address"]
    sneaking_tokens = ["without consent", "without permission", "defaulted", "pre-selected", "auto-selected", "added to", "automatically added", "auto-subscribed", "automatically subscribed", "auto-enrolled"]
    if has_combination(addon_tokens, sneaking_tokens) or has_any(["sneaking", "hidden fee", "without user consent", "auto-subscribed"]):
        detected_issues.append((
            "Sneaking / Unconsented Billing",
            "Sneaking conceals information, delays costs, or slips extra items into a cart or subscription list without explicit consent.",
            "Ensure default options require an explicit opt-in action from the user rather than auto-subscribing or auto-selecting.",
            25
        ))
        score -= 25

    # Obstruction / Visual Interference (Roach Motel & Hidden Links)
    exit_tokens = ["cancel", "delete account", "unsubscribe", "opt out", "close membership", "terminate"]
    friction_tokens = ["call support", "speak with", "phone", "cannot cancel online", "agent", "must call", "customer service", "offline", "same color", "hidden link", "blend in", "invisible", "highlighting"]
    if has_combination(exit_tokens, friction_tokens) or has_any(["obstruction", "roach motel", "difficult to cancel", "hidden unsubscribe", "same color as"]):
        detected_issues.append((
            "Obstruction",
            "Obstruction builds artificial friction or hides critical actions (like unsubscribe links) to prevent users from leaving.",
            "Provide direct, straightforward online self-service workflows and clearly visible, contrasting links for unsubscription.",
            30
        ))
        score -= 30

    # Hard to Cancel / Forced Continuity
    subscription_tokens = ["subscription", "trial", "plan", "yearly", "monthly", "membership", "billing"]
    continuity_tokens = ["automatically converts", "auto-renew", "non-refundable", "minimum commitment", "recurring charge", "renews automatically"]
    if has_combination(subscription_tokens, continuity_tokens) or has_any(["forced continuity", "hard to cancel", "recurring billing trap"]):
        detected_issues.append((
            "Hard to Cancel / Forced Continuity",
            "Forced Continuity traps users in ongoing recurring charges by obscuring auto-renewal terms.",
            "Clearly disclose recurring terms upfront and make cancellation as seamless as initial signup.",
            30
        ))
        score -= 30

    # Fake Urgency
    urgency_tokens = ["only left", "limited time", "flash sale", "ends in", "viewing this", "hurry", "last chance", "countdown", "timer"]
    if has_any(urgency_tokens) or has_any(["fake urgency", "artificial scarcity", "false pressure"]):
        detected_issues.append((
            "Fake Urgency",
            "Fake Urgency uses false countdown timers or artificial scarcity claims to pressure users into hasty decisions.",
            "Remove arbitrary pressure tactics; display genuine, real-time inventory and timing data only.",
            15
        ))
        score -= 15

    # Bait-and-Switch
    bait_tokens = ["switched at checkout", "different price", "advertised price", "bait and switch", "unexpected total", "price changed"]
    if has_any(bait_tokens):
        detected_issues.append((
            "Bait-and-Switch",
            "Bait-and-Switch advertises a favorable term upfront, then alters it to a less favorable term during checkout.",
            "Ensure advertised terms and pricing remain strictly consistent throughout the user journey.",
            30
        ))
        score -= 30

    score = max(0, score)
    return score, detected_issues


# 4. Centered Side-by-Side Buttons
col_left, col_audit, col_clear, col_right = st.columns([2, 1.5, 1.5, 2])

with col_audit:
    audit_clicked = st.button("Audit UI", type="primary")

with col_clear:
    st.button("Clear", on_click=clear_text)

# 5. Result Execution
if audit_clicked:
    if user_text.strip():
        score, detected_issues = run_semantic_audit(user_text)

        st.markdown("---")
        
        # Risk Status
        st.subheader("Audit Results & Findings")
        
        if score >= 85:
            st.success(f"Ethical Usability Score: {score} / 100 — Low Deception Risk")
        elif score >= 50:
            st.warning(f"Ethical Usability Score: {score} / 100 — Moderate Deception Risk")
        else:
            st.error(f"Ethical Usability Score: {score} / 100 — High Deception Risk")

        # Flagged Deceptive Patterns
        if detected_issues:
            st.markdown("### Flagged Deceptive Patterns")
            for p_name, desc, fix, penalty in detected_issues:
                st.markdown(f"#### {p_name} (-{penalty} pts)")
                st.markdown(f"**What it means:** {desc}")
                st.markdown(f"**Recommended Fix:** {fix}")
                st.markdown("---")
        else:
            st.success("No dark patterns matched in the provided text.")

        # Scoring Methodology & Rationale
        st.markdown("### Scoring Methodology & Rationale")
        st.markdown("""
        **How the Usability Score is calculated:**
        - **Base Score:** Starts at 100 points assuming complete ethical transparency.
        - **Penalty Rationale:** Deductions are modeled after UX research severity scales, calculated based on the level of financial harm and user autonomy restriction:
          - **-30 pts (High Severity):** Traps users or blocks cancellation (Obstruction, Hard to Cancel, Bait-and-Switch).
          - **-25 pts (Medium Severity):** Introduces unconsented financial charges or forced add-ons (Sneaking).
          - **-15 pts (Low Severity):** Applies psychological pressure, fear, or false scarcity (Fake Urgency, Confirmshaming).
        """)
            
    else:
        st.warning("Please enter interface text above before running the audit.")
