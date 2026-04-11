/**
 * Core Reader Module
 *
 * Reads companion Markdown files for the skill-writer-builder.
 * Sources: refs/, templates/, eval/, optimize/ (Single Source of Truth)
 * 
 * @version 3.1.0 - Added v3.0 collective evolution refs; v3.1.0 added session-artifact, edit-audit, skill-registry reads
 */

const fs = require('fs-extra');
const path = require('path');
const { glob } = require('glob');
const config = require('../config');

/**
 * Parse a Markdown or JSON file
 * @param {string} filePath - Path to the file
 * @returns {Object} - Parsed content object
 */
async function parseFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const content = await fs.readFile(filePath, 'utf-8');

  if (ext === '.json') {
    return JSON.parse(content);
  }

  return {
    content,
    path: filePath,
    name: path.basename(filePath),
    extension: ext || '.md'
  };
}

/**
 * Read CREATE mode files from templates/
 * @returns {Object} - CREATE mode data
 */
async function readCreateMode() {
  const templatesDir = config.PATHS.templates;
  const data = {
    templates: {}
  };

  if (await fs.pathExists(templatesDir)) {
    const templateFiles = await glob('*.md', {
      cwd: templatesDir,
      absolute: true
    });

    for (const templatePath of templateFiles) {
      const templateName = path.basename(templatePath, '.md');
      // Skip the UTE snippet — it's not a skill template
      if (templateName === 'use-to-evolve-snippet') continue;
      data.templates[templateName] = await parseFile(templatePath);
    }
  }

  return data;
}

/**
 * Read EVALUATE mode files from eval/
 * @returns {Object} - EVALUATE mode data
 */
async function readEvaluateMode() {
  const data = {
    rubrics: null,
    benchmarks: null
  };

  const rubricsPath = path.join(config.PATHS.eval, 'rubrics.md');
  if (await fs.pathExists(rubricsPath)) {
    data.rubrics = await parseFile(rubricsPath);
  }

  const benchmarksPath = path.join(config.PATHS.eval, 'benchmarks.md');
  if (await fs.pathExists(benchmarksPath)) {
    data.benchmarks = await parseFile(benchmarksPath);
  }

  return data;
}

/**
 * Read OPTIMIZE mode files from optimize/
 * Note: convergence.md is read in readSharedResources() (refs/) to avoid duplication.
 * @returns {Object} - OPTIMIZE mode data
 */
async function readOptimizeMode() {
  const data = {
    strategies: null,
    antiPatterns: null,
    // convergence is now in shared.convergence (refs/convergence.md)
  };

  const strategiesPath = path.join(config.PATHS.optimize, 'strategies.md');
  if (await fs.pathExists(strategiesPath)) {
    data.strategies = await parseFile(strategiesPath);
  }

  const antiPatternsPath = path.join(config.PATHS.optimize, 'anti-patterns.md');
  if (await fs.pathExists(antiPatternsPath)) {
    data.antiPatterns = await parseFile(antiPatternsPath);
  }

  return data;
}

/**
 * Read shared resources from refs/
 * Includes all companion files listed in config.REQUIRED_FILES with mustEmbed: true.
 * @returns {Object} - Shared resources data
 */
async function readSharedResources() {
  const data = {
    // Core evaluation and evolution refs
    securityPatterns: null,
    selfReview: null,
    evolution: null,
    useToEvolve: null,
    convergence: null,
    // v3.0: collective evolution refs (SkillClaw-compatible)
    sessionArtifact: null,
    editAudit: null,
    skillRegistry: null,
  };

  // Read security patterns (includes OWASP Agentic Top 10 since v3.1.0)
  const securityPath = path.join(config.PATHS.refs, 'security-patterns.md');
  if (await fs.pathExists(securityPath)) {
    data.securityPatterns = await parseFile(securityPath);
  }

  // Read self-review protocol
  const selfReviewPath = path.join(config.PATHS.refs, 'self-review.md');
  if (await fs.pathExists(selfReviewPath)) {
    data.selfReview = await parseFile(selfReviewPath);
  }

  // Read evolution spec (3-trigger system + OWASP/tier-drift triggers since v3.1.0)
  const evolutionPath = path.join(config.PATHS.refs, 'evolution.md');
  if (await fs.pathExists(evolutionPath)) {
    data.evolution = await parseFile(evolutionPath);
  }

  // Read use-to-evolve spec (UTE 2.0 L1/L2)
  const useToEvolvePath = path.join(config.PATHS.refs, 'use-to-evolve.md');
  if (await fs.pathExists(useToEvolvePath)) {
    data.useToEvolve = await parseFile(useToEvolvePath);
  }

  // Read convergence detection spec
  const convergencePath = path.join(config.PATHS.refs, 'convergence.md');
  if (await fs.pathExists(convergencePath)) {
    data.convergence = await parseFile(convergencePath);
  }

  // v3.0+: Read session artifact schema (SkillClaw + SkillRL lesson distillation since v3.1.0)
  const sessionArtifactPath = path.join(config.PATHS.refs, 'session-artifact.md');
  if (await fs.pathExists(sessionArtifactPath)) {
    data.sessionArtifact = await parseFile(sessionArtifactPath);
  }

  // v3.0+: Read edit audit guard spec
  const editAuditPath = path.join(config.PATHS.refs, 'edit-audit.md');
  if (await fs.pathExists(editAuditPath)) {
    data.editAudit = await parseFile(editAuditPath);
  }

  // v3.0+: Read skill registry spec (SHA-256 IDs, versioning, SHARE protocol)
  const skillRegistryPath = path.join(config.PATHS.refs, 'skill-registry.md');
  if (await fs.pathExists(skillRegistryPath)) {
    data.skillRegistry = await parseFile(skillRegistryPath);
  }

  return data;
}

/**
 * Read all core data from source files
 * @returns {Object} - Complete core data object
 */
async function readAllCoreData() {
  const [create, evaluate, optimize, shared] = await Promise.all([
    readCreateMode(),
    readEvaluateMode(),
    readOptimizeMode(),
    readSharedResources()
  ]);

  return {
    create,
    evaluate,
    optimize,
    shared,
    metadata: {
      readAt: new Date().toISOString(),
      version: require('../../package.json').version
    }
  };
}

/**
 * Get list of files that must be embedded (mustEmbed: true)
 * @returns {Array} - List of file configs that must be embedded
 */
function getMustEmbedFiles() {
  return config.REQUIRED_FILES.filter(f => f.mustEmbed);
}

module.exports = {
  parseFile,
  readCreateMode,
  readEvaluateMode,
  readOptimizeMode,
  readSharedResources,
  readAllCoreData,
  getMustEmbedFiles,
};
