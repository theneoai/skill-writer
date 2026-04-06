/**
 * Config Module Tests
 * 
 * Tests for the centralized configuration module
 */

const config = require('../../src/config');

describe('Config Module', () => {
  describe('PATHS', () => {
    test('should export PATHS object with all required paths', () => {
      expect(config.PATHS).toBeDefined();
      expect(config.PATHS.root).toBeDefined();
      expect(config.PATHS.templates).toBeDefined();
      expect(config.PATHS.refs).toBeDefined();
      expect(config.PATHS.eval).toBeDefined();
      expect(config.PATHS.optimize).toBeDefined();
      expect(config.PATHS.platforms).toBeDefined();
      expect(config.PATHS.skillFramework).toBeDefined();
    });

    test('paths should be absolute', () => {
      expect(path.isAbsolute(config.PATHS.root)).toBe(true);
      expect(path.isAbsolute(config.PATHS.templates)).toBe(true);
    });
  });

  describe('REQUIRED_FILES', () => {
    test('should export REQUIRED_FILES array', () => {
      expect(Array.isArray(config.REQUIRED_FILES)).toBe(true);
      expect(config.REQUIRED_FILES.length).toBeGreaterThan(0);
    });

    test('each file should have path, label, and mustEmbed properties', () => {
      config.REQUIRED_FILES.forEach(file => {
        expect(file.path).toBeDefined();
        expect(file.label).toBeDefined();
        expect(typeof file.mustEmbed).toBe('boolean');
      });
    });

    test('should include all critical companion files', () => {
      const labels = config.REQUIRED_FILES.map(f => f.label);
      expect(labels).toContain('refs/self-review.md');
      expect(labels).toContain('refs/security-patterns.md');
      expect(labels).toContain('eval/rubrics.md');
      expect(labels).toContain('optimize/strategies.md');
    });
  });

  describe('REQUIRED_UTE_FIELDS', () => {
    test('should export REQUIRED_UTE_FIELDS array', () => {
      expect(Array.isArray(config.REQUIRED_UTE_FIELDS)).toBe(true);
      expect(config.REQUIRED_UTE_FIELDS).toContain('enabled');
      expect(config.REQUIRED_UTE_FIELDS).toContain('injected_by');
    });
  });

  describe('PLACEHOLDERS', () => {
    test('should export PLACEHOLDERS with regex patterns', () => {
      expect(config.PLACEHOLDERS.standard).toBeInstanceOf(RegExp);
      expect(config.PLACEHOLDERS.extended).toBeInstanceOf(RegExp);
      expect(config.PLACEHOLDERS.cursor).toBeInstanceOf(RegExp);
    });

    test('standard pattern should match {{KEY}} format', () => {
      expect('{{NAME}}').toMatch(config.PLACEHOLDERS.standard);
      expect('{{VERSION}}').toMatch(config.PLACEHOLDERS.standard);
      expect('not a placeholder').not.toMatch(config.PLACEHOLDERS.standard);
    });
  });

  describe('PLATFORMS', () => {
    test('should export all 6 platform configs', () => {
      expect(config.PLATFORMS.opencode).toBeDefined();
      expect(config.PLATFORMS.openclaw).toBeDefined();
      expect(config.PLATFORMS.claude).toBeDefined();
      expect(config.PLATFORMS.cursor).toBeDefined();
      expect(config.PLATFORMS.openai).toBeDefined();
      expect(config.PLATFORMS.gemini).toBeDefined();
    });

    test('each platform should have required properties', () => {
      Object.values(config.PLATFORMS).forEach(platform => {
        expect(platform.name).toBeDefined();
        expect(platform.placeholderPattern).toBeInstanceOf(RegExp);
        expect(typeof platform.supportsFrontmatter).toBe('boolean');
      });
    });
  });

  describe('SCORING', () => {
    test('should export scoring configuration', () => {
      expect(config.SCORING.lean.maxScore).toBe(500);
      expect(config.SCORING.evaluate.maxScore).toBe(1000);
      expect(config.SCORING.varianceGates.platinum).toBe(10);
    });
  });

  describe('ERROR_CODES', () => {
    test('should export error codes', () => {
      expect(config.ERROR_CODES.MISSING_PLACEHOLDER).toBe('EMISSING_PLACEHOLDER');
      expect(config.ERROR_CODES.EMBED_FAILED).toBe('EEMBED_FAILED');
    });
  });
});

const path = require('path');
