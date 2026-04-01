"""
data_utils.py
=============
Static lookup tables for all 12 assessment questions:
  - Answer texts (short labels from the Question Framework)
  - Answer explanations (full text from Assessment Question Results)
  - Pathway signal mappings
  - Classification rule logic
"""

QUESTIONS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12"]

ANSWER_ENCODING = {"A": 1, "B": 2, "C": 3, "D": 4}
ENCODING_ANSWER = {1: "A", 2: "B", 3: "C", 4: "D"}

PATHWAYS = ["Foundation", "Growth", "Optimization"]
PATHWAY_ENCODING = {"Foundation": 0, "Growth": 1, "Optimization": 2}
ENCODING_PATHWAY = {0: "Foundation", 1: "Growth", 2: "Optimization"}

# ---------------------------------------------------------------------------
# Short answer labels per question (from the Question Framework PDF)
# ---------------------------------------------------------------------------
ANSWER_LABELS = {
    "q1": {
        1: "I'm still refining what I sell.",
        2: "I have multiple offers but no clear primary focus.",
        3: "I have one clear primary offer and CTA.",
        4: "I have one primary offer with defined positioning and proof.",
    },
    "q2": {
        1: "No structured website.",
        2: "Basic website with limited conversion structure.",
        3: "Structured website with clear conversion path.",
        4: "Website + targeted landing pages aligned to offers.",
    },
    "q3": {
        1: "Manual inquiries (email/DM).",
        2: "Basic contact form or booking link.",
        3: "Form/booking with automated confirmations.",
        4: "Multi-step qualification (forms, conversational AI, funnels).",
    },
    "q4": {
        1: "Inbox or spreadsheet tracking.",
        2: "CRM exists but inconsistent use.",
        3: "Defined customer journey stages with consistent usage.",
        4: "Lifecycle stages + segmentation + reporting.",
    },
    "q5": {
        1: "Manual replies only.",
        2: "Templates but no automation.",
        3: "Automated confirmations + reminders.",
        4: "Multi-step nurture sequences tied to customer journey stages.",
    },
    "q6": {
        1: "Varies each time.",
        2: "Manual checklist but inconsistent.",
        3: "Structured onboarding workflow.",
        4: "Automated lifecycle transitions.",
    },
    "q7": {
        1: "Manual invoicing only.",
        2: "Online payments but limited automation.",
        3: "Integrated checkout with confirmation workflows.",
        4: "Subscriptions, order bumps, automated payment workflows.",
    },
    "q8": {
        1: "No reactivation efforts.",
        2: "Occasional manual outreach.",
        3: "Structured reactivation campaigns.",
        4: "Automated lifecycle-based reactivation + Outreach AI.",
    },
    "q9": {
        1: "No review system.",
        2: "Manual requests occasionally.",
        3: "Structured review request workflow.",
        4: "Automated Reviews AI with follow-up and response workflows.",
    },
    "q10": {
        1: "No AI tools in use.",
        2: "AI tools installed but not integrated.",
        3: "AI tools integrated into workflows.",
        4: "AI voice/conversational agents driving engagement at scale.",
    },
    "q11": {
        1: "I do not consistently track metrics.",
        2: "I check results occasionally but no structured review.",
        3: "I review dashboards regularly and adjust workflows.",
        4: "I track lifecycle performance, attribution, and optimize continuously.",
    },
    "q12": {
        1: "No structured retention strategy.",
        2: "Occasional manual upsell offers.",
        3: "Planned follow-up offers or renewal reminders.",
        4: "Automated retention, renewal, and expansion workflows.",
    },
}

