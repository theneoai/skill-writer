/**
 * Validate Command
 *
 * Validates the core engine structure by checking directory structure,
 * YAML file parseability, required files, and template placeholders.
 *
 * @module builder/src/commands/validate
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const chalk = require('chalk');
const glob = require('glob');

// Configuration
const CORE_ENGINE_PATH = path.resolve(__dirname, '../../../core');
const TEMPLATES_PATH = path.resolve(__dirname, '../../../templates');
const PLATFORMS_PATH = path.resolve(__dirname, '../../../platforms');

// Required use_to_evolve fields
const REQUIRED_UTE_FIELDS = [
  'enabled', 'injected_by', 'injected_at', 'check_cadence',
  'micro_patch_enabled', 'feedback_detection', 'certified_lean_score',
  'last_ute_check', 'pending_patches', 'total_micro_patches_applied',
  'cumulative_invocations',
];

// Required directory structure
const REQUIRED_DIRECTORIES = [
  'create',
  'evaluate',
  'optimize',
  'shared',
  'create/templates',
  'shared/security',
  'shared/utils',
];

// Required YAML files
const REQUIRED_YAML_FILES = [
  'create/workflow.yaml',
  'create/elicitation.yaml',
  'evaluate/phases.yaml',
  'evaluate/rubrics.yaml',
  'evaluate/certification.yaml',
  'optimize/dimensions.yaml',
  'optimize/strategies.yaml',
  'optimize/convergence.yaml',
  'shared/security/cwe-patterns.yaml',
  'shared/utils/helpers.yaml',
];

// Required template files
const REQUIRED_TEMPLATE_FILES = [
  'base.md',
];

// Placeholder pattern for templates
const PLACEHOLDER_PATTERN = /\{\{[A-Z_0-9]+\}\}/g;

/**
 * Validation result structure
 * @typedef {Object} ValidationResult
 * @property {boolean} valid - Whether validation passed
 * @property {number} errors - Number of errors found
 * @property {number} warnings - Number of warnings found
 * @property {Array<Object>} issues - Detailed list of issues
 */

/**
 * Main validate function - validates the core engine structure
 *
 * @returns {Promise<ValidationResult>} Validation result with status and issues
 */
async function validate() {
  console.log(chalk.blue.bold('\n🔍 Validating Core Engine Structure\n'));

  const result = {
    valid: true,
    errors: 0,
    warnings: 0,
    issues: [],
  };

  // Run all validation checks
  await validateDirectoryStructure(result);
  await validateYamlFiles(result);
  await validateRequiredFiles(result);
  await validateTemplates(result);
  await validateGeneratedSkills(result);

  // Print summary
  printSummary(result);

  return result;
}

/**
 * Validate directory structure exists
 *
 * @param {ValidationResult} result - Validation result object to update
 */
async function validateDirectoryStructure(result) {
  console.log(chalk.cyan('📁 Checking directory structure...'));

  for (const dir of REQUIRED_DIRECTORIES) {
    const fullPath = path.join(CORE_ENGINE_PATH, dir);

    try {
      const stats = await fs.promises.stat(fullPath);
      if (!stats.isDirectory()) {
        addIssue(result, 'error', `Path exists but is not a directory: ${dir}`);
      } else {
        console.log(chalk.green(`  ✓ ${dir}`));
      }
    } catch (error) {
      if (error.code === 'ENOENT') {
        addIssue(result, 'error', `Missing required directory: ${dir}`);
      } else {
        addIssue(result, 'error', `Cannot access directory ${dir}: ${error.message}`);
      }
    }
  }

  console.log('');
}

/**
 * Validate YAML files are parseable
 *
 * @param {ValidationResult} result - Validation result object to update
 */
async function validateYamlFiles(result) {
  console.log(chalk.cyan('📄 Validating YAML files...'));

  // Find all YAML files in core directory
  const yamlPattern = path.join(CORE_ENGINE_PATH, '**/*.yaml');
  const yamlFiles = glob.sync(yamlPattern);

  if (yamlFiles.length === 0) {
    addIssue(result, 'warning', 'No YAML files found in core engine');
    console.log('');
    return;
  }

  console.log(chalk.gray(`  Found ${yamlFiles.length} YAML file(s)`));

  for (const filePath of yamlFiles) {
    const relativePath = path.relative(CORE_ENGINE_PATH, filePath);

    try {
      const content = await fs.promises.readFile(filePath, 'utf8');

      if (!content.trim()) {
        addIssue(result, 'warning', `Empty YAML file: ${relativePath}`);
        console.log(chalk.yellow(`  ⚠ ${relativePath} (empty)`));
        continue;
      }

      // Attempt to parse YAML
      yaml.load(content);
      console.log(chalk.green(`  ✓ ${relativePath}`));
    } catch (error) {
      if (error.name === 'YAMLException') {
        addIssue(result, 'error', `Invalid YAML in ${relativePath}: ${error.message}`);
        console.log(chalk.red(`  ✗ ${relativePath} (parse error)`));
      } else {
        addIssue(result, 'error', `Cannot read ${relativePath}: ${error.message}`);
        console.log(chalk.red(`  ✗ ${relativePath} (read error)`));
      }
    }
  }

  console.log('');
}

