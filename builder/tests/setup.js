/**
 * Test Setup
 * 
 * Jest configuration and test utilities for skill-writer-builder
 */

const path = require('path');

// Test configuration
const TEST_CONFIG = {
  // Project root for tests
  projectRoot: path.resolve(__dirname, '../..'),
  
  // Test timeouts
  timeout: {
    unit: 5000,
    integration: 30000,
  },
  
  // Test data paths
  fixtures: {
    templates: path.join(__dirname, '../fixtures/templates'),
    refs: path.join(__dirname, '../fixtures/refs'),
  },
};

/**
 * Create a mock file system structure for testing
 */
function createMockFs() {
  return {
    files: new Map(),
    
    readFile(filepath, encoding) {
      if (this.files.has(filepath)) {
        return Promise.resolve(this.files.get(filepath));
      }
      const error = new Error(`ENOENT: no such file or directory, open '${filepath}'`);
      error.code = 'ENOENT';
      return Promise.reject(error);
    },
    
    writeFile(filepath, content) {
      this.files.set(filepath, content);
      return Promise.resolve();
    },
    
    pathExists(filepath) {
      return Promise.resolve(this.files.has(filepath));
    },
    
    reset() {
      this.files.clear();
    },
  };
}

/**
 * Create mock data for testing
 */
function createMockCoreData() {
  return {
    create: {
      templates: {
        base: {
          content: '# Base Template\n\n{{DESCRIPTION}}',
          name: 'base.md',
        },
      },
    },
    evaluate: {
      rubrics: {
        content: '# Evaluation Rubrics',
        name: 'rubrics.md',
      },
    },
    optimize: {
      strategies: {
        content: '# Optimization Strategies',
        name: 'strategies.md',
      },
    },
    shared: {
      securityPatterns: {
        content: '# Security Patterns',
        name: 'security-patterns.md',
      },
    },
  };
}

module.exports = {
  TEST_CONFIG,
  createMockFs,
  createMockCoreData,
};
