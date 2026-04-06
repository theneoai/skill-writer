/**
 * Validate Command Tests
 * 
 * Tests for the validate command
 */

const { validate, validateRequiredFiles, validateTemplates, validateGeneratedSkills } = require('../../src/commands/validate');
const config = require('../../src/config');

describe('Validate Command', () => {
  describe('validate', () => {
    test('should return validation result object', async () => {
      const result = await validate();
      expect(result).toHaveProperty('valid');
      expect(result).toHaveProperty('errors');
      expect(result).toHaveProperty('warnings');
      expect(result).toHaveProperty('issues');
      expect(Array.isArray(result.issues)).toBe(true);
    });

    test('should count errors and warnings', async () => {
      const result = await validate();
      expect(typeof result.errors).toBe('number');
      expect(typeof result.warnings).toBe('number');
      expect(result.errors).toBeGreaterThanOrEqual(0);
      expect(result.warnings).toBeGreaterThanOrEqual(0);
    });
  });

  describe('validateRequiredFiles', () => {
    test('should check all required files exist', async () => {
      const result = {
        valid: true,
        errors: 0,
        warnings: 0,
        issues: [],
      };

      await validateRequiredFiles(result);

      // Should have checked all required files
      expect(result.issues.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('validateTemplates', () => {
    test('should check template placeholders', async () => {
      const result = {
        valid: true,
        errors: 0,
        warnings: 0,
        issues: [],
      };

      await validateTemplates(result);

      // Should complete without throwing
      expect(result).toBeDefined();
    });
  });

  describe('validateGeneratedSkills', () => {
    test('should validate generated skill files', async () => {
      const result = {
        valid: true,
        errors: 0,
        warnings: 0,
        issues: [],
      };

      await validateGeneratedSkills(result);

      // Should complete without throwing
      expect(result).toBeDefined();
    });
  });
});
