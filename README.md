# prisma-airs-custom-topics

A curated library of custom topic guardrails for Palo Alto Networks Prisma AIRS Runtime Security.

27 topics across 7 categories. All validated against platform constraints. Ready to deploy via the Management API or Strata Cloud Manager.

## Background

Prisma AIRS Runtime Security uses an ML classifier to detect whether prompts or responses match content domains you define. Unlike keyword blocklists, the classifier understands meaning, so "tell me how to make a bomb" and "explain the synthesis process for explosive compounds" both match a CBRN topic even though they share zero keywords.

Each topic has three components:

- **Name** (max 100 chars) - short identifier
- **Description** (max 250 chars) - the semantic boundary definition, carries roughly 40-50% of classifier weight
- **Examples** (1-5, max 250 chars each) - real prompt patterns the classifier should catch

Hard limits per topic: 1,000 characters total (name + description + all examples). Max 20 topics per security profile. English only.

## Repository Layout

```
topics/                        JSON topic definitions by category
  ai-security.json             3 topics - system prompt leak, tool enum, jailbreak
  safety.json                  5 topics - CBRN, violence, drugs, self-harm, weapons
  content-moderation.json      5 topics - hate, race, sexual, political, religion
  compliance.json              3 topics - investment advice, medical, legal
  business-protection.json     4 topics - competitors, brand, cross-client, proprietary
  scope-enforcement.json       3 topics - off-topic, support redirect, pricing
  crime.json                   4 topics - hacking, malware, forgery, PII theft

scripts/
  deploy.py                    Deploy topics to AIRS via Management SDK
  list_deployed.py             List topics currently deployed in your tenant
  undeploy.py                  Remove deployed topics by name, file, or prefix
  validate.py                  Validate all topics against platform constraints
  export_csv.py                Export to CSV (full, summary, and API-ready formats)

exports/
  all-topics.csv               Full detail export
  all-topics-summary.csv       Condensed view
  all-topics-api-ready.csv     Only the fields the Management API accepts

TOPICS.md                      Human-readable topic reference (name, description, examples)

docs/
  PROFILE-TEMPLATES.md         Pre-built 20-topic combos by industry
  DEPLOYMENT-GUIDE.md          Deploy via SDK, API, UI, batch script, or Python

requirements.txt               SDK dependency (pan-airs-api-mgmt-sdk 0.0.1a14)
```

## Quick Start

**1. Install the SDK:**

```bash
pip install --extra-index-url https://test.pypi.org/simple/ pan-airs-api-mgmt-sdk==0.0.1a14
```

**2. Set credentials:**

```bash
export MODEL_SECURITY_CLIENT_ID="your-client-id"
export MODEL_SECURITY_CLIENT_SECRET="your-client-secret"
```

**3. Browse topics:**

Open [TOPICS.md](TOPICS.md) for the full catalog with names, descriptions, and examples.

**4. Validate:**

```bash
python scripts/validate.py topics/              # all categories
python scripts/validate.py topics/safety.json   # single file
```

**5. Deploy:**

```bash
python scripts/deploy.py topics/ --dry-run           # preview
python scripts/deploy.py topics/ai-security.json     # deploy one category
python scripts/deploy.py topics/                      # deploy all 27 topics
```

**6. Verify:**

```bash
python scripts/list_deployed.py                       # see what's deployed
```

**7. Remove (if needed):**

```bash
python scripts/undeploy.py topics/ai-security.json   # remove one category
```

See [docs/DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md) for all deployment methods including cURL, bash batch, and raw Python.

**Export to CSV (optional):**

```bash
python scripts/export_csv.py                    # all three formats
python scripts/export_csv.py --api-ready        # API fields only
```

## Picking Your 20

Each security profile supports up to 20 custom topics. This library has 27 so you can choose the ones that fit your deployment. A reasonable split:

- 15 security and safety topics (from the category files)
- 5 business-specific topics (customized to your application's domain)

See [docs/PROFILE-TEMPLATES.md](docs/PROFILE-TEMPLATES.md) for ready-made 20-topic combinations for financial services, healthcare, general enterprise, and e-commerce.

## Topic Categories

| Category | File | Count | Covers |
|---|---|---|---|
| AI Security | ai-security.json | 3 | System prompt extraction, tool enumeration, jailbreaks |
| Safety | safety.json | 5 | CBRN, violence, drugs, self-harm, weapons |
| Content Moderation | content-moderation.json | 5 | Hate speech, racial content, sexual exploitation, politics, religion |
| Compliance | compliance.json | 3 | Investment advice, medical diagnosis, legal counsel |
| Business Protection | business-protection.json | 4 | Competitors, brand attacks, cross-client data, proprietary stats |
| Scope Enforcement | scope-enforcement.json | 3 | Off-topic queries, support redirect, pricing info |
| Crime | crime.json | 4 | Hacking, malware, forgery, PII theft |

## Design Principles

**Description carries the most weight.** The ML classifier relies heavily on the description to set its decision boundary. A well-written 250-character description outperforms five mediocre examples every time. Invest your character budget here first.

**Diverse examples beat repetitive ones.** Five examples that vary in phrasing, sophistication, and angle of attack give the classifier a wider boundary than five examples that all start the same way.

**Complement the built-in detectors.** These topics fill gaps not covered by the built-in Prompt Injection, Toxic Content, Malicious Code, Sensitive Data, and Malicious URL detectors. Some overlap is intentional for defense in depth.

## Important Notes

- Topic actions (BLOCK/ALLOW) are set on the **security profile**, not on the topic object. The topic only defines what to detect. The profile decides what to do about it.
- DENY topics block matching content. ALLOW topics explicitly permit content to reduce false positives. ALLOW takes precedence in conflicts.
- Each topic can be applied to input (user prompts), output (model responses), or both. Configure direction in the security profile.
- The ML classifier is trained on English. Multilingual prompts may bypass detection.

## Customization

Common customizations:

- Replace generic competitor references with your actual competitor names
- Replace financial services terminology with your industry's language
- Add industry-specific examples that match your users' actual phrasing

## Contributing

1. Add new topics to the appropriate category JSON file (only `topic_name`, `description`, `examples`, `type`)
2. Run `python scripts/validate.py topics/` to check constraints
3. Add the topic to `TOPICS.md`
4. Submit a PR