/**
 * Check required files are present
 *
 * @param {ValidationResult} result - Validation result object to update
 */
async function validateRequiredFiles(result) {
  console.log(chalk.cyan('📋 Checking required files...'));

  // Check required YAML files
  for (const file of REQUIRED_YAML_FILES) {
    const fullPath = path.join(CORE_ENGINE_PATH, file);

    try {
      await fs.promises.access(fullPath, fs.constants.F_OK);
      console.log(chalk.green(`  ✓ ${file}`));
    } catch {
      addIssue(result, 'error', `Missing required file: ${file}`);
      console.log(chalk.red(`  ✗ ${file} (missing)`));
    }
  }

  // Check required template files
  for (const file of REQUIRED_TEMPLATE_FILES) {
    const fullPath = path.join(TEMPLATES_PATH, file);

    try {
      await fs.promises.access(fullPath, fs.constants.F_OK);
      console.log(chalk.green(`  ✓ templates/${file}`));
    } catch {
      addIssue(result, 'error', `Missing required template: templates/${file}`);
      console.log(chalk.red(`  ✗ templates/${file} (missing)`));
    }
  }

  console.log('');
}

/**
 * Validate templates have placeholders
 *
 * @param {ValidationResult} result - Validation result object to update
 */
async function validateTemplates(result) {
  console.log(chalk.cyan('🎨 Validating templates...'));

  // Find all template files
  const templatePattern = path.join(TEMPLATES_PATH, '*.md');
  const templateFiles = glob.sync(templatePattern);

  if (templateFiles.length === 0) {
    addIssue(result, 'warning', 'No template files found');
    console.log('');
    return;
  }

  console.log(chalk.gray(`  Found ${templateFiles.length} template file(s)`));

  for (const filePath of templateFiles) {
    const relativePath = path.relative(path.dirname(TEMPLATES_PATH), filePath);

    try {
      const content = await fs.promises.readFile(filePath, 'utf8');

      if (!content.trim()) {
        addIssue(result, 'warning', `Empty template file: ${relativePath}`);
        console.log(chalk.yellow(`  ⚠ ${relativePath} (empty)`));
        continue;
      }

      // Check for placeholders
      const placeholders = content.match(PLACEHOLDER_PATTERN);

      if (!placeholders || placeholders.length === 0) {
        addIssue(result, 'warning', `Template has no placeholders: ${relativePath}`);
        console.log(chalk.yellow(`  ⚠ ${relativePath} (no placeholders)`));
      } else {
        const uniquePlaceholders = [...new Set(placeholders)];
        console.log(chalk.green(`  ✓ ${relativePath} (${uniquePlaceholders.length} placeholders)`));
      }

      // Check for unmodified example placeholder (must be replaced before delivery)
      if (content.includes('{{PLACEHOLDER}}')) {
        addIssue(result, 'error', `Template contains unmodified {{PLACEHOLDER}} marker: ${relativePath}`);
        console.log(chalk.red(`  ✗ ${relativePath} (contains {{PLACEHOLDER}})`));
      }

    } catch (error) {
      addIssue(result, 'error', `Cannot read template ${relativePath}: ${error.message}`);
      console.log(chalk.red(`  ✗ ${relativePath} (read error)`));
    }
  }

  console.log('');
}

/**
 * Validate generated platform skill files for structural completeness
 *
 * Checks each platforms/*.md for:
 *  - ≥3 §N sections
 *  - Red Lines / 严禁 section
 *  - use_to_evolve: YAML block with all 11 required fields
 *  - §UTE Use-to-Evolve body section
 *  - No remaining {{PLACEHOLDER}} tokens
 *
 * @param {ValidationResult} result - Validation result object to update
 */
