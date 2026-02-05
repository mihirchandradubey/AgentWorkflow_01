"""Command-line interface for Pega to Camunda migration accelerator."""

import click
import os
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parser.pega_parser import PegaParser
from src.parser.workflow_extractor import WorkflowExtractor
from src.converter.bpmn_generator import BPMNGenerator
from src.converter.dmn_generator import DMNGenerator
from src.converter.mapping_engine import MappingEngine
from src.analyzer.complexity_analyzer import ComplexityAnalyzer
from src.analyzer.dependency_analyzer import DependencyAnalyzer
from src.analyzer.pattern_detector import PatternDetector
from src.validator.bpmn_validator import BPMNValidator
from src.validator.schema_validator import SchemaValidator
from src.generator.migration_reporter import MigrationReporter
from src.generator.guide_builder import GuideBuilder
from src.utils.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Pega to Camunda Migration Accelerator CLI"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input Pega workflow file or directory')
@click.option('--output', '-o', required=True, help='Output directory for generated files')
@click.option('--batch', is_flag=True, help='Process multiple files in batch mode')
@click.option('--format', '-f', type=click.Choice(['xml', 'json']), default='xml', help='Input format')
def convert(input, output, batch, format):
    """Convert Pega workflow(s) to Camunda BPMN"""
    
    click.echo(f"🚀 Starting migration process...")
    click.echo(f"Input: {input}")
    click.echo(f"Output: {output}")
    
    # Create output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    
    # Get input files
    if batch:
        input_files = list(Path(input).glob('**/*.xml' if format == 'xml' else '**/*.json'))
        click.echo(f"Found {len(input_files)} files to process")
    else:
        input_files = [Path(input)]
    
    # Process each file
    for input_file in input_files:
        click.echo(f"\n📄 Processing: {input_file.name}")
        
        try:
            _process_single_workflow(str(input_file), output, format)
            click.echo(f"✅ Successfully processed {input_file.name}")
        except Exception as e:
            click.echo(f"❌ Error processing {input_file.name}: {str(e)}", err=True)
            logger.exception(f"Error processing {input_file}")
    
    click.echo(f"\n✨ Migration complete! Output saved to: {output}")


