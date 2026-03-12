# Documentation Index - DBT Demo Project

Complete guide to all documentation files.

## Quick Access

| Need Help With? | Read This | Time |
|---|---|---|
| **Getting started** | [QUICK_START.md](QUICK_START.md) | 5 min |
| **Full overview** | [README.md](README.md) | 20 min |
| **How it works** | [ARCHITECTURE.md](ARCHITECTURE.md) | 15 min |
| **What data means** | [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | 10 min |
| **Write new models** | [DEVELOPMENT.md](DEVELOPMENT.md) | 15 min |
| **Something broke** | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Quick lookup |

---

## File Guide

### 📘 QUICK_START.md
**For:** First-time users, demos
**Content:**
- 5-minute setup guide
- Basic commands
- Verify everything works

**Start here if you're new!**

---

### 📗 README.md
**For:** Complete project overview
**Content:**
- Project description
- Installation instructions
- DBT models explanation
- Data quality tests
- How to run commands
- Troubleshooting basics
- Best practices
- Performance tuning

**Read after QUICK_START for full context**

---

### 🏗️ ARCHITECTURE.md
**For:** Understanding system design
**Content:**
- High-level architecture diagrams
- Data flow pipeline
- Container structure
- Component interactions
- Entity relationships
- Database schema design
- Scalability considerations
- Security recommendations

**Read if you need to: modify architecture, scale system, understand design decisions**

---

### 📚 DATA_DICTIONARY.md
**For:** Understanding the data
**Content:**
- Raw table schema & definitions
- Staging layer transformations
- Mart table descriptions
- Column-by-column reference
- Data lineage
- Business metrics
- Data types
- Data quality summary

**Read if you need to: understand what data means, write queries, add new columns**

---

### 👨‍💻 DEVELOPMENT.md
**For:** Development workflow
**Content:**
- Development environment setup
- Daily development cycle
- Adding new models
- Writing tests
- Debugging tools
- Best practices
- Common development tasks
- Performance optimization

**Read if you need to: add new models, write tests, debug issues**

---

### 🔧 TROUBLESHOOTING.md
**For:** Problem solving
**Content:**
- Docker & container troubleshooting
- Database connection issues
- Data loading problems
- DBT model issues
- Test failures
- Performance problems
- FAQ
- Debug techniques

**Read if: something is broken, you get error messages**

---

## Reading Paths

### Path 1: New User (0 → productive)
```
1. QUICK_START.md (5 min)
             ↓
   ✓ System is running, data is loaded
             ↓
2. README.md sections "Concepts" (10 min)
             ↓
   ✓ Understand what project does
             ↓
3. DATA_DICTIONARY.md (5 min)
             ↓
   ✓ Can write basic queries
             ↓
4. Bookmark TROUBLESHOOTING.md
```
**Total: ~30 minutes**

### Path 2: Data Analyst (write queries, understand data)
```
1. QUICK_START.md (5 min)
2. DATA_DICTIONARY.md (full) (15 min)
3. README.md → "SQL Cheat Sheet" (10 min)
4. Use TROUBLESHOOTING.md if errors
```
**Total: ~30 minutes**

### Path 3: Data Engineer (develop models)
```
1. QUICK_START.md (5 min)
2. ARCHITECTURE.md (15 min)
3. DEVELOPMENT.md (full) (30 min)
4. Bookmark TROUBLESHOOTING.md
```
**Total: 50 minutes**

### Path 4: DevOps/SRE (deploy, scale, secure)
```
1. README.md (20 min)
2. ARCHITECTURE.md → "Deployment Strategy" (10 min)
3. ARCHITECTURE.md → "Security" (5 min)
4. See scalability section (10 min)
```
**Total: 45 minutes**

### Path 5: Troubleshooting (something is broken)
```
1. Identify error type
2. Find section in TROUBLESHOOTING.md
3. Follow step-by-step solution
4. Check README.md "Troubleshooting" section
```
**Total: Varies**

---

## By Topic

### 🚀 Getting Started
- [QUICK_START.md](QUICK_START.md) - 5-minute setup
- [README.md](README.md#installation-instructions) - Full installation steps
- [ARCHITECTURE.md](ARCHITECTURE.md#deployment-strategy) - Deployment options

### 📊 Understanding Data
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - All table definitions
- [ARCHITECTURE.md](ARCHITECTURE.md#data-flow-pipeline) - How data flows
- [README.md](README.md#cấu-trúc-dữ-liệu) - Data structure overview

### 🛠️ Development
- [DEVELOPMENT.md](DEVELOPMENT.md) - Complete dev guide
- [README.md](README.md#best-practices) - Best practices
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md#dbt-model-issues) - DBT issues

### 🏗️ Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture
- [README.md](README.md#docker-configuration) - Docker setup
- [ARCHITECTURE.md](ARCHITECTURE.md#technology-stack) - Tech stack

### 🔐 Security & DevOps
- [ARCHITECTURE.md](ARCHITECTURE.md#security-considerations) - Security
- [README.md](README.md#performance-tuning) - Performance
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md#docker--container-issues) - Deployment issues

### ❓ Problem Solving
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - All issues
- [README.md](README.md#khắc-phục-sự-cố) - Common issues
- [DEVELOPMENT.md](DEVELOPMENT.md#debugging--troubleshooting) - Debug techniques

---

## Common Questions

**Q: Should I read all docs?**
A: No! Start with QUICK_START.md, then pick 1-2 files based on your role.

**Q: I'm in a hurry, what's the minimum?**
A: QUICK_START.md (5 min) + DATA_DICTIONARY.md (5 min) = 10 minutes to be productive.

**Q: I need to add a new data model**
A: Read DEVELOPMENT.md section "Adding New Models"

**Q: Something is broken**
A: Go to TROUBLESHOOTING.md and find your error type

**Q: I need to deploy this to production**
A: Read ARCHITECTURE.md "Deployment Strategy" + "Security Considerations"

**Q: What does column X mean?**
A: Look in DATA_DICTIONARY.md, find the table, search for column name

---

## Document Features

### 🔍 Easy Search
All files are markdown - use Ctrl+F to find topics

### 📑 Table of Contents
Each file starts with clickable table of contents

### 💬 Code Examples
Practical examples throughout for running commands and writing queries

### 📋 Quick Reference
Reference sections for common tasks at bottom of files

### 🔗 Cross-Linking
Files reference each other - follow links to dive deeper

---

## Version Info

**Documentation Version:** 1.0
**Project Version:** 1.0
**Last Updated:** 2026-03-12

---

## Summary

| File | Purpose | Audience | Time |
|------|---------|----------|------|
| QUICK_START.md | Get running | Everyone | 5 min |
| README.md | Complete reference | Data people | 20 min |
| ARCHITECTURE.md | System design | Engineers | 15 min |
| DATA_DICTIONARY.md | Data reference | Analysts | 10 min |
| DEVELOPMENT.md | How to develop | Developers | 15 min |
| TROUBLESHOOTING.md | Fix problems | Everyone | Variable |
| INDEX.md (this file) | Navigate docs | Everyone | 5 min |

---

## Next Steps

1. **New here?** → Read [QUICK_START.md](QUICK_START.md)
2. **Want overview?** → Read [README.md](README.md)
3. **Want to develop?** → Read [DEVELOPMENT.md](DEVELOPMENT.md)
4. **Something broke?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
5. **Need data details?** → Check [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
6. **Understanding design?** → Read [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Happy learning! 🚀**

---

## Document Statistics

```
Total Documentation Files: 7 (including this index)
Total Pages: ~100+ pages equivalent
Total Sections: 150+
Total Code Examples: 200+
Estimated Reading Time: 
  - Beginner: 1-2 hours complete
  - Intermediate: 1 hour specific sections
  - Expert: 30 min lookup-based
```

---

**Last Updated:** 2026-03-12