# ---------------------------------------------------------------------------
# Detailed explanation texts per question-answer (from Assessment Question
# Results PDF).  Used to generate the personalised output summary.
# ---------------------------------------------------------------------------
ANSWER_EXPLANATIONS = {
    "q1": {
        1: (
            "Offer clarity is one of the most important foundations a business can have — and one "
            "of the hardest to nail down, especially when you're talented in more than one area. "
            "Right now, the energy you're putting into your business may be getting spread across "
            "too many directions, which can make everything feel harder than it needs to be. "
            "This isn't a flaw; it's a stage. The work of getting clear on what you sell and who "
            "it's for is the single most valuable thing you can do right now, because every other "
            "system in your business depends on it."
        ),
        2: (
            "You've built enough momentum to have more than one offer on the table — that's "
            "a real sign of capability. The challenge at this stage is that without a clear "
            "primary focus, your marketing, your systems, and even your client conversations "
            "Energy divided across multiple offers rarely converts as well as energy directed "
            "toward one strong, well-positioned offer. Narrowing your focus isn't about doing "
            "less — it's about making what you do work harder for you."
        ),
        3: (
            "Having one clear offer and a defined call to action is a meaningful milestone "
            "that many business owners skip right past. It means your potential clients know "
            "exactly what you do and what you want them to do next — and that clarity makes "
            "every other part of your business easier to build. Your systems now have "
            "something stable to support, which puts you in a strong position to grow with intention."
        ),
        4: (
            "Your offer is not just clear — it's credible. You've done the work of positioning "
            "what you sell and backing it up with results, which means your marketing has real "
            "traction to work with. This level of offer maturity is what separates businesses "
            "that grow steadily from those that stay stuck in constant refinement mode. "
            "The foundation here is solid, and it opens the door to building more sophisticated "
            "systems around what's already working."
        ),
    },
    "q2": {
        1: (
            "Not having a structured website yet means that right now, your business likely "
            "relies on word of mouth, social media, or direct outreach to connect with potential "
            "clients — and while those can work, they put a ceiling on how far your reach can grow. "
            "A website isn't just a digital business card; it's the place where your "
            "offer becomes credible to someone who has never heard of you before. Building even "
            "a simple, clear web presence is one of the highest-leverage first steps you can take."
        ),
        2: (
            "You have a presence online, which is a real starting point — but if your website "
            "isn't set up to guide a visitor toward a clear next step, it's likely working harder "
            "as a brochure than as a business tool. A website that converts has one job: move "
            "the right person from \"I found you\" to \"I want to talk to you.\" "
            "Small structural adjustments — a stronger "
            "headline, a clear call to action, a simple way to book or inquire — can make a "
            "significant difference without requiring a full rebuild."
        ),
        3: (
            "Your website is doing real work for your business. It has structure, a clear message, "
            "and a path for visitors to follow — which means when the right person lands on it, "
            "they know what to do. This is the kind of online presence that supports consistent "
            "lead flow rather than leaving potential clients guessing. You're well-positioned to "
            "layer in more targeted pages as your offers evolve."
        ),
        4: (
            "Your online presence is working at a strategic level. Not only do you have a structured "
            "main site, but you've also built targeted landing pages that speak directly to specific "
            "offers — which means you're meeting potential clients where they are, with messaging "
            "that's relevant to exactly what they're looking for. This kind of presence supports "
            "higher conversion rates and gives you a strong platform to run campaigns and track results."
        ),
    },
    "q3": {
        1: (
            "When leads come in through email or direct messages, every inquiry depends on you "
            "personally catching it, responding to it, and remembering to follow up. That works "
            "when volume is low, but it creates a fragile system where leads can easily fall through "
            "the cracks — not because you're disorganized, but because the process isn't built to "
            "run without you. Building even a simple, structured capture point is one of the first "
            "steps toward a business that doesn't lose opportunities when life gets busy."
        ),
        2: (
            "Having a form or booking link means you've created a real entry point into your business — "
            "potential clients can find their way to you without requiring a back-and-forth conversation "
            "just to get started. The next layer is making sure something happens automatically after "
            "that form is submitted or that booking is made, so the experience feels responsive and "
            "professional from the very first interaction, even when you're not at your desk."
        ),
        3: (
            "Your lead capture system is doing more than just collecting information — it's responding. "
            "Automated confirmations mean that every person who reaches out receives an immediate, "
            "consistent acknowledgment, which builds trust and reduces the chance they'll move on to "
            "someone else while waiting to hear back. This is a meaningful step toward a business "
            "that operates smoothly even outside of your working hours."
        ),
        4: (
            "Your lead capture process is sophisticated and intentional. Rather than simply collecting "
            "a name and email, you're actively qualifying potential clients before they ever reach you — "
            "filtering for fit, gathering useful information, and guiding the right people through a "
            "structured path toward a conversation or purchase. This kind of system saves significant "
            "time and means the leads that reach you are far more likely to convert."
        ),
    },
    "q4": {
        1: (
            "Tracking clients in your inbox or a spreadsheet is a completely understandable starting "
            "point — it's often how businesses begin. But as your client list grows, this approach "
            "becomes increasingly difficult to maintain reliably. Important follow-ups get missed, "
            "the status of any given client becomes hard to track at a glance, and the mental load "
            "of keeping everything in your head adds up. A simple CRM structure — even a basic "
            "pipeline with a few clear stages — removes that burden "
            "and makes sure nothing slips through."
        ),
        2: (
            "You've recognized the value of a CRM and taken the step of setting one up, which puts "
            "you ahead of many businesses at this stage. The challenge is that a CRM only works when "
            "it's used consistently — and inconsistent use can actually create more confusion than no "
            "system at all, because some information is tracked and some isn't. The goal from here "
            "is to simplify your setup so that using it feels easy enough to do every time, not just "
            "when you remember to."
        ),
        3: (
            "Your CRM isn't just set up — it's being used. You have defined stages for your customer "
            "journey and you're moving clients through them consistently, which means you always have "
            "a clear picture of where each person stands. This is the kind of operational clarity that "
            "makes growth manageable rather than chaotic, and it gives you a reliable foundation to "
            "build more sophisticated automations on top of."
        ),
        4: (
            "Your CRM is operating at a high level. You're not just tracking contacts — you're "
            "segmenting them by behavior, managing lifecycle stages, and using reporting to understand "
            "what's actually happening in your business. This depth of CRM maturity means you can "
            "make decisions based on real data, target the right people with the right messages, and "
            "build automations that respond intelligently to where each client is in their journey with you."
        ),
    },
    "q5": {
        1: (
            "Right now, every follow-up in your business is a task that requires your direct attention "
            "and memory. When someone reaches out, the response depends entirely on you — your "
            "availability, your bandwidth, and whether you happen to see the message at the right time. "
            "This means that on busy days, or during periods when life pulls your attention elsewhere, "
            "potential clients may not hear back quickly enough to stay engaged. "
            "Building even a basic automated response into your follow-up process can make a significant "
            "difference in how many inquiries convert."
        ),
        2: (
            "Having templates is a smart move — it saves time and keeps your communication consistent. "
            "But when those templates still require you to manually send each one, the follow-up process "
            "still depends on you remembering to do it. The gap between a template and an automated "
            "sequence is smaller than it might seem, and closing that gap means your follow-up happens "
            "reliably every time, not just when you have the bandwidth to make it happen."
        ),
        3: (
            "Your follow-up system is working without you having to think about it every time. "
            "Automated confirmations and reminders mean that every new inquiry receives a timely, "
            "consistent response — which communicates professionalism and keeps potential clients "
            "engaged while they're still in decision-making mode. This is a meaningful layer of your "
            "business that's running independently, and it creates a reliable experience for every "
            "person who reaches out."
        ),
        4: (
            "Your follow-up system isn't just functional — it's strategic. Nurture sequences that are "
            "tied to specific customer journey stages mean that each person receives communication "
            "that's relevant to exactly where they are in their relationship with your business. "
            "This level of personalization and consistency builds trust over time, increases conversion "
            "rates, and keeps your business top of mind for people who aren't quite ready to buy yet "
            "but will be."
        ),
    },
    "q6": {
        1: (
            "When every client onboarding is different, a significant amount of your mental energy "
            "goes into figuring out the process each time rather than simply delivering great work. "
            "This can also lead to inconsistent client experiences. Standardizing even the first few "
            "steps of your onboarding process is one of the highest-leverage things you can do to "
            "improve both client satisfaction and your own sense of ease in the business."
        ),
        2: (
            "Having a checklist tells you that you've thought through the onboarding process and you "
            "know what a good client experience looks like. The inconsistency is usually less about "
            "intention and more about execution — checklists that live outside your workflow are easy "
            "to skip when things get busy. Moving your onboarding steps into a structured workflow, "
            "even a simple one, means the process runs whether or not you have the mental bandwidth "
            "to remember every step."
        ),
        3: (
            "Your clients experience a consistent, structured onboarding process — and that matters "
            "more than most business owners realize. A reliable onboarding workflow sets the tone for "
            "the entire client relationship, reduces early-stage confusion and questions, and frees "
            "you up to focus on delivering results rather than managing logistics. This is a sign of "
            "a business that takes its client experience seriously, and it's a strong foundation for "
            "scaling your capacity."
        ),
        4: (
            "Your delivery system is operating at a level where the business itself guides clients "
            "through each stage of their experience with you. Automated transitions from onboarding "
            "to fulfillment to retention mean that nothing falls through the cracks, every client "
            "moves through a consistent journey, and your time is protected for the high-value work "
            "that actually requires you. This is the kind of infrastructure that makes growth "
            "sustainable rather than overwhelming."
        ),
    },
    "q7": {
        1: (
            "Sending invoices manually for every transaction works — but it adds friction to both "
            "sides of the exchange. You spend time creating and tracking invoices, and your clients "
            "have an extra step between deciding to work with you and actually paying. Beyond the "
            "administrative load, manual invoicing also makes it harder to offer things like payment "
            "plans, recurring billing, or instant-access products. Streamlining even part of your "
            "payment process removes a barrier that may be slowing down your cash flow."
        ),
        2: (
            "Accepting payments online is a real step forward — it removes the friction of manual "
            "invoicing and makes it easy for clients to pay you. The next layer is connecting your "
            "payment process to the rest of your business systems, so that when someone pays, "
            "something happens automatically: they receive a confirmation, get added to the right "
            "pipeline stage, or are triggered into an onboarding sequence. Right now, payment and the "
            "rest of your workflow are likely operating somewhat separately, which creates manual work "
            "to bridge the gap."
        ),
        3: (
            "Your payment system is connected to your business operations in a meaningful way. "
            "When someone completes a purchase, the process doesn't stop at the transaction — "
            "they're moved into the right workflow automatically, they receive confirmation, and "
            "the next steps are triggered without you having to intervene. This kind of integration "
            "reduces manual work, creates a smoother client experience, and makes your revenue "
            "process feel like a system rather than a series of individual tasks."
        ),
        4: (
            "Your payments and offers infrastructure is sophisticated and revenue-optimized. "
            "You're not just accepting payments — you're using your checkout process strategically, "
            "with recurring billing, offer stacking, and automated workflows that maximize the "
            "value of every transaction. This level of maturity means your business can generate "
            "and manage revenue at scale without proportionally increasing the manual work required."
        ),
    },
    "q8": {
        1: (
            "Every business has a database of people who expressed interest, worked with them in "
            "the past, or signed up at some point and then went quiet. That list is one of the most "
            "underutilized assets a business owner has — because those people already know who you "
            "are, which means the trust barrier is much lower than it is with a cold audience. "
            "Not having a reactivation system in place right now simply means that revenue "
            "opportunity is sitting dormant. It doesn't take a complex campaign to begin tapping into it."
        ),
        2: (
            "You're already doing something most business owners don't — you occasionally reach "
            "back out to people who've gone quiet or haven't heard from you in a while. The challenge "
            "with doing this manually is that it's inconsistent and dependent on you having the time "
            "and bandwidth to make it happen. Occasional outreach is better than none, but turning "
            "that manual habit into a structured campaign means it happens reliably, not just when "
            "you think of it."
        ),
        3: (
            "You're actively working your existing database, and that's a competitive advantage most "
            "business owners overlook. Structured reactivation campaigns mean you're not relying "
            "solely on new leads to generate revenue — you're also nurturing relationships with people "
            "who already have some level of connection to your business. This is a far more efficient "
            "path to revenue than constantly acquiring new contacts, and it reflects a mature "
            "understanding of how sustainable businesses grow."
        ),
        4: (
            "Your reactivation system is running at a level where your existing database is "
            "continuously being worked, not just occasionally touched. Lifecycle-based automation "
            "means that contacts move through relevant sequences based on their behavior and history, "
            "and Outreach AI means that scale doesn't require proportional manual effort. This is "
            "one of the highest-leverage capabilities a business can develop — monetizing what "
            "you've already built rather than constantly chasing new audiences."
        ),
    },
    "q9": {
        1: (
            "Reviews are one of the most powerful trust signals a potential client can encounter — "
            "and for many people, they're one of the first things they look for before deciding to "
            "reach out. Not having a system to generate or manage reviews means that your reputation "
            "is being built passively, through whoever happens to leave feedback on their own. "
            "For a business serving other women entrepreneurs, social proof is especially important — "
            "people want to know that someone like them has had a great experience working with you."
        ),
        2: (
            "Asking for reviews occasionally shows that you understand their value — and you're "
            "likely getting some great feedback as a result. The limitation is that manual requests "
            "are easy to forget in the flow of running a business, which means your review volume "
            "stays lower than it could be. A structured process for requesting reviews can "
            "significantly increase the number of people who take the time to share their experience."
        ),
        3: (
            "You have a consistent process for asking clients to share their experience, which means "
            "your reputation is being actively built rather than left to chance. A structured review "
            "workflow also means you're reaching clients at the right moment — when the experience is "
            "fresh and they're most likely to respond positively. This kind of system compounds over "
            "time, steadily building the social proof that makes it easier for new clients to say yes."
        ),
        4: (
            "Your reputation system is running on autopilot in the best possible way. Reviews are "
            "being requested automatically at the right moments, responses are managed consistently, "
            "and follow-up workflows ensure that no feedback — positive or critical — goes unaddressed. "
            "This level of reputation management builds trust at scale and creates a compounding "
            "asset that continues to work for your business long after the initial setup."
        ),
    },
    "q10": {
        1: (
            "Not using AI tools in your engagement process right now is completely fine — and in "
            "many cases, it's the right call. AI tools work best when they're layered on top of "
            "solid foundational systems. If the underlying structure of your business is still being "
            "built out, adding AI before those foundations are in place often creates more complexity "
            "than it solves. When your systems are ready, AI can meaningfully accelerate your response "
            "speed, qualification process, and client engagement — but the foundation comes first."
        ),
        2: (
            "Having AI tools in place but not yet integrated into your workflows is a common "
            "in-between stage — and it's worth being honest about what it means. "
            "Tools that aren't connected to your systems and processes aren't yet "
            "working for your business; they're just present. Before expanding your AI stack, the "
            "priority is making sure what you've already installed is actually doing something — "
            "connected to your CRM, triggering the right workflows, and responding in a way that's "
            "consistent with your brand."
        ),
        3: (
            "Your AI tools aren't just installed — they're doing real work inside your business. "
            "Integration into qualification and reminder workflows means that AI is actively supporting "
            "supporting your engagement process, reducing manual effort, and improving response "
            "speed in ways that your clients can feel. This is the stage where AI begins to pay "
            "for itself, and it creates a strong foundation for expanding its role as your systems "
            "continue to mature."
        ),
        4: (
            "AI is functioning as a core part of how your business engages with leads and clients. "
            "Voice and conversational agents are handling qualification, follow-up, and engagement "
            "at a level of scale and speed that would be impossible to replicate manually. This "
            "represents a significant operational advantage — your business can respond immediately, "
            "consistently, and at any hour, without requiring your personal time for every interaction. "
            "It's a model that supports growth without proportionally increasing your workload."
        ),
    },
    "q11": {
        1: (
            "Running a business without consistent metrics tracking often means making decisions "
            "based on how things feel rather than what the data shows. That can work for a while — "
            "intuition is a real skill — but it also means it's hard to know what's actually driving "
            "your results, what's costing you money or time, and where the highest-leverage "
            "improvements are hiding. Building even a simple tracking habit — checking a few key "
            "numbers on a regular schedule — creates a feedback loop that makes your decisions more "
            "grounded over time."
        ),
        2: (
            "You're paying attention to your results, which is more than many business owners do. "
            "The challenge with occasional check-ins is that they don't build a pattern — it's hard "
            "to spot trends, catch problems early, or make confident decisions when your data review "
            "is irregular. A simple, structured weekly or monthly review doesn't need to be complex. "
            "Even fifteen minutes with the right three or four numbers can dramatically improve the "
            "quality of decisions you make about where to focus your energy."
        ),
        3: (
            "You're operating with real visibility into your business. Regular dashboard reviews mean "
            "you're catching what's working and what isn't before small problems become big ones, and "
            "adjusting workflows based on actual data rather than assumptions. This is the kind of "
            "operational discipline that compounds — the more consistently you review and adjust, the "
            "more refined your systems become, and the more predictable your results."
        ),
        4: (
            "Your business is running with a genuine improvement loop. You're not just tracking "
            "surface metrics — you're following performance through the entire lifecycle, "
            "understanding where leads come from and what drives them to convert, and using that "
            "intelligence to continuously refine your systems. This level of reporting maturity "
            "means you can scale with confidence, because you understand the mechanics of your "
            "growth well enough to repeat and amplify what's working."
        ),
    },
    "q12": {
        1: (
            "Most of the marketing conversation in the business world focuses on getting new clients — "
            "but the revenue that's often easiest to generate is from people who've already worked "
            "with you and had a good experience. Without a structured retention strategy, that "
            "opportunity is largely untapped. Your existing clients already trust you, which means "
            "the barrier to a second purchase, an upgrade, or a referral is much lower than it is "
            "for a brand new contact. Building even a simple retention system is one of the most "
            "direct paths to sustainable revenue growth."
        ),
        2: (
            "You're already thinking about the lifetime value of your clients, which is a healthy "
            "instinct. Occasional upsell offers mean that some of your clients are hearing about "
            "additional ways you can help them — and some of them are likely saying yes. The "
            "limitation is that manual, occasional offers are inconsistent and dependent on your "
            "memory and timing. A structured approach means every client is given the right offer "
            "at the right moment, not just the ones you happen to think of on a good day."
        ),
        3: (
            "You have a deliberate strategy for staying in relationship with your clients after the "
            "initial work is done. Planned offers and renewal reminders mean that the conversation "
            "doesn't end when a project closes — you're creating natural opportunities for clients "
            "to continue working with you. This is exactly how long-term client relationships and "
            "predictable revenue are built, and it signals a real maturity in how you think about "
            "the value you bring over time."
        ),
        4: (
            "Your retention system is running continuously in the background, ensuring that every "
            "client is being nurtured toward their next step with your business. Automated workflows "
            "mean that upsell opportunities, renewal reminders, and expansion offers are delivered "
            "at exactly the right time — not based on when you remember to send something, but based "
            "on where each client actually is in their journey. This kind of system maximizes the "
            "lifetime value of every client relationship and creates a compounding revenue base."
        ),
    },
}

