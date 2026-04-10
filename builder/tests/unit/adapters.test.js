/**
 * Platform Adapter Tests
 *
 * Tests for the platform adapter layer including the MarkdownAdapter base class,
 * the MCP adapter, and the platform registry.
 */

const { MarkdownAdapter } = require('../../src/platforms/MarkdownAdapter');
const mcp = require('../../src/platforms/mcp');
const platforms = require('../../src/platforms');

// Minimal valid skill content (YAML frontmatter + body)
const VALID_SKILL = `---
name: test-skill
version: 1.0.0
description: A test skill
---

## §1 Identity

This is a test skill.

## §2 Mode Router

Routes to appropriate mode.

## §3 Examples

Example usage here.
`;

describe('MarkdownAdapter Base Class', () => {
  let adapter;

  beforeEach(() => {
    adapter = new MarkdownAdapter({
      name: 'test-platform',
      installDir: '.test-platform',
      sections: ['## Overview', '## Usage'],
      requiredFields: ['name', 'version'],
    });
  });

  test('should set name from options', () => {
    expect(adapter.name).toBe('test-platform');
  });

  test('should generate correct install path', () => {
    const installPath = adapter.getInstallPath();
    expect(installPath).toContain('.test-platform');
    expect(installPath).toContain('skills');
  });

  test('formatSkill should accept valid YAML frontmatter content', () => {
    const result = adapter.formatSkill(VALID_SKILL);
    expect(result).toContain('test-skill');
    expect(typeof result).toBe('string');
  });

  test('formatSkill should throw on missing frontmatter', () => {
    expect(() => adapter.formatSkill('# No frontmatter\n\nContent')).toThrow();
  });

  test('formatSkill should throw on empty input', () => {
    expect(() => adapter.formatSkill('')).toThrow();
    expect(() => adapter.formatSkill(null)).toThrow();
  });

  test('formatSkill should normalise extra H1 headings to H2', () => {
    const multiH1 = `---
name: test
version: 1.0.0
description: test
---

# First H1

# Second H1 — should become H2
`;
    const result = adapter.formatSkill(multiH1);
    const h1Count = (result.match(/^# /gm) || []).length;
    expect(h1Count).toBe(1);
  });

  test('validateSkill should report errors for missing required fields', () => {
    const noVersion = VALID_SKILL.replace('version: 1.0.0\n', '');
    const result = adapter.validateSkill(noVersion);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('version'))).toBe(true);
  });

  test('validateSkill should warn about missing recommended sections', () => {
    const result = adapter.validateSkill(VALID_SKILL);
    // VALID_SKILL doesn't have "## Overview" or "## Usage" so warnings expected
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  test('generateMetadata should return platform name', () => {
    const meta = adapter.generateMetadata({ version: '2.0.0' });
    expect(meta.platform).toBe('test-platform');
  });

  test('template getter should return sections and requiredFields', () => {
    const tmpl = adapter.template;
    expect(tmpl.sections).toContain('## Overview');
    expect(tmpl.requiredFields).toContain('name');
  });
});

describe('Claude Adapter (extends MarkdownAdapter)', () => {
  const claude = require('../../src/platforms/claude');

  test('should have name = claude', () => {
    expect(claude.name).toBe('claude');
  });

  test('should expose all required adapter methods', () => {
    expect(typeof claude.formatSkill).toBe('function');
    expect(typeof claude.getInstallPath).toBe('function');
    expect(typeof claude.generateMetadata).toBe('function');
    expect(typeof claude.validateSkill).toBe('function');
  });

  test('install path should reference .claude', () => {
    expect(claude.getInstallPath()).toContain('.claude');
  });
});

describe('Gemini Adapter (extends MarkdownAdapter)', () => {
  const gemini = require('../../src/platforms/gemini');

  test('should have name = gemini', () => {
    expect(gemini.name).toBe('gemini');
  });

  test('install path should reference .gemini', () => {
    expect(gemini.getInstallPath()).toContain('.gemini');
  });
});

describe('MCP Adapter', () => {
  test('should have name = mcp', () => {
    expect(mcp.name).toBe('mcp');
  });

  test('install path should reference .mcp/servers', () => {
    const installPath = mcp.getInstallPath();
    expect(installPath).toContain('.mcp');
    expect(installPath).toContain('servers');
  });

  test('formatSkill should return valid JSON', () => {
    const result = mcp.formatSkill(VALID_SKILL);
    expect(() => JSON.parse(result)).not.toThrow();
  });

  test('formatSkill should extract name from frontmatter', () => {
    const result = mcp.formatSkill(VALID_SKILL);
    const manifest = JSON.parse(result);
    expect(manifest.name).toBe('test-skill');
  });

  test('formatSkill should include schema_version', () => {
    const result = mcp.formatSkill(VALID_SKILL);
    const manifest = JSON.parse(result);
    expect(manifest.schema_version).toBe('1.0');
  });

  test('formatSkill should declare at least one tool', () => {
    const result = mcp.formatSkill(VALID_SKILL);
    const manifest = JSON.parse(result);
    expect(Array.isArray(manifest.tools)).toBe(true);
    expect(manifest.tools.length).toBeGreaterThan(0);
  });

  test('formatSkill should include capabilities block', () => {
    const result = mcp.formatSkill(VALID_SKILL);
    const manifest = JSON.parse(result);
    expect(manifest.capabilities).toBeDefined();
    expect(manifest.capabilities.self_evolution).toBe(true);
  });

  test('validateSkill should pass valid JSON manifest', () => {
    const formatted = mcp.formatSkill(VALID_SKILL);
    const result = mcp.validateSkill(formatted);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('validateSkill should fail on invalid JSON', () => {
    const result = mcp.validateSkill('{broken json');
    expect(result.valid).toBe(false);
  });

  test('generateMetadata should include MCP protocol version', () => {
    const meta = mcp.generateMetadata({ version: '1.0.0' });
    expect(meta.compatibility.mcp_protocol).toBe('1.0');
  });

  test('formatSkill should throw on empty input', () => {
    expect(() => mcp.formatSkill('')).toThrow();
    expect(() => mcp.formatSkill(null)).toThrow();
  });
});

describe('Platform Registry', () => {
  test('should support all 7 platforms including mcp', () => {
    const supported = platforms.getSupportedPlatforms();
    expect(supported).toContain('opencode');
    expect(supported).toContain('openclaw');
    expect(supported).toContain('claude');
    expect(supported).toContain('cursor');
    expect(supported).toContain('openai');
    expect(supported).toContain('gemini');
    expect(supported).toContain('mcp');
    expect(supported).toHaveLength(7);
  });

  test('getPlatform should return adapter for valid platform', () => {
    const adapter = platforms.getPlatform('mcp');
    expect(adapter).toBeDefined();
    expect(adapter.name).toBe('mcp');
  });

  test('getPlatform should throw for unknown platform', () => {
    expect(() => platforms.getPlatform('unknown-platform')).toThrow();
  });

  test('isSupported should return true for known platforms', () => {
    expect(platforms.isSupported('mcp')).toBe(true);
    expect(platforms.isSupported('claude')).toBe(true);
  });

  test('isSupported should return false for unknown platforms', () => {
    expect(platforms.isSupported('unknown')).toBe(false);
  });

  test('all adapters should expose the standard interface', () => {
    const required = ['name', 'formatSkill', 'getInstallPath', 'generateMetadata', 'validateSkill'];
    platforms.getSupportedPlatforms().forEach(name => {
      const adapter = platforms.getPlatform(name);
      required.forEach(method => {
        expect(adapter[method]).toBeDefined();
      });
    });
  });

  test('formatForPlatform should format skill for mcp as JSON', () => {
    const result = platforms.formatForPlatform('mcp', VALID_SKILL);
    expect(() => JSON.parse(result)).not.toThrow();
  });

  test('getAllPlatformInfo should return info for all platforms', () => {
    const info = platforms.getAllPlatformInfo();
    expect(Object.keys(info)).toHaveLength(7);
    expect(info.mcp).toBeDefined();
    expect(info.mcp.name).toBe('mcp');
  });
});
