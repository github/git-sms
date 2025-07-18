# Git SMS 📲 

Idea: Enabling GitHub collaboration, automation, and AI interaction via SMS text messages.

> **DISCLAIMER:** Proof-of-concept, insecure by design, do not use in production, not a GitHub product. **As-Is, At Your Own Risk.**

## What It Is

Git SMS is an open source project that shows a proof of concept to enable users to interact with GitHub and AI via SMS. Simply by texting a number you could summarize issues, pull requests, repos, and receive updates, and more.

This workflow brings the power of open source and AI to people who may not have consistent access to laptops or high-speed internet.

## Why It Matters

93% of the world has access to SMS.

Fewer than 65% have reliable internet or a smartphone.

Everyone should be able to participate in global innovation, contribute to the open source community, learn from others and interact 
with AI.

This system enables:
* Participation in open source and AI regardless of location or hardware
* Communication over SMS network
* Interaction with GitHub through a plain text interface

## Use Cases

This project can be adapted for a wide variety of scenarios, from individual developer productivity to large-scale community initiatives.

*Bridging the Digital Divide & Empowering Communities*

- **Offline First Contribution:** Allow individuals in areas with limited, expensive, or unreliable internet to contribute to open source projects by opening issues, commenting, and receiving updates via SMS.
- **Bug Reporting from the Field:** Enable users of open source software in remote locations (e.g., agricultural tech, water management systems) to report bugs and provide feedback directly from their location using any mobile phone.
- **Community Polling & Governance:** Use SMS to allow community members to vote on project features, governance decisions, or new initiatives, ensuring everyone has a voice regardless of their internet access.
- **Educational Access:** Facilitate coding education by allowing students to interact with repositories, submit assignments as issues, and get feedback from instructors, all without requiring a computer or broadband.
- **Citizen Journalism & Data Collection:** Empower individuals to submit reports, news tips, or data (e.g., local election monitoring, environmental observations) to a centralized repository as structured issues via SMS.

*Developer & Project Manager Productivity*

- **On the Go Issue Management:** Quickly create an issue to capture a bug or idea right when it occurs to you, whether you're commuting, in a meeting, or away from your desk.
- **Emergency Code Review & Merge:** In critical situations, a project maintainer could receive an urgent pull request notification and approve a merge for a hotfix directly from their phone.
- **Quick Status Checks:** Get a quick list of open issues, recent commits, or the status of pull requests for a repository while on the move without needing to open a laptop.
- **Simple Project Scaffolding:** Create a new repository from a predefined template with a single SMS command, streamlining the start of new projects.
- **Team Status Updates:** Allow team members to provide quick end-of-day status updates by commenting on a designated "daily stand-up" issue via text message.

*DevOps & Automation*

- **Triggering CI/CD Pipelines:** Initiate a build, test, or deployment process through a GitHub Actions workflow triggered by a specific SMS command (e.g., `DEPLOY <app> to staging`).
- **Infrastructure Status & Control:** Create workflows where you can request the status of production systems (`STATUS <service>`) or trigger a restart of a service (`RESTART <service>`) via SMS.
- **Incident Response & Management:** In the event of a production outage, receive an automated SMS alert and be able to create an incident issue, notify the team, and post updates from your phone.
- **Release Management:** Trigger a release workflow that tags a new version, generates release notes from recent commits, and publishes the release, all initiated by an SMS command.
- **Automated Reporting:** Schedule a GitHub Action to send a summary of weekly repository activity (e.g., new issues, closed PRs) to a list of stakeholders via SMS.

*AI-Powered & Natural Language Interaction*

- **Code & Project Summarization:** Get a high-level summary of a complex pull request, a lengthy issue discussion, or even the purpose of an entire repository by sending a simple question like, "Summarize the latest PR in owner/repo."
- **Natural Language Bug Reports:** Allow non-technical users to report issues in plain language (e.g., "The app crashes when I click the blue button"). An LLM backend can parse this, add appropriate labels, and create a well-formatted GitHub issue.
- **Code Generation & Scaffolding:** Request simple code snippets or file creation via natural language (e.g., "Create a new Python file in repo with a function to calculate factorial").
- **Knowledge Base Queries:** Use SMS to ask questions about a project's documentation. The AI could search the repository's markdown files and return a concise answer.
- **AI-Assisted Task Management:** Tell the system, "Remind me to review the auth PR tomorrow," and have it create a new issue assigned to you with a due date.

*Beyond Software Development*

- **Field Service & Maintenance Reporting:** Technicians in the field can report equipment status, log maintenance tasks, or request parts by sending an SMS that creates an issue in a project repository.
- **Disaster Response & Coordination:** Enable first responders to report incidents, request resources, and provide status updates via SMS, which would populate a centralized dashboard or issue tracker for coordination.
- **Scientific Research & Citizen Science:** Allow researchers and volunteers in the field without internet to submit data points, observations, or findings to a project repository via text message.
- **Inventory & Asset Management:** Use SMS to log the status or location of physical assets, creating a commit or issue in a repository that serves as a lightweight asset tracking system.

## Demo 

[Simulation](https://gh.io/git-sms-simulation)

## ✅ Maintainers

* Ashley Wolf - @ashleywolf
* Dan Velton - @dvelton