# ---------------------------------------------------------------------------
# Question section names (for summary formatting)
# ---------------------------------------------------------------------------
SECTION_NAMES = {
    "q1": "Clarity & Offer System",
    "q2": "Presence System",
    "q3": "Lead Capture System",
    "q4": "Customer Journey / CRM System",
    "q5": "Nurture & Follow-Up System",
    "q6": "Delivery System",
    "q7": "Payments & Offers System",
    "q8": "Reactivation & Outreach System",
    "q9": "Reputation & Reviews System",
    "q10": "AI Engagement & Conversion System",
    "q11": "Reporting & Improvement System",
    "q12": "Lifetime Value & Retention System",
}

SECTION_QUESTIONS = {
    "q1": "How clearly defined is your primary offer?",
    "q2": "What best describes your online presence?",
    "q3": "How are leads captured?",
    "q4": "How structured is your CRM and customer journey?",
    "q5": "What follow-up happens after inquiry?",
    "q6": "How standardized is client onboarding and fulfillment?",
    "q7": "How are payments and offers handled?",
    "q8": "Do you actively monetize your existing database?",
    "q9": "How do you generate and manage reviews?",
    "q10": "How are AI tools used in your engagement process?",
    "q11": "How do you track and improve performance?",
    "q12": "How do you increase revenue from existing clients?",
}

