/**
 * Embedder Module Tests
 * 
 * Tests for the embedder module with strict mode
 */

const embedder = require('../../src/core/embedder');
const config = require('../../src/config');

describe('Embedder Module', () => {
  describe('getPlatformConfig', () => {
    test('should return config for known platforms', () => {
      const opencode = embedder.getPlatformConfig('opencode');
      expect(opencode.name).toBe('opencode');
      expect(opencode.supportsFrontmatter).toBe(true);
    });

    test('should return default config for unknown platforms', () => {
      const unknown = embedder.getPlatformConfig('unknown');
      expect(unknown).toBeDefined();
      expect(unknown.name).toBe('opencode'); // Default
    });

    test('should be case insensitive', () => {
      const lower = embedder.getPlatformConfig('claude');
      const upper = embedder.getPlatformConfig('CLAUDE');
      expect(lower.name).toBe(upper.name);
    });
  });

  describe('replacePlaceholders', () => {
    const mockConfig = {
      placeholderPattern: /\{\{(\w+)\}\}/g,
    };

    test('should replace placeholders with data values', () => {
      const template = 'Hello {{NAME}}, version {{VERSION}}';
      const data = { NAME: 'Test', VERSION: '1.0.0' };
      const result = embedder.replacePlaceholders(template, data, mockConfig);
      expect(result).toBe('Hello Test, version 1.0.0');
    });

    test('should keep original placeholder when value missing (non-strict)', () => {
      const template = 'Hello {{NAME}}, missing {{MISSING}}';
      const data = { NAME: 'Test' };
      const result = embedder.replacePlaceholders(template, data, mockConfig);
      expect(result).toBe('Hello Test, missing {{MISSING}}');
    });

    test('should throw error in strict mode when placeholder missing', () => {
      const template = 'Hello {{NAME}}, missing {{MISSING}}';
      const data = { NAME: 'Test' };
      expect(() => {
        embedder.replacePlaceholders(template, data, mockConfig, { strict: true });
      }).toThrow(config.ERROR_CODES.MISSING_PLACEHOLDER);
    });

    test('should include placeholder key in error message', () => {
      const template = 'Missing {{MISSING_KEY}}';
      const data = {};
      expect(() => {
        embedder.replacePlaceholders(template, data, mockConfig, { strict: true });
      }).toThrow('MISSING_KEY');
    });

    test('should handle null values as missing in strict mode', () => {
      const template = 'Value: {{NULL_VAL}}';
      const data = { NULL_VAL: null };
      expect(() => {
        embedder.replacePlaceholders(template, data, mockConfig, { strict: true });
      }).toThrow(config.ERROR_CODES.MISSING_PLACEHOLDER);
    });

    test('should handle empty string values (not missing)', () => {
      const template = 'Value: {{EMPTY}}';
      const data = { EMPTY: '' };
      const result = embedder.replacePlaceholders(template, data, mockConfig, { strict: true });
      expect(result).toBe('Value: ');
    });

    test('should default to non-strict mode', () => {
      const template = 'Missing {{MISSING}}';
      const data = {};
      // Should not throw
      expect(() => {
        embedder.replacePlaceholders(template, data, mockConfig);
      }).not.toThrow();
    });
  });

  describe('formatFrontmatter', () => {
    test('should format object as YAML frontmatter', () => {
      const data = {
        name: 'test-skill',
        version: '1.0.0',
      };
      const result = embedder.formatFrontmatter(data);
      expect(result).toContain('---');
      expect(result).toContain('name: test-skill');
      expect(result).toContain('version: 1.0.0');
    });

    test('should handle empty object', () => {
      const result = embedder.formatFrontmatter({});
      expect(result).toContain('---');
      expect(result).toContain('---');
    });
  });

  describe('extractPlaceholders', () => {
    test('should extract all placeholders from template', () => {
      const template = '{{NAME}} {{VERSION}} {{NAME}}';
      const config = { placeholderPattern: /\{\{(\w+)\}\}/g };
      const result = embedder.extractPlaceholders(template, config);
      expect(result).toContain('NAME');
      expect(result).toContain('VERSION');
      expect(result.length).toBe(3); // Includes duplicates
    });

    test('should return empty array for no placeholders', () => {
      const template = 'No placeholders here';
      const config = { placeholderPattern: /\{\{(\w+)\}\}/g };
      const result = embedder.extractPlaceholders(template, config);
      expect(result).toEqual([]);
    });
  });
});
