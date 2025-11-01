# EvalSwipe User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating a Session](#creating-a-session)
4. [Reviewing Traces](#reviewing-traces)
5. [Open Coding](#open-coding)
6. [Axial Coding](#axial-coding)
7. [Prompt Improvement](#prompt-improvement)
8. [Braintrust Integration](#braintrust-integration)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Tips & Best Practices](#tips--best-practices)

## Introduction

EvalSwipe is a systematic approach to AI trace evaluation that combines speed with methodological rigor. It uses open and axial coding from grounded theory to help you discover patterns in AI system failures and generate improvements.

### Key Concepts

- **Open Coding**: Writing freeform observations about trace failures
- **Axial Coding**: Organizing observations into structured categories (tags)
- **Trace**: A complete record of an AI interaction (input, output, metadata)
- **Session**: A collection of traces being reviewed together

## Getting Started

### Demo Data

The quickest way to get started is with the built-in demo data:

1. Click **"Load Demo"** on the welcome screen
2. Review 50 sample snack recommendation traces
3. Practice the coding workflow

### Understanding the Interface

The main interface has three sections:

1. **Progress Tracker** (top): Shows review progress and counts
2. **Trace Card** (center): Displays current trace details
3. **Action Buttons** (bottom): Pass, Fail, or Defer decisions

## Creating a Session

You have three options for loading traces:

### Option 1: Demo Data

- Pre-loaded 50 snack recommendation traces
- Mix of good and bad examples
- Ideal for learning the system

### Option 2: Upload JSON

1. Click **"Upload JSON"**
2. Select a file with trace data
3. Expected format:

```json
{
  "traces": [
    {
      "id": "trace_001",
      "user_input": "User's question or prompt",
      "agent_output": "AI system's response",
      "system_prompt": "Optional system prompt",
      "metadata": {}
    }
  ]
}
```

### Option 3: Import from Braintrust

1. Click **"Import from Braintrust"**
2. Enter your credentials:
   - API Key (if not in .env)
   - Project ID
   - Experiment ID
3. Set trace limit (max 1000)
4. Click **"Fetch Traces"**

## Reviewing Traces

### Basic Review Workflow

Each trace shows:
- **User Input**: What the user asked
- **Agent Output**: How the AI responded
- **Show Details** (expandable): System prompt, intermediate steps, metadata

### Making Decisions

You have three options for each trace:

#### Pass (✓)
- Trace meets quality standards
- No significant issues
- **Shortcut**: Right arrow or **P** key

#### Fail (✗)
- Trace has problems
- Opens open coding modal
- **Shortcut**: Left arrow or **F** key

#### Defer (⟳)
- Uncertain about judgment
- Need more context
- Will review later
- **Shortcut**: Up arrow or **D** key

### Viewing Details

Click **"Show Details"** or press **Space** to see:
- Full system prompt
- Intermediate reasoning steps
- Tool calls and responses
- Metadata (model, latency, etc.)

## Open Coding

When you mark a trace as **Fail**, the open coding modal appears.

### Writing Good Open Codes

**Guidelines:**
- Be specific about what went wrong
- Focus on the first significant failure
- Describe what you observed, not what should have happened
- Include examples from the trace

**Example Good Open Codes:**

✅ "Agent claimed Lindt 90% cacao bars are sugar-free, but they contain ~5g sugar per bar"

✅ "User asked for plant-based protein snacks but got Greek yogurt, eggs, and beef jerky instead"

✅ "Response tone overly formal ('procuring', 'interactive digital entertainment') for casual user input ('yo', 'munching')"

**Example Poor Open Codes:**

❌ "Wrong"

❌ "Bad response"

❌ "Needs improvement"

### After Writing

You have two options:

1. **Tag Now**: Immediately apply axial tags
2. **Tag Later**: Save and move to next trace

**Recommended**: Tag later for your first 20-30 traces to discover patterns before categorizing.

## Axial Coding

Axial coding organizes your open codes into structured categories.

### Creating Tags

1. Click **"+ Create New Tag"**
2. Fill in:
   - **Name**: Short, descriptive (2-30 chars)
   - **Description**: What failures belong here (20-200 chars)
   - **Color**: Visual distinction (optional)
3. Click **"Save Tag"**

**Example Tags:**

- **Hallucinated Metadata**: Agent invented facts not in source data
- **Ignored Constraints**: Failed to follow user's specific requirements
- **Tone Mismatch**: Response formality doesn't match user's style
- **Incomplete Response**: Missing explanations or insufficient detail

### Applying Tags

1. Click tags to select/deselect
2. Multiple tags can apply to one trace
3. Click **"Apply Tags & Continue"**

### Tag Usage Counts

Tags show usage counts like "Hallucinated Metadata (12)" to help you see common failure modes.

## Prompt Improvement

After coding 20-30 traces, use the AI-powered prompt improvement tool.

### Generating Suggestions

1. Click **"Prompt Improvement"** in header
2. Paste your current system prompt
3. Select target failure modes (tags)
4. Add optional context
5. Set number of suggestions (1-5)
6. Click **"Generate Suggestions"**

### Reviewing Suggestions

Each suggestion includes:
- Improved prompt text
- List of changes made
- Targeted failure modes
- **Copy** button for quick use

### Best Practices

- Start with 2-3 most common failure modes
- Generate multiple variations
- Test improved prompts with real traces
- Iterate based on results

## Braintrust Integration

### Importing Traces

See [Creating a Session](#creating-a-session) → Option 3

### Exporting Annotations

After reviewing, sync your annotations back to Braintrust:

1. Click **"Export"** menu
2. Select **"Export to Braintrust"**
3. Annotations include:
   - Pass/Fail scores (1/0)
   - Open codes as comments
   - Axial tags as labels
   - Reviewer ID and timestamp

## Keyboard Shortcuts

### Navigation
- **→** or **P**: Pass current trace
- **←** or **F**: Fail current trace
- **↑** or **D**: Defer current trace
- **Space**: Toggle trace details
- **Cmd/Ctrl + Z**: Undo last action

### Efficiency Tips

- Use keyboard shortcuts for 3-5x faster reviews
- Keep hands on keyboard, minimize mouse use
- Review 10-15 traces before taking a break

## Tips & Best Practices

### Open Coding Phase (First 20-30 Traces)

1. Write detailed observations for every failure
2. Don't create tags yet - discover patterns first
3. Look for recurring themes in your notes
4. Recommended: 15-20 traces per hour

### Axial Coding Phase

1. Review all untagged open codes together
2. Group similar failures
3. Create 5-10 distinct tags
4. Re-tag traces as patterns become clear

### Achieving Theoretical Saturation

You've reached saturation when:
- New traces show same failure modes
- No new tags needed for 10+ consecutive traces
- Typically occurs after 30-50 traces

### Inter-Rater Reliability

For team reviews:
- Have 2+ reviewers code same 20 traces independently
- Compare tags and calculate Cohen's Kappa
- Discuss disagreements to align on definitions
- Target > 0.75 agreement

### Session Management

- **Auto-save**: Sessions save to browser automatically
- **Resume**: Reload page to continue where you left off
- **Export**: Download CSV/JSON/PDF before clearing browser data
- **Multiple Sessions**: Use "New Session" to start fresh

### Quality Over Speed

- Don't rush through traces
- Read full outputs carefully
- Consider edge cases
- Write specific, actionable open codes

## Troubleshooting

### Session Not Saving

- Check browser localStorage quota
- Export session before closing browser
- Use smaller batches (< 500 traces)

### Missing Traces

- Verify JSON format matches expected structure
- Check browser console (F12) for errors
- Try demo data to verify system works

### Slow Performance

- Close unused browser tabs
- Review in batches of 100 traces
- Clear old sessions from localStorage

## Export Options

### CSV Export

- One row per trace
- Includes all annotations
- Good for spreadsheet analysis

### JSON Export

- Complete session data
- Preserves all metadata
- Good for backups and sharing

### PDF Report

- Summary statistics
- Failure mode distribution
- Visual charts
- Good for stakeholder reports

## Next Steps

1. **Complete your first session**: Review all traces
2. **Generate prompt improvements**: Use your findings
3. **Test improvements**: Import new traces, compare results
4. **Iterate**: Refine tags, improve prompts, measure impact

## Additional Resources

- See [SETUP.md](SETUP.md) for installation instructions
- See [API.md](API.md) for integration details
- Review the full PRD for methodology background
