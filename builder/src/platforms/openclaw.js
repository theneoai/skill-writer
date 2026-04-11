/**
 * OpenClaw Platform Adapter
 *
 * Adapts skills to the OpenClaw AgentSkills format.
 * OpenClaw requires a `metadata.openclaw` frontmatter block and expects
 * the LoongFlow (§4), Self-Review (§9), and UTE (§11) sections to be present.
 *
 * @module builder/src/platforms/openclaw
 * @version 2.2.0
 */

const path = require('path');
const os = require('os');
const fs = require('fs');

const name = 'openclaw';

// ---------------------------------------------------------------------------
// External section templates (loaded once at module initialisation).
// Keeping presentation content in dedicated files separates it from adapter
// logic and makes each section independently reviewable and editable.
// ---------------------------------------------------------------------------
const SECTIONS_DIR = path.join(__dirname, 'sections');

function readSection(filename) {
  try {
    return fs.readFileSync(path.join(SECTIONS_DIR, filename), 'utf8');
  } catch (e) {
    throw new Error(`[openclaw] Failed to load section template "${filename}": ${e.message}`);
  }
}

const LOONGFLOW_BODY = readSection('openclaw-loongflow.md');
const SELF_REVIEW_BODY = readSection('openclaw-self-review.md');
const UTE_BODY = readSection('openclaw-ute.md');

// ---------------------------------------------------------------------------
// Constants — centralised so they don't scatter across formatSkill / validate
// ---------------------------------------------------------------------------

const OPENCLAW_METADATA = {
  format: 'agentskills',
  compatibility: ['1.0', '2.0'],
  features: ['self-review', 'self-evolution'],
  runtime: { timeout: 30000, maxRetries: 3, checkpointInterval: 10 },
};

/**
 * Sections that OpenClaw mandates in the skill body.
 *
 * NOTE: Only list sections that formatSkill() INJECTS when absent.
 * §1 (Identity/Overview) comes from the source skill and is not injected,
 * so it is NOT included here — its presence is a source-skill concern, not
 * an adapter guarantee.
 */
const REQUIRED_SECTIONS = [
  '## §4 LoongFlow Orchestration',  // injected by formatSkill if missing
  '## §9 Self-Review Protocol',     // injected by formatSkill if missing
];

/** Sections that are strongly recommended but not blocking */
const RECOMMENDED_SECTIONS = [
  '## §11 UTE Injection',
];


// ---------------------------------------------------------------------------
// Template definition
// ---------------------------------------------------------------------------

const template = {
  frontmatter: `---
name: {{name}}
version: {{version}}
description: {{description}}
license: {{license}}
author: {{author}}
tags: {{tags}}
interface:
  mode:
    type: enum
    values: {{modes}}
    default: {{defaultMode}}
    description: Operating mode for the skill
metadata:
  openclaw:
    format: agentskills
    compatibility: ["1.0", "2.0"]
    features:
      - self-review
      - self-evolution
    runtime:
      timeout: 30000
      maxRetries: 3
      checkpointInterval: 10
---`,
  sections: [
    '## §1 Identity',
    '## §2 Mode Router',
    '## §3 Graceful Degradation',
    '## §4 LoongFlow Orchestration',
    '## §5 Workflow',
    '## §6 Quality Gates',
    '## §7 Security Baseline',
    '## §8 Error Handling',
    '## §9 Self-Review Protocol',
    '## §10 Usage Examples',
    '## §11 UTE Injection',
  ],
  requiredFields: ['name', 'version', 'description', 'metadata.openclaw'],
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Check whether a section heading is present in the content.
 * @param {string} content
 * @param {string} sectionHeading - e.g. '## §4 LoongFlow Orchestration'
 */
function hasSection(content, sectionHeading) {
  const escaped = sectionHeading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`^${escaped}`, 'm').test(content);
}

/**
 * Inject `metadata.openclaw` into frontmatter if not already present.
 */
function ensureOpenClawMetadata(content) {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) return content;

  const fm = frontmatterMatch[1];
  if (fm.includes('metadata:') && fm.includes('openclaw:')) return content;

  const metaBlock = [
    'metadata:',
    '  openclaw:',
    `    format: ${OPENCLAW_METADATA.format}`,
    `    compatibility: ${JSON.stringify(OPENCLAW_METADATA.compatibility)}`,
    '    features:',
    ...OPENCLAW_METADATA.features.map(f => `      - ${f}`),
    '    runtime:',
    `      timeout: ${OPENCLAW_METADATA.runtime.timeout}`,
    `      maxRetries: ${OPENCLAW_METADATA.runtime.maxRetries}`,
    `      checkpointInterval: ${OPENCLAW_METADATA.runtime.checkpointInterval}`,
  ].join('\n');

  return content.replace(/^---\n([\s\S]*?)\n---/, `---\n$1\n${metaBlock}\n---`);
}

