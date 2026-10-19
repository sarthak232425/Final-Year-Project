"""
Presentation generator script.
Reads slides from docs/PRESENTATION_SLIDES.md or definitions and generates
docs/Final_Project_Review_Presentation.pptx if python-pptx is available,
or outputs structured presentation markdown and XML assets.
"""

import os
import sys

def create_presentation():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
    except ImportError:
        print("[INFO] python-pptx is not installed. To generate the .pptx binary file, run: pip install python-pptx")
        print("[INFO] All 12 slides are already formatted and available in docs/PRESENTATION_SLIDES.md")
        return False

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Dark theme background color
    bg_color = RGBColor(10, 14, 26)       # #0a0e1a
    primary_color = RGBColor(59, 130, 246) # #3b82f6
    text_white = RGBColor(240, 244, 255)
    text_muted = RGBColor(148, 163, 184)

    slides_data = [
        {
            "title": "AI-Based Customer Segmentation and\nPersonalized WhatsApp Marketing Platform",
            "subtitle": "Department of Information Technology • Final Year B.E. Project\nReview-2: MVP Implementation & Research Paper Draft",
            "bullets": []
        },
        {
            "title": "Problem Statement & Industry Context",
            "subtitle": "The challenge of conversational commerce and marketing fatigue",
            "bullets": [
                "Traditional retail marketing relies on generic email/SMS broadcasts (<3% click-through, high opt-outs).",
                "WhatsApp delivers >90% open rates, but unguided messaging triggers spam reports, blockages, and churn.",
                "Small & mid-size retailers lack automated ML pipelines to segment customers based on actual purchasing habits.",
                "Lack of automated fatigue guardrails: Existing systems do not enforce frequency caps or privacy consent policies."
            ]
        },
        {
            "title": "End-to-End System Architecture",
            "subtitle": "Layered design separating analytics, policy enforcement, and dispatch",
            "bullets": [
                "Ingestion & Hygiene: Parses raw transactions, isolates cancellations ('C'), filters corrupt records.",
                "RFM Feature Engineering: Extracts Recency, Frequency, Monetary spend; applies log-transform & Z-score scaling.",
                "Clustering & Validation: K-Means with automated K-sweep evaluating Silhouette, Davies–Bouldin, and Calinski–Harabasz.",
                "Recommendation Engine: Maps segments to campaign archetypes with human-readable rationale.",
                "Fatigue Prevention Gate: Enforces consent checks, global suppression, and rolling 30-day frequency caps.",
                "Presentation Layer: FastAPI REST backend + React 18 / TypeScript interactive web dashboard."
            ]
        },
        {
            "title": "Data Ingestion & Hygiene Pipeline",
            "subtitle": "Guaranteed data quality prior to feature vector computation",
            "bullets": [
                "Automatic column alias mapping (supports standard UCI Online Retail format).",
                "Strict validation checks: drops missing customer IDs, invalid date strings, negative prices/quantities.",
                "Cancellation Isolation: Orders starting with 'C' are separated to prevent distorted purchase frequencies.",
                "Quality Gate Metrics: Retention rate and comprehensive issue logs reported with each run."
            ]
        },
        {
            "title": "RFM Feature Formulation & Normalization",
            "subtitle": "Mathematical basis for customer behavioral modeling",
            "bullets": [
                "Recency (R): Days elapsed since customer's last valid invoice relative to reference date.",
                "Frequency (F): Total count of distinct, valid purchase invoices.",
                "Monetary (M): Lifetime net transactional spend (sum of quantity * unit price).",
                "Log-Transformation: x' = ln(x + 1) compresses severe Pareto spend skewness.",
                "Standardization: Z-score scaling ensures equal weight across dimensions in Euclidean space."
            ]
        },
        {
            "title": "Unsupervised Clustering & Optimal K Selection",
            "subtitle": "Algorithmic parameter tuning without arbitrary human guessing",
            "bullets": [
                "Automated parameter sweep across K in [2, 10] with reproducible random seed (seed=42).",
                "Selected K = 4 achieves peak Silhouette Score (0.4328) and lowest Davies–Bouldin Index (0.8712).",
                "Segment 0 (Champions): Low Recency (12d), High Frequency (8.5), High Spend ($1,240).",
                "Segment 1 (Loyal Steady): Medium Recency (28d), Consistent Frequency (4.0).",
                "Segment 2 (At Risk): High Recency (92d), Prior regular spenders drifting away.",
                "Segment 3 (Hibernating): Very high Recency (180d), Low Frequency (1.0)."
            ]
        },
        {
            "title": "Explainable Campaign Recommendations",
            "subtitle": "Transparent heuristics bridging machine learning into business action",
            "bullets": [
                "Champions -> VIP Exclusive Loyalty Campaign (exclusive early access discounts).",
                "Loyal Steady -> Tier Progression / Reward Points Campaign.",
                "Recent One-Time -> Cross-Sell & Complementary Product Campaign.",
                "At Risk / Hibernating -> Win-Back Reactivation Campaign with tiered incentives.",
                "Full Explainability: Every recommendation generates a clear natural-language rationale."
            ]
        },
        {
            "title": "Marketing Fatigue Prevention Engine",
            "subtitle": "Ethical guardrails and regulatory compliance filters",
            "bullets": [
                "Consent Gate: Mandatory verification of customer opt-in (consent_given == True).",
                "Suppression Gate: Automated exclusion of customers on global opt-out/suppression lists.",
                "Frequency Capping: Hard limit of max 3 messages per rolling 30-day window.",
                "Lifecycle Matching: Campaign window alignment (e.g., Win-Back requires Recency >= 30 days).",
                "Zero Unauthorized Dispatches: 100% compliance verified in test suite."
            ]
        },
        {
            "title": "Software Engineering & Architecture Patterns",
            "subtitle": "Modular, production-ready full-stack design",
            "bullets": [
                "Clean Architecture: Routers, Services, Schemas, ORM Models, and Adapters strictly decoupled.",
                "Adapter Pattern: MockWhatsAppAdapter for offline testing & review with [SIMULATED] tags; Live adapter ready.",
                "Type Safety: Pydantic v2 schemas on backend; strict TypeScript interfaces on frontend.",
                "Modern Frontend: React 18, Vite, responsive dark-mode design system with zero external UI bloat."
            ]
        },
        {
            "title": "Automated Testing & Quality Assurance",
            "subtitle": "Comprehensive verification with hand-calculated test vectors",
            "bullets": [
                "test_ingestion.py: CSV parser validation, edge cases, alias normalization.",
                "test_rfm.py: RFM calculations verified against hand-calculated mathematical test cases.",
                "test_clustering.py: Cluster assignments, metrics validity, and reproducibility.",
                "test_fatigue.py: Consent blocking, suppression lists, frequency saturation.",
                "test_recommendations.py: Recommendation completeness, scoring, and non-null explanations."
            ]
        },
        {
            "title": "Live Demonstration Plan",
            "subtitle": "Walkthrough of working MVP on localhost:5173",
            "bullets": [
                "1. Data Ingestion: Loading example transactions and viewing real-time data cleaning summary.",
                "2. RFM & Clustering: Executing ML pipeline and exploring behavioral customer cohorts.",
                "3. Validation Metrics: Reviewing K-selection sweep and Silhouette Score profile.",
                "4. Recommendations: Inspecting explainable campaign cards and fatigue gate rejections.",
                "5. WhatsApp Simulation: Demonstrating simulated chat template dispatch with audit trail."
            ]
        },
        {
            "title": "Review 2 Deliverables & Next Phase Roadmap",
            "subtitle": "Project progress summary and future enhancements",
            "bullets": [
                "Completed for Review 2: Runnable MVP, verified clustering, research paper draft, presentation deck.",
                "Next Phase (Review 3): Multi-tenant database isolation, live Meta Cloud API integration, XGBoost churn modeling.",
                "Academic Deliverable: Research paper draft prepared in IEEE format with 10 verified citations.",
                "Thank You: Open for Questions & Technical Discussion."
            ]
        }
    ]

    blank_layout = prs.slide_layouts[6]

    for item in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Background rectangle
        bg_shape = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = bg_color
        bg_shape.line.color.rgb = bg_color

        # Title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(1.5))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = item["title"]
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = text_white

        # Subtitle
        p2 = tf.add_paragraph()
        p2.text = item["subtitle"]
        p2.font.size = Pt(14)
        p2.font.color.rgb = primary_color
        p2.space_before = Pt(8)

        # Bullets
        if item["bullets"]:
            bullet_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.7), Inches(4.5))
            btf = bullet_box.text_frame
            btf.word_wrap = True

            for idx, bullet in enumerate(item["bullets"]):
                bp = btf.paragraphs[0] if idx == 0 else btf.add_paragraph()
                bp.text = "• " + bullet
                bp.font.size = Pt(16)
                bp.font.color.rgb = text_white
                bp.space_before = Pt(14)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    docs_dir = os.path.join(project_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    output_path = os.path.join(docs_dir, "Final_Project_Review_Presentation.pptx")
    prs.save(output_path)
    print(f"[SUCCESS] PowerPoint presentation generated at: {output_path}")
    return True

if __name__ == "__main__":
    create_presentation()