async function validateGeneratedSkills(result) {
  console.log(chalk.cyan('🧪 Validating generated skill files...'));

  let skillFiles;
  try {
    skillFiles = glob.sync(path.join(PLATFORMS_PATH, '*.md'));
  } catch {
    skillFiles = [];
  }

  if (skillFiles.length === 0) {
    addIssue(result, 'warning', 'No generated skill files found in platforms/');
    console.log(chalk.yellow('  ⚠ No skill files found (run build first)\n'));
    return;
  }

  console.log(chalk.gray(`  Found ${skillFiles.length} skill file(s)`));

  for (const filePath of skillFiles) {
    const fileName = path.basename(filePath);
    let content;

    try {
      content = await fs.promises.readFile(filePath, 'utf8');
    } catch (error) {
      addIssue(result, 'error', `Cannot read ${fileName}: ${error.message}`);
      continue;
    }

    let fileOk = true;

    // Check §N section count (≥3)
    const sectionMatches = content.match(/^##\s+§\d+\s+\S/gm) || [];
    if (sectionMatches.length < 3) {
      addIssue(result, 'error', `${fileName}: fewer than 3 §N sections (found ${sectionMatches.length})`);
      fileOk = false;
    }

    // Check Red Lines / 严禁
    if (!/严禁|Red Lines/i.test(content)) {
      addIssue(result, 'error', `${fileName}: missing Red Lines (严禁) section`);
      fileOk = false;
    }

    // Check use_to_evolve block and all 11 required fields
    if (!content.includes('use_to_evolve:')) {
      addIssue(result, 'error', `${fileName}: missing use_to_evolve: YAML block`);
      fileOk = false;
    } else {
      for (const field of REQUIRED_UTE_FIELDS) {
        if (!content.includes(`${field}:`)) {
          addIssue(result, 'error', `${fileName}: use_to_evolve missing field '${field}'`);
          fileOk = false;
        }
      }
    }

    // Check §UTE body section
    if (!/##\s+§UTE\b/i.test(content)) {
      addIssue(result, 'error', `${fileName}: missing ## §UTE Use-to-Evolve body section`);
      fileOk = false;
    }

    // No remaining {{PLACEHOLDER}} tokens (error)
    if (/\{\{[A-Z_0-9]+\}\}/.test(content)) {
      const remaining = (content.match(/\{\{[A-Z_0-9]+\}\}/g) || []);
      const unique = [...new Set(remaining)];
      addIssue(result, 'error', `${fileName}: ${unique.length} unreplaced placeholder(s): ${unique.slice(0, 5).join(', ')}`);
      fileOk = false;
    }

    if (fileOk) {
      console.log(chalk.green(`  ✓ ${fileName}`));
    } else {
      console.log(chalk.red(`  ✗ ${fileName} (see issues above)`));
    }
  }

  console.log('');
}

/**
 * Add an issue to the validation result
 *
 * @param {ValidationResult} result - Validation result object
 * @param {string} type - Issue type ('error' or 'warning')
 * @param {string} message - Issue description
 */
function addIssue(result, type, message) {
  result.issues.push({
    type,
    message,
    timestamp: new Date().toISOString(),
  });

  if (type === 'error') {
    result.errors++;
    result.valid = false;
  } else {
    result.warnings++;
  }
}

/**
 * Print validation summary
 *
 * @param {ValidationResult} result - Validation result object
 */
function printSummary(result) {
  console.log(chalk.blue.bold('━'.repeat(50)));
  console.log(chalk.bold('📊 Validation Summary\n'));

  if (result.valid && result.warnings === 0) {
    console.log(chalk.green.bold('✅ All checks passed!'));
  } else if (result.valid) {
    console.log(chalk.yellow.bold('⚠️  Validation passed with warnings'));
  } else {
    console.log(chalk.red.bold('❌ Validation failed'));
  }

  console.log(chalk.gray(`\n  Errors:   ${result.errors > 0 ? chalk.red(result.errors) : chalk.green(result.errors)}`));
  console.log(chalk.gray(`  Warnings: ${result.warnings > 0 ? chalk.yellow(result.warnings) : chalk.green(result.warnings)}`));

  if (result.issues.length > 0) {
    console.log(chalk.bold('\n📋 Issues:\n'));
    result.issues.forEach((issue, index) => {
      const color = issue.type === 'error' ? chalk.red : chalk.yellow;
      const icon = issue.type === 'error' ? '✗' : '⚠';
      console.log(color(`  ${icon} ${issue.message}`));
    });
  }

  console.log(chalk.blue.bold('\n' + '━'.repeat(50) + '\n'));
}

module.exports = {
  validate,
  validateDirectoryStructure,
  validateYamlFiles,
  validateRequiredFiles,
  validateTemplates,
  validateGeneratedSkills,
};