/**
 * Inject a section body after the Mode Router section (§2), or append to end.
 * @param {string} content
 * @param {string} sectionBody - Full section text (starts with `\n## §N …`)
 * @param {string} insertAfter - Heading to insert after (e.g. '## §2 Mode Router')
 */
function injectSection(content, sectionBody, insertAfter) {
  if (insertAfter) {
    const escaped = insertAfter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const afterPattern = new RegExp(`(${escaped}[\\s\\S]*?)(\n## §|$)`);
    const match = content.match(afterPattern);
    if (match) {
      return content.replace(match[1], match[1] + sectionBody);
    }
  }
  return content + sectionBody;
}

// ---------------------------------------------------------------------------
// Adapter interface
// ---------------------------------------------------------------------------

/**
 * Format skill content for the OpenClaw platform.
 * Ensures:
 *   1. `metadata.openclaw` block in frontmatter
 *   2. §4 LoongFlow Orchestration section
 *   3. §9 Self-Review Protocol section
 *   4. §11 UTE Injection section (recommended)
 *
 * @param {string} skillContent - Raw skill content (Markdown with YAML frontmatter)
 * @returns {string} Formatted content for OpenClaw
 */
function formatSkill(skillContent) {
  if (!skillContent || typeof skillContent !== 'string') {
    throw new Error('Invalid skill content provided');
  }

  const frontmatterMatch = skillContent.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    throw new Error('Skill content missing required YAML frontmatter');
  }

  let content = skillContent;

  // 1. Ensure metadata.openclaw is in frontmatter
  content = ensureOpenClawMetadata(content);

  // 2. Inject LoongFlow section if missing
  if (!hasSection(content, '## §4 LoongFlow Orchestration')) {
    content = injectSection(content, LOONGFLOW_BODY, '## §2 Mode Router');
  }

  // 3. Inject Self-Review section if missing
  if (!hasSection(content, '## §9 Self-Review Protocol')) {
    content = injectSection(content, SELF_REVIEW_BODY, '## §8 Error Handling');
  }

  // 4. Inject UTE section if missing (recommended, not mandatory)
  if (!hasSection(content, '## §11 UTE Injection')) {
    content = content + UTE_BODY;
  }

  return content.trim();
}

/**
 * Get the installation path for OpenClaw skills.
 * @returns {string} Installation path
 */
function getInstallPath() {
  return path.join(os.homedir(), '.openclaw', 'skills');
}

/**
 * Generate OpenClaw-specific metadata.
 * @param {Object} skillData - Skill data object
 * @returns {Object} Platform metadata
 */
function generateMetadata(skillData) {
  return {
    platform: name,
    format: 'AgentSkills',
    version: skillData?.version || '1.0.0',
    created: new Date().toISOString(),
    metadata: { openclaw: OPENCLAW_METADATA },
    compatibility: { minVersion: '2.2.0', testedVersions: [require('../../package.json').version] },
  };
}

/**
 * Validate skill structure for OpenClaw.
 * @param {string} skillContent - Skill content to validate
 * @returns {{ valid: boolean, errors: string[], warnings: string[] }}
 */
function validateSkill(skillContent) {
  const errors = [];
  const warnings = [];

  const frontmatterMatch = skillContent.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    errors.push('Missing YAML frontmatter');
  } else {
    const fm = frontmatterMatch[1];
    if (!fm.includes('name:')) errors.push('Missing required field: name');
    if (!fm.includes('version:')) errors.push('Missing required field: version');
    if (!fm.includes('description:')) errors.push('Missing required field: description');
    if (!fm.includes('metadata:') || !fm.includes('openclaw:')) {
      errors.push('Missing required metadata.openclaw section');
    }
  }

  REQUIRED_SECTIONS.forEach(section => {
    if (!hasSection(skillContent, section)) {
      errors.push(`Missing required section: ${section}`);
    }
  });

  RECOMMENDED_SECTIONS.forEach(section => {
    if (!hasSection(skillContent, section)) {
      warnings.push(`Missing recommended section: ${section}`);
    }
  });

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * Convert an OpenCode-formatted skill to OpenClaw format.
 * @param {string} opencodeContent - OpenCode formatted skill
 * @returns {string} OpenClaw formatted skill
 */
function fromOpenCode(opencodeContent) {
  return formatSkill(opencodeContent);
}

module.exports = {
  name,
  template,
  formatSkill,
  getInstallPath,
  generateMetadata,
  validateSkill,
  fromOpenCode,
  // Export constants for testing
  REQUIRED_SECTIONS,
  RECOMMENDED_SECTIONS,
  OPENCLAW_METADATA,
};
