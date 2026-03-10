# Contributing to Disaster Dash

Thank you for your interest in contributing to Disaster Dash! This document outlines a Milestone 3 workflow retrospective from the dashboard authors, collaboration norms for Milestone 4, and guidelines for proposing changes to the project. For questions about the contribution process, please open an issue or contact a core group member.

## Milestone 3 Retrospective

During Milestones 1–3 our team successfully developed the core functionality of Disaster Dash and maintained an active GitHub workflow using issues, a development branch (`dev`), pull requests, and a project board to track tasks. However, collaboration feedback highlighted several areas for improvement in our development process.

Some pull requests were large integration PRs created after significant local development, which made them harder to review effectively. In addition, design documentation was not always updated alongside feature development, which meant the specification document sometimes lagged behind the implementation.

After discussing this feedback as a team, we agreed to adjust our workflow to focus on smaller pull requests, clearer documentation of design decisions, and consistent peer review before merging changes.

## Collaboration Norms for Milestone 4

For the final milestone we agreed on the following collaboration practices:

- **Atomic pull requests:** Features and fixes will be submitted as smaller, focused PRs rather than large integration changes.
- **Design before code:** The specification document will be updated as design decisions are made so it remains a living reference for the project.
- **Consistent peer review:** All PRs will receive at least one teammate review before merging.
- **Clear PR descriptions:** Each PR should explain both *what* was changed and *why*.
- **Shared code familiarity:** Work will be distributed across team members so everyone remains familiar with multiple parts of the dashboard codebase.

## Fixing Typos

Small typos or grammatical errors in documentation may be edited directly using the GitHub web interface, so long as the changes are made in the source file.

* YES: you edit documentation in `.md` files or docstrings in `.py` files
* NO: you edit generated output files

## Prerequisites

Before you make a substantial pull request, you should always file an issue and make sure someone from the team agrees that it's a problem or desired feature. If you've found a bug, create an associated issue and describe:

* Steps to reproduce the bug
* Expected behavior
* Actual behavior
* Screenshots (if applicable)

## Pull Request Process

* We recommend that you create a Git branch for each pull request (PR)
* Pull requests should be small and focused on a single feature or fix whenever possible
* New code should follow the PEP 8 style guide
* Use descriptive commit messages
* We use docstrings for documentation - please include them for new functions
* Contributions with test cases are easier to accept
* Update `README.md`, `m2_spec.md`, or other relevant documentation if your changes affect how users interact with the dashboard
* In your pull request description, clearly explain what changes you've made and why

## Code Standards

* Follow PEP 8 for Python code formatting
* Write clear, descriptive variable and function names
* Include comments for complex logic
* Test your changes locally before submitting

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

---

*Adapted from the [dplyr contributing guidelines](https://github.com/tidyverse/dplyr/blob/main/.github/CONTRIBUTING.md).*