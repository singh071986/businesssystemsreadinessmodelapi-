# Parsed questions and options for the assessment UI
# This is a helper file to keep question text and options cleanly structured for the template

QUESTIONS = [
    {
        "section": "Clarity & Offer System",
        "question": "How clearly defined is your primary offer?",
        "options": [
            {"value": "A", "label": "I’m still refining what I sell."},
            {"value": "B", "label": "I have multiple offers but no clear primary focus."},
            {"value": "C", "label": "I have one clear primary offer and CTA."},
            {"value": "D", "label": "I have one primary offer with defined positioning and proof (testimonials/results)."}
        ]
    },
    {
        "section": "Presence System",
        "question": "What best describes your online presence?",
        "options": [
            {"value": "A", "label": "No structured website."},
            {"value": "B", "label": "Basic website with limited conversion structure."},
            {"value": "C", "label": "Structured website with clear conversion path."},
            {"value": "D", "label": "Website + targeted landing pages aligned to offers."}
        ]
    },
    {
        "section": "Lead Capture System",
        "question": "How are leads captured?",
        "options": [
            {"value": "A", "label": "Manual inquiries (email/DM)."},
            {"value": "B", "label": "Basic contact form or booking link."},
            {"value": "C", "label": "Form/booking with automated confirmations."},
            {"value": "D", "label": "Multi-step qualification (forms, conversational AI, funnels)."}
        ]
    },
    {
        "section": "Customer Journey / CRM System",
        "question": "How structured is your CRM and customer journey?",
        "options": [
            {"value": "A", "label": "Inbox or spreadsheet tracking."},
            {"value": "B", "label": "CRM exists but inconsistent use."},
            {"value": "C", "label": "Defined customer journey stages with consistent usage."},
            {"value": "D", "label": "Lifecycle stages + segmentation + reporting."}
        ]
    },
    {
        "section": "Nurture & Follow-Up System",
        "question": "What follow-up happens after inquiry?",
        "options": [
            {"value": "A", "label": "Manual replies only."},
            {"value": "B", "label": "Templates but no automation."},
            {"value": "C", "label": "Automated confirmations + reminders."},
            {"value": "D", "label": "Multi-step nurture sequences tied to customer journey stages."}
        ]
    },
    {
        "section": "Delivery System",
        "question": "How standardized is client onboarding and fulfillment?",
        "options": [
            {"value": "A", "label": "Varies each time."},
            {"value": "B", "label": "Manual checklist but inconsistent."},
            {"value": "C", "label": "Structured onboarding workflow."},
            {"value": "D", "label": "Automated lifecycle transitions (onboarding → fulfillment → retention)."}
        ]
    },
    {
        "section": "Payments & Offers System",
        "question": "How are payments and offers handled?",
        "options": [
            {"value": "A", "label": "Manual invoicing only."},
            {"value": "B", "label": "Online payments but limited automation."},
            {"value": "C", "label": "Integrated checkout with confirmation workflows."},
            {"value": "D", "label": "Subscriptions, order bumps, automated payment workflows."}
        ]
    },
    {
        "section": "Reactivation & Outreach System",
        "question": "Do you actively monetize your existing database?",
        "options": [
            {"value": "A", "label": "No reactivation efforts."},
            {"value": "B", "label": "Occasional manual outreach."},
            {"value": "C", "label": "Structured reactivation campaigns."},
            {"value": "D", "label": "Automated lifecycle-based reactivation + Outreach AI."}
        ]
    },
    {
        "section": "Reputation & Reviews System",
        "question": "How do you generate and manage reviews?",
        "options": [
            {"value": "A", "label": "No review system."},
            {"value": "B", "label": "Manual requests occasionally."},
            {"value": "C", "label": "Structured review request workflow."},
            {"value": "D", "label": "Automated Reviews AI with follow-up and response workflows."}
        ]
    },
    {
        "section": "AI Engagement & Conversion System",
        "question": "How are AI tools used in your engagement process?",
        "options": [
            {"value": "A", "label": "No AI tools in use."},
            {"value": "B", "label": "AI tools installed but not integrated."},
            {"value": "C", "label": "AI tools integrated into workflows (qualification, reminders)."},
            {"value": "D", "label": "AI voice/conversational agents driving engagement at scale."}
        ]
    },
    {
        "section": "Reporting & Improvement System",
        "question": "How do you track and improve performance?",
        "options": [
            {"value": "A", "label": "I do not consistently track metrics."},
            {"value": "B", "label": "I check results occasionally but no structured review."},
            {"value": "C", "label": "I review dashboards regularly and adjust workflows."},
            {"value": "D", "label": "I track lifecycle performance, attribution, and optimize continuously."}
        ]
    },
    {
        "section": "Lifetime Value & Retention",
        "question": "How do you increase revenue from existing clients?",
        "options": [
            {"value": "A", "label": "No structured retention strategy."},
            {"value": "B", "label": "Occasional manual upsell offers."},
            {"value": "C", "label": "Planned follow-up offers or renewal reminders."},
            {"value": "D", "label": "Automated retention, renewal, and expansion workflows."}
        ]
    }
]