# ---------------------------------------------------------------------------
# Foundation signal mapping:
# Defines which encoded answer values count as a "Foundation signal" per question.
# ---------------------------------------------------------------------------
FOUNDATION_SIGNALS = {
    "q1":  [1, 2],  # A (Foundation) and B (Foundation/Growth bridge)
    "q2":  [1, 2],  # A (Foundation) and B (Foundation stable)
    "q3":  [1, 2],  # A (Foundation) and B (Foundation)
    "q4":  [1, 2],  # A (Foundation) and B (Foundation/Growth)
    "q5":  [1, 2],  # A (Foundation) and B (Foundation)
    "q6":  [1],     # A only (B = Growth early)
    "q7":  [1],     # A only (B = Growth early)
    "q8":  [1],     # A (Foundation/Growth — counted as Foundation)
    "q9":  [1],     # A (Foundation/Growth — counted as Foundation)
    "q10": [],      # Neutral baseline — not counted
    "q11": [1],     # A only (B = Growth early)
    "q12": [1],     # A only (B = Growth)
}

# ---------------------------------------------------------------------------
# Priority actions and anti-priority warnings per pathway
# ---------------------------------------------------------------------------
PATHWAY_PRIORITY_ACTIONS = {
    "Foundation": [
        "Define and lock in ONE primary offer with a clear call to action before building anything else.",
        "Build a simple, structured website with a single clear conversion path.",
        "Set up a basic CRM or pipeline to track every lead and client in one place.",
        "Implement at minimum an automated email confirmation after every inquiry.",
        "Create a repeatable onboarding checklist so every client experience starts consistently.",
    ],
    "Growth": [
        "Standardise your client onboarding and fulfillment into a documented workflow.",
        "Connect your payment system to automated confirmation and onboarding sequences.",
        "Launch a structured reactivation campaign to your existing database.",
        "Implement a consistent review request process at the close of every client engagement.",
        "Set up a regular metrics review cadence — weekly or monthly — using a simple dashboard.",
    ],
    "Optimization": [
        "Integrate AI tools into your qualification, follow-up, and engagement workflows.",
        "Build lifecycle-based reactivation sequences that trigger from contact behaviour.",
        "Implement full lifecycle tracking and attribution to understand every conversion driver.",
        "Develop automated retention and expansion workflows for existing clients.",
        "Add order bumps, subscription options, and automated upsell sequences to your payment flows.",
    ],
}