def _process_single_workflow(input_file: str, output_dir: str, format_type: str):
    """Process a single workflow file."""
    
    # Parse Pega workflow
    parser = PegaParser()
    workflow_data = parser.parse_file(input_file)
    
    if not workflow_data:
        raise ValueError("Failed to parse workflow file")
    
    workflow_name = workflow_data.get('name', 'workflow')
    base_filename = Path(input_file).stem
    
    # Extract workflow components
    extractor = WorkflowExtractor(workflow_data)
    
    # Generate BPMN
    bpmn_gen = BPMNGenerator()
    bpmn_xml = bpmn_gen.generate(workflow_data)
    
    # Save BPMN
    bpmn_output_path = os.path.join(output_dir, f"{base_filename}.bpmn")
    with open(bpmn_output_path, 'w') as f:
        f.write(bpmn_xml)
    
    # Generate DMN for decisions
    decision_elements = extractor.get_decision_elements()
    if decision_elements:
        dmn_gen = DMNGenerator()
        for decision in decision_elements:
            dmn_xml = dmn_gen.generate_from_pega_decision(decision)
            dmn_filename = f"{base_filename}_{decision.get('id', 'decision')}.dmn"
            dmn_output_path = os.path.join(output_dir, dmn_filename)
            with open(dmn_output_path, 'w') as f:
                f.write(dmn_xml)
    
    # Run analysis
    analysis_results = _run_analysis(workflow_data)
    
    # Validate BPMN
    validator = BPMNValidator()
    validation_results = validator.validate(bpmn_xml)
    
    # Generate report
    reporter = MigrationReporter(workflow_name)
    report = reporter.build_comprehensive_report(
        workflow_data,
        analysis_results,
        validation_results
    )
    
    report_path = os.path.join(output_dir, f"{base_filename}_report.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Generate implementation guide
    guide_builder = GuideBuilder()
    impl_guide = guide_builder.create_implementation_manual(workflow_data, bpmn_xml)
    
    guide_path = os.path.join(output_dir, f"{base_filename}_implementation.md")
    with open(guide_path, 'w') as f:
        f.write(impl_guide)


def _run_analysis(workflow_data: dict) -> dict:
    """Run all analysis tools on workflow."""
    
    results = {}
    
    # Complexity analysis
    complexity_analyzer = ComplexityAnalyzer()
    results['complexity'] = complexity_analyzer.analyze(workflow_data)
    
    # Pattern detection
    pattern_detector = PatternDetector()
    results['patterns'] = pattern_detector.detect(workflow_data)
    
    # Dependency analysis
    dependency_analyzer = DependencyAnalyzer()
    results['dependencies'] = dependency_analyzer.analyze(workflow_data)
    
    return results


@cli.command()
@click.option('--input', '-i', required=True, help='Input Pega workflow file')
@click.option('--output', '-o', help='Output file for analysis report')
def analyze(input, output):
    """Analyze Pega workflow complexity and dependencies"""
    
    click.echo(f"🔍 Analyzing workflow: {input}")
    
    # Parse workflow
    parser = PegaParser()
    workflow_data = parser.parse_file(input)
    
    if not workflow_data:
        click.echo("❌ Failed to parse workflow file", err=True)
        return
    
    # Run analysis
    analysis_results = _run_analysis(workflow_data)
    
    # Display results
    click.echo("\n" + "="*60)
    click.echo("COMPLEXITY ANALYSIS")
    click.echo("="*60)
    
    complexity = analysis_results['complexity']
    click.echo(f"Complexity Level: {complexity.get('complexity_level')}")
    click.echo(f"Complexity Score: {complexity.get('complexity_score', 0):.1f}")
    
    effort = complexity.get('effort_estimate', {})
    click.echo(f"\nEstimated Effort:")
    click.echo(f"  - Days: {effort.get('estimated_days', 0):.1f}")
    click.echo(f"  - Hours: {effort.get('estimated_hours', 0):.1f}")
    click.echo(f"  - Automation: {effort.get('automation_percentage', 0)}%")
    
    # Patterns
    click.echo("\n" + "="*60)
    click.echo("PATTERNS DETECTED")
    click.echo("="*60)
    
    patterns = analysis_results['patterns']
    for pattern_name, pattern_info in patterns.get('patterns', {}).items():
        click.echo(f"✓ {pattern_name}: {pattern_info.get('description', '')}")
    
    # Dependencies
    click.echo("\n" + "="*60)
    click.echo("DEPENDENCIES")
    click.echo("="*60)
    
    deps = analysis_results['dependencies']
    external = deps.get('external_dependencies', {})
    click.echo(f"External Systems: {external.get('count', 0)}")
    
    subprocess_deps = deps.get('subprocess_dependencies', {})
    click.echo(f"Subprocesses: {subprocess_deps.get('count', 0)}")
    
    # Save report if output specified
    if output:
        reporter = MigrationReporter(workflow_data.get('name', 'Workflow'))
        report = reporter.build_comprehensive_report(
            workflow_data,
            analysis_results,
            {'valid': True, 'errors': [], 'warnings': []}
        )
        
        with open(output, 'w') as f:
            f.write(report)
        
        click.echo(f"\n📝 Full report saved to: {output}")


@cli.command()
@click.option('--input', '-i', required=True, help='Input BPMN file to validate')
def validate(input):
    """Validate generated BPMN file"""
    
    click.echo(f"🔍 Validating BPMN: {input}")
    
    # Read BPMN file
    with open(input, 'r') as f:
        bpmn_content = f.read()
    
    # Validate
    validator = BPMNValidator()
    results = validator.validate(bpmn_content)
    
    # Display results
    if results['valid']:
        click.echo("✅ BPMN is valid!")
    else:
        click.echo("❌ BPMN validation failed")
    
    if results['errors']:
        click.echo("\nErrors:")
        for error in results['errors']:
            click.echo(f"  ✗ {error}")
    
    if results['warnings']:
        click.echo("\nWarnings:")
        for warning in results['warnings'][:10]:
            click.echo(f"  ⚠ {warning}")
        if len(results['warnings']) > 10:
            click.echo(f"  ... and {len(results['warnings']) - 10} more warnings")
    
    if results['suggestions']:
        click.echo("\nSuggestions:")
        for suggestion in results['suggestions']:
            click.echo(f"  💡 {suggestion}")


@cli.command()
def init():
    """Initialize a new Camunda project structure"""
    
    click.echo("🏗️  Initializing Camunda project structure...")
    
    directories = [
        'src/main/java/com/example/delegates',
        'src/main/java/com/example/listeners',
        'src/main/resources/processes',
        'src/main/resources/dmn',
        'src/test/java/com/example'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        click.echo(f"  Created: {directory}")
    
    click.echo("\n✅ Project structure initialized!")
    click.echo("📋 Next steps:")
    click.echo("  1. Copy generated BPMN files to src/main/resources/processes/")
    click.echo("  2. Copy generated DMN files to src/main/resources/dmn/")
    click.echo("  3. Implement service task delegates in src/main/java/com/example/delegates/")


if __name__ == '__main__':
    cli()
