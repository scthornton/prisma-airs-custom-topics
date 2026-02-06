# Security Profile Templates

Pre-built 20-topic combinations for common deployment scenarios. Each template uses the maximum 20 custom topic slots.

> **Remember:** Topic actions (BLOCK/ALLOW) are set on the security profile, not the topic object. Set all DENY topics to BLOCK for both input and output directions.

---

## Template 1: Financial Services Chatbot

*For: Trading platforms, wealth management, banking assistants, investment tools*

| Slot | Topic | Category |
|---|---|---|
| 1 | `system_prompt_disclosure` | AI Security |
| 2 | `tool_capability_enumeration` | AI Security |
| 3 | `instruction_override_injection` | AI Security |
| 4 | `investment_advice_recommendations` | Compliance |
| 5 | `competitor_intelligence` | Business Protection |
| 6 | `cross_client_data_privacy` | Business Protection |
| 7 | `malicious_code_generation` | Crime |
| 8 | `political_manipulation` | Content Moderation |
| 9 | `hate_speech_discrimination` | Content Moderation |
| 10 | `brand_reputation_attacks` | Business Protection |
| 11 | `proprietary_data_disclosure` | Business Protection |
| 12 | `hacking_system_intrusion` | Crime |
| 13 | `off_topic_general_knowledge` | Scope Enforcement |
| 14 | `pii_harvesting_identity_theft` | Crime |
| 15 | `legal_counsel_advice` | Compliance |
| 16 | `pricing_commercial_terms` | Scope Enforcement |
| 17 | `platform_support_redirect` | Scope Enforcement |
| 18 | `document_identity_forgery` | Crime |
| 19 | `cbrn_weapons_content` | Safety |
| 20 | `violence_harm_instructions` | Safety |

**Why this combination:** Financial services requires investment advice blocking (SEC/FINRA), cross-client data privacy, and competitor intelligence protection.

---

## Template 2: Healthcare AI Assistant

*For: Patient portals, clinical decision support, medical research tools, health chatbots*

| Slot | Topic | Category |
|---|---|---|
| 1 | `system_prompt_disclosure` | AI Security |
| 2 | `tool_capability_enumeration` | AI Security |
| 3 | `instruction_override_injection` | AI Security |
| 4 | `medical_diagnosis_treatment` | Compliance |
| 5 | `pii_harvesting_identity_theft` | Crime |
| 6 | `malicious_code_generation` | Crime |
| 7 | `political_manipulation` | Content Moderation |
| 8 | `hate_speech_discrimination` | Content Moderation |
| 9 | `drug_synthesis_manufacturing` | Safety |
| 10 | `self_harm_concealment` | Safety |
| 11 | `cbrn_weapons_content` | Safety |
| 12 | `violence_harm_instructions` | Safety |
| 13 | `sexual_exploitation_content` | Content Moderation |
| 14 | `brand_reputation_attacks` | Business Protection |
| 15 | `legal_counsel_advice` | Compliance |
| 16 | `off_topic_general_knowledge` | Scope Enforcement |
| 17 | `religious_denigration` | Content Moderation |
| 18 | `racial_stereotyping_content` | Content Moderation |
| 19 | `cross_client_data_privacy` | Business Protection |
| 20 | `document_identity_forgery` | Crime |

**Why this combination:** Healthcare requires medical diagnosis blocking, PII protection (HIPAA), self-harm prevention, and drug synthesis blocking. Cross-client data privacy prevents patient record leakage.

---

## Template 3: General Enterprise AI Assistant

*For: Internal tools, productivity assistants, customer service chatbots, knowledge bases*

| Slot | Topic | Category |
|---|---|---|
| 1 | `system_prompt_disclosure` | AI Security |
| 2 | `tool_capability_enumeration` | AI Security |
| 3 | `instruction_override_injection` | AI Security |
| 4 | `malicious_code_generation` | Crime |
| 5 | `political_manipulation` | Content Moderation |
| 6 | `cbrn_weapons_content` | Safety |
| 7 | `hate_speech_discrimination` | Content Moderation |
| 8 | `racial_stereotyping_content` | Content Moderation |
| 9 | `religious_denigration` | Content Moderation |
| 10 | `sexual_exploitation_content` | Content Moderation |
| 11 | `violence_harm_instructions` | Safety |
| 12 | `weapons_manufacturing` | Safety |
| 13 | `drug_synthesis_manufacturing` | Safety |
| 14 | `self_harm_concealment` | Safety |
| 15 | `hacking_system_intrusion` | Crime |
| 16 | `brand_reputation_attacks` | Business Protection |
| 17 | `competitor_intelligence` | Business Protection |
| 18 | `pii_harvesting_identity_theft` | Crime |
| 19 | `document_identity_forgery` | Crime |
| 20 | `legal_counsel_advice` | Compliance |

**Why this combination:** Broad coverage across all safety and content moderation categories. Suitable as a starting point that can be customized by swapping topics for your specific domain.

---

## Template 4: E-Commerce / Retail AI

*For: Shopping assistants, product recommendation engines, customer support bots*

| Slot | Topic | Category |
|---|---|---|
| 1 | `system_prompt_disclosure` | AI Security |
| 2 | `tool_capability_enumeration` | AI Security |
| 3 | `instruction_override_injection` | AI Security |
| 4 | `malicious_code_generation` | Crime |
| 5 | `political_manipulation` | Content Moderation |
| 6 | `cross_client_data_privacy` | Business Protection |
| 7 | `competitor_intelligence` | Business Protection |
| 8 | `pii_harvesting_identity_theft` | Crime |
| 9 | `hate_speech_discrimination` | Content Moderation |
| 10 | `brand_reputation_attacks` | Business Protection |
| 11 | `hacking_system_intrusion` | Crime |
| 12 | `off_topic_general_knowledge` | Scope Enforcement |
| 13 | `pricing_commercial_terms` | Scope Enforcement |
| 14 | `sexual_exploitation_content` | Content Moderation |
| 15 | `violence_harm_instructions` | Safety |
| 16 | `cbrn_weapons_content` | Safety |
| 17 | `weapons_manufacturing` | Safety |
| 18 | `drug_synthesis_manufacturing` | Safety |
| 19 | `document_identity_forgery` | Crime |
| 20 | `platform_support_redirect` | Scope Enforcement |

**Why this combination:** E-commerce requires cross-user data privacy (purchase history isolation), competitor intelligence blocking, and strong content moderation.

---

## Customization Guide

### Swapping Topics

If a template doesn't fit your needs exactly, swap topics:

| If you don't need... | Replace with... |
|---|---|
| `investment_advice_recommendations` (fin. services only) | `weapons_manufacturing` or `religious_denigration` |
| `medical_diagnosis_treatment` (healthcare only) | `proprietary_data_disclosure` or `off_topic_general_knowledge` |
| `off_topic_general_knowledge` (general-purpose bots) | `self_harm_concealment` or `document_identity_forgery` |
| `platform_support_redirect` (no support portal) | `racial_stereotyping_content` or `legal_counsel_advice` |

### Adding ALLOW Topics

ALLOW topics explicitly permit content that might otherwise trigger false positives:

```json
{
  "topic_name": "legitimate_security_research",
  "description": "Permits discussion of security vulnerabilities, penetration testing results, CVE analysis, and defensive security measures within authorized research contexts",
  "examples": [
    "What are the OWASP Top 10 vulnerabilities for web applications",
    "How does SQL injection work and what are the best defenses",
    "Explain the CVE-2024-1234 vulnerability and recommended patches"
  ],
  "type": "ALLOW"
}
```

ALLOW topics take precedence over DENY topics when there's a classification conflict.
