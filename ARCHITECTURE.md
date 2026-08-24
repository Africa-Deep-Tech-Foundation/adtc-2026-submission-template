# VECTOR Afya MVP Architecture

```text
USER
  |
  v
HYBRID ROUTING
  |-- explicit category ------------------+
  |                                       |
  +-- Auto-detect --> deterministic router|
                                          v
                         CONFIRMED CATEGORY
                                          |
              +---------------------------+---------------------------+
              |             |             |                           |
        Clinical Info   Medical Q&A   Triage Support          Patient Education
              |             |             |                           |
              +-------------+-------------+---------------------------+
                                          |
                                          v
                       SAFETY / ASSESSMENT & ESCALATION
                                          |
                                          v
                         CATEGORY + GLOBAL SAFETY PROMPT
                                          |
                                          v
                         LOCAL QWEN2.5-3B / GGUF
                                          |
                                          v
                              POST-RESPONSE CHECK
                                          |
                                          v
                                        USER
```

The user-facing modes are the four categories above. Assessment and escalation is cross-cutting safety behavior.
