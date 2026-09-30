# Domain Packs

A domain pack contains the business-specific configuration that sits above the reusable conversational engine.

The core engine should not need to be rewritten when the business domain changes.

## Domain pack responsibilities

A domain pack can define:

- identity and purpose of the assistant
- knowledge sources
- workflows
- available tools
- business policies
- response behavior

## Planned structure

```text
domains/
├── README.md
└── demo_ecommerce/
    └── domain.json
```

The domain configuration is intentionally kept separate from model/provider code.

The next implementation layer will load this configuration into the conversational engine. Knowledge retrieval, tool execution, and workflow routing will be added incrementally rather than being mixed into the current intake logic.
