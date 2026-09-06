# Enterprise IT Support Master Knowledge Base (1,000-Page Technical Reference)

## Project Overview
This repository contains an enterprise-grade technical knowledge base dataset specifically engineered for powering, fine-tuning, and benchmarking **Retrieval-Augmented Generation (RAG) AI IT Support Assistants**.

The dataset consolidates authoritative vendor technical documentation from **Microsoft Learn, Cisco, CISA, NIST, Red Hat, Ubuntu, AWS, and VMware**.

All technical data across 10 enterprise domains and 100 deep technical runbooks is provided in two master single-file formats:
1. **Master PDF:** `pdfs/it_support_knowledge_base_1000pages.pdf`
2. **Master Markdown:** `markdown/it_support_knowledge_base_1000pages.md`

---

## Dataset Summary
- **Collection Date:** 2026-09-06
- **Total Enterprise Domains:** 10 Domains
- **Total Technical Runbooks:** 100 Comprehensive Modules
- **Master PDF Deliverable:** `pdfs/it_support_knowledge_base_1000pages.pdf`
- **Master Markdown Deliverable:** `markdown/it_support_knowledge_base_1000pages.md`
- **Evaluation Benchmark:** 100 Curated Benchmark Queries (`evaluation_questions.json`)
- **Metadata Index:** `metadata.json`
- **Sources CSV:** `sources.csv`

---

## Directory Structure

```text
it-support-rag-dataset/
├── pdfs/
│   └── it_support_knowledge_base_1000pages.pdf   # Master PDF (All 100 runbooks)
├── markdown/
│   └── it_support_knowledge_base_1000pages.md    # Master Markdown (All 100 runbooks)
├── metadata.json                                  # Document metadata index with verified URLs
├── evaluation_questions.json                     # Benchmark question set (100 queries across 10 domains)
├── sources.csv                                    # CSV mapping of runbooks to official URLs and metadata
└── README.md                                      # Dataset documentation & RAG implementation guide
```
