/**
 * Claude Platform Adapter
 * 
 * Adapts skills to the Claude platform format.
 * Claude uses SKILL.md format with YAML frontmatter.
 * 
 * @version 2.1.0 - Refactored to use MarkdownAdapter base class
 */

const { MarkdownAdapter } = require('./MarkdownAdapter');

// Create Claude adapter instance
const claudeAdapter = new MarkdownAdapter({
  name: 'claude',
  installDir: '.claude',
  sections: [
    '## Overview',
    '## Usage',
    '## Examples',
    '## Configuration',
  ],
  requiredFields: ['name', 'version', 'description'],
});

// Export the adapter interface
module.exports = {
  name: claudeAdapter.name,
  template: claudeAdapter.template,
  formatSkill: claudeAdapter.formatSkill.bind(claudeAdapter),
  getInstallPath: claudeAdapter.getInstallPath.bind(claudeAdapter),
  generateMetadata: claudeAdapter.generateMetadata.bind(claudeAdapter),
  validateSkill: claudeAdapter.validateSkill.bind(claudeAdapter),
};
