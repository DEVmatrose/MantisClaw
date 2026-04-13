---
name: workspace_status
version: 0.1.0
description: "Liest den Workspace-Status und erstellt eine Zusammenfassung"
requires_tools:
  - list_dir
  - read_file
  - summarize
category: workspace
trigger: planner
max_retries: 1
---

# Skill: Workspace Status

## System-Prompt
Du prüfst den aktuellen Zustand des Workspace und erstellst eine kurze Zusammenfassung.

## Workflow

### Step 1: Verzeichnis auflisten
- tool: list_dir
- input: WORKSPACE/WORKING
- output: $dir_listing

### Step 2: Workpapers lesen
- tool: list_dir
- input: WORKSPACE/WORKING/WORKPAPER
- output: $workpapers

### Step 3: Zusammenfassung
- tool: summarize
- input: Workspace enthält: $dir_listing. Aktive Workpapers: $workpapers
- output: $summary
