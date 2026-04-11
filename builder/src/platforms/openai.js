/**
 * OpenAI Platform Adapter
 * 
 * Adapts skills to the OpenAI platform format.
 * OpenAI uses JSON format for instructions rather than Markdown.
 */

const path = require('path');
const os = require('os');
const yaml = require('js-yaml');

const name = 'openai';

const template = {
  // OpenAI uses JSON format
  format: 'json',
  requiredFields: [
    'name',
    'version',
    'description',
    'instructions'
  ]
};

/**
 * Format skill content for OpenAI platform
 * @param {string} skillContent - Raw skill content
 * @returns {string} Formatted skill content (JSON)
 */
function formatSkill(skillContent) {
  if (!skillContent || typeof skillContent !== 'string') {
    throw new Error('Invalid skill content provided');
  }

  // Extract YAML frontmatter
  const frontmatterMatch = skillContent.match(/^---\n([\s\S]*?)\n---\n/);
  let metadata = {};
  let content = skillContent;

  if (frontmatterMatch) {
    try {
      metadata = yaml.load(frontmatterMatch[1]);
      content = skillContent.replace(frontmatterMatch[0], '');
    } catch (error) {
      console.warn('Failed to parse frontmatter:', error.message);
    }
  }

  // Build OpenAI format
  const openaiSkill = {
    name: metadata.name || 'unnamed-skill',
    version: metadata.version || '1.0.0',
    description: metadata.description || '',
    instructions: content.trim(),
    metadata: {
      platform: name,
      created: new Date().toISOString(),
      ...metadata
    }
  };

  return JSON.stringify(openaiSkill, null, 2);
}

/**
 * Get the installation path for OpenAI skills
 * @returns {string} Installation path
 */
function getInstallPath() {
  const homeDir = os.homedir();
  // OpenAI doesn't have a standard local skill directory
  return path.join(homeDir, '.openai', 'skills');
}

/**
 * Generate platform-specific metadata
 * @param {Object} skillData - Skill data object
 * @returns {Object} Platform metadata
 */
function generateMetadata(skillData) {
  return {
    platform: name,
    format: 'JSON',
    version: skillData.version || '1.0.0',
    created: new Date().toISOString(),
    compatibility: {
      minVersion: '2.2.0',
      testedVersions: [require('../../package.json').version],
    }
  };
}

/**
 * Validate skill structure for OpenAI
 * @param {string} skillContent - Skill content to validate (JSON)
 * @returns {Object} Validation result
 */
function validateSkill(skillContent) {
  const errors = [];
  const warnings = [];

  try {
    const data = JSON.parse(skillContent);
    
    // Check required fields
    template.requiredFields.forEach(field => {
      if (!data[field]) {
        errors.push(`Missing required field: ${field}`);
      }
    });
  } catch (error) {
    errors.push(`Invalid JSON: ${error.message}`);
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

module.exports = {
  name,
  template,
  formatSkill,
  getInstallPath,
  generateMetadata,
  validateSkill
};