PATHWAY_ANTI_PRIORITY = {
    "Foundation": [
        "Don't invest in paid advertising before your offer, landing page, and lead capture are solid.",
        "Don't layer AI tools onto systems that don't yet exist — foundations come first.",
        "Don't attempt to build retention workflows until your delivery and onboarding are consistent.",
    ],
    "Growth": [
        "Don't invest heavily in AI tools until your CRM is being used consistently.",
        "Don't build complex reactivation automations before your core follow-up sequences are reliable.",
        "Don't expand to multiple offers until your primary offer's systems are fully operational.",
    ],
    "Optimization": [
        "Don't over-automate at the expense of personal touchpoints that drive client loyalty.",
        "Don't onboard new AI systems without first auditing integration with your existing CRM and workflows.",
        "Don't expand to new markets before lifecycle tracking shows consistent performance in your current market.",
    ],
}

PATHWAY_GRADUATION_OUTLOOK = {
    "Foundation": (
        "Once you have one clear offer, a structured website, a basic CRM, and automated "
        "follow-up in place, you'll be ready to move into the Growth pathway — where your "
        "focus shifts from building the basics to running them reliably and adding delivery "
        "and payment systems that scale with your client volume."
    ),
    "Growth": (
        "Once you have standardised delivery, integrated payments, a structured reactivation "
        "strategy, and consistent metrics review in place, you'll be ready to move into the "
        "Optimization pathway — where your focus shifts to AI-assisted engagement, lifecycle "
        "automation, and continuous performance improvement."
    ),
    "Optimization": (
        "You are operating at the highest maturity level. The focus now is compounding what's "
        "already working — expanding AI capabilities, deepening lifecycle intelligence, and "
        "building the retention and expansion infrastructure that turns client relationships "
        "into long-term, compounding revenue."
    ),
}


# ---------------------------------------------------------------------------
# Deterministic rule-based classifier (used for training data generation
# and as a cross-check alongside the logistic regression model).
# ---------------------------------------------------------------------------
def rule_based_classify(encoded_responses: dict) -> str:
    """
    Classify a set of encoded responses (q1–q12, values 1–4) into a pathway.

    Args:
        encoded_responses: dict mapping question key (e.g. 'q1') to int (1–4).

    Returns:
        Pathway string: 'Foundation', 'Growth', or 'Optimization'.
    """
    # Count Foundation signals
    foundation_signals = sum(
        1
        for q, signals in FOUNDATION_SIGNALS.items()
        if encoded_responses.get(q, 0) in signals
    )

    # Rule 1: 3+ Foundation signals → Foundation
    if foundation_signals >= 3:
        return "Foundation"

    # Critical Foundation blockers (prevent Optimization)
    q1_val = encoded_responses.get("q1", 1)
    q4_val = encoded_responses.get("q4", 1)
    q5_val = encoded_responses.get("q5", 1)

    has_critical_blocker = (
        q1_val == 1         # unclear offer
        or q4_val <= 2      # no structured CRM
        or q5_val <= 2      # no follow-up automation
    )

    # Optimization-level (D = 4) answers
    optimization_signals = sum(1 for v in encoded_responses.values() if v == 4)

    # Strong CRM and reporting required for Optimization
    strong_crm = encoded_responses.get("q4", 1) >= 3
    strong_reporting = encoded_responses.get("q11", 1) >= 3

    # Rule 2: Optimization conditions
    if (
        not has_critical_blocker
        and optimization_signals >= 4
        and strong_crm
        and strong_reporting
    ):
        return "Optimization"

    # Rule 3: Default → Growth
    return "Growth"
