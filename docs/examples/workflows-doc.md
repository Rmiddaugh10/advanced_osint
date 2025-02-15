# Creating Custom Workflows in OSINT Framework

This guide explains how to create and use custom workflows in the OSINT Framework. Workflows allow you to orchestrate complex scanning and analysis procedures by combining multiple modules and processing steps in a structured way.

## Understanding Workflows

A workflow in the OSINT Framework coordinates multiple operations to achieve specific security assessment goals. Think of a workflow as a recipe that specifies what steps to take, in what order, and how to handle the results of each step.

### Basic Workflow Structure

Let's start with a basic workflow that demonstrates the fundamental concepts:

```python
from osint.framework import OSINTFramework, WorkflowBuilder
from osint.workflows import BaseWorkflow
from typing import Dict, Any, List

class BasicSecurityWorkflow(BaseWorkflow):
    """
    A basic security assessment workflow that demonstrates the fundamental
    structure of OSINT Framework workflows.
    """

    def __init__(self, framework: OSINTFramework, config: Dict[str, Any]):
        super().__init__(framework, config)
        self.results = {
            'phases': {},
            'findings': [],
            'recommendations': []
        }

    async def execute(self, target: str) -> Dict[str, Any]:
        """Execute the workflow phases in sequence."""
        try:
            # Phase 1: Initial Reconnaissance
            self.results['phases']['recon'] = await self._perform_reconnaissance(target)

            # Phase 2: Detailed Analysis
            self.results['phases']['analysis'] = await self._perform_analysis(target)

            # Phase 3: Risk Assessment
            self.results['phases']['risks'] = await self._assess_risks()

            # Phase 4: Generate Recommendations
            self.results['recommendations'] = await self._generate_recommendations()

            return self.results

        except Exception as e:
            self.logger.error(f"Workflow execution error: {str(e)}")
            raise WorkflowExecutionError(f"Failed to execute workflow: {str(e)}")

    async def _perform_reconnaissance(self, target: str) -> Dict[str, Any]:
        """Perform initial reconnaissance using passive modules."""
        recon_results = {}
        
        # Run passive reconnaissance modules
        passive_scan = await self.framework.scan_with_modules(
            target,
            ['passive_recon']
        )
        recon_results['passive'] = passive_scan.data

        # Gather domain information
        dns_info = await self.framework.scan_with_modules(
            target,
            ['dns_enumeration']
        )
        recon_results['dns'] = dns_info.data

        return recon_results

    async def _perform_analysis(self, target: str) -> Dict[str, Any]:
        """Perform detailed analysis using active modules."""
        analysis_results = {}
        
        # Run security analysis modules
        security_scan = await self.framework.scan_with_modules(
            target,
            ['security_headers', 'ssl_analysis']
        )
        analysis_results['security'] = security_scan.data

        # Run technology detection
        tech_scan = await self.framework.scan_with_modules(
            target,
            ['tech_detection']
        )
        analysis_results['technologies'] = tech_scan.data

        return analysis_results

    async def _assess_risks(self) -> Dict[str, Any]:
        """Assess risks based on gathered information."""
        risk_assessment = {
            'risk_score': 0,
            'risk_factors': [],
            'critical_issues': [],
            'warnings': []
        }

        # Analyze security findings
        security_data = self.results['phases']['analysis']['security']
        await self._analyze_security_risks(security_data, risk_assessment)

        # Analyze technology risks
        tech_data = self.results['phases']['analysis']['technologies']
        await self._analyze_technology_risks(tech_data, risk_assessment)

        return risk_assessment

    async def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        # Process risk assessment
        risk_data = self.results['phases']['risks']
        
        # Generate recommendations for critical issues
        for issue in risk_data['critical_issues']:
            recommendations.append({
                'priority': 'high',
                'finding': issue,
                'recommendation': self._get_recommendation_for_issue(issue),
                'remediation_steps': self._get_remediation_steps(issue)
            })

        # Generate recommendations for warnings
        for warning in risk_data['warnings']:
            recommendations.append({
                'priority': 'medium',
                'finding': warning,
                'recommendation': self._get_recommendation_for_warning(warning),
                'remediation_steps': self._get_remediation_steps(warning)
            })

        return recommendations
```

### Creating Advanced Workflows

Let's create a more sophisticated workflow for comprehensive security assessment:

```python
class ComprehensiveSecurityWorkflow(BaseWorkflow):
    """
    A comprehensive security assessment workflow that performs
    detailed analysis across multiple security domains.
    """

    def __init__(self, framework: OSINTFramework, config: Dict[str, Any]):
        super().__init__(framework, config)
        self.results = {
            'phases': {},
            'findings': [],
            'recommendations': [],
            'metrics': {},
            'timeline': []
        }
        self.start_time = None

    async def execute(self, target: str) -> Dict[str, Any]:
        """Execute the comprehensive workflow."""
        self.start_time = datetime.now()
        self._log_phase('Starting comprehensive security assessment')

        try:
            # Phase 1: Infrastructure Analysis
            await self._analyze_infrastructure(target)

            # Phase 2: Security Posture Assessment
            await self._assess_security_posture(target)

            # Phase 3: Vulnerability Analysis
            await self._analyze_vulnerabilities(target)

            # Phase 4: Exposure Assessment
            await self._assess_exposure(target)

            # Phase 5: Final Analysis and Reporting
            await self._generate_final_analysis()

            self._log_phase('Assessment completed successfully')
            return self.results

        except Exception as e:
            self._log_phase(f'Assessment failed: {str(e)}')
            raise

    async def _analyze_infrastructure(self, target: str):
        """Analyze target infrastructure."""
        self._log_phase('Starting infrastructure analysis')

        # Perform DNS analysis
        dns_results = await self.framework.scan_with_modules(
            target,
            ['dns_enumeration', 'reverse_dns']
        )
        self.results['phases']['infrastructure'] = {
            'dns': dns_results.data
        }

        # Analyze hosting infrastructure
        hosting_results = await self.framework.scan_with_modules(
            target,
            ['hosting_analysis', 'cdn_detection']
        )
        self.results['phases']['infrastructure']['hosting'] = hosting_results.data

    async def _assess_security_posture(self, target: str):
        """Assess security posture including configurations and policies."""
        self._log_phase('Starting security posture assessment')

        # Check security headers and SSL configuration
        security_results = await self.framework.scan_with_modules(
            target,
            ['security_headers', 'ssl_analysis', 'policy_check']
        )
        self.results['phases']['security_posture'] = security_results.data

    async def _analyze_vulnerabilities(self, target: str):
        """Perform vulnerability analysis."""
        self._log_phase('Starting vulnerability analysis')

        # Scan for common vulnerabilities
        vuln_results = await self.framework.scan_with_modules(
            target,
            ['vulnerability_scan', 'misconfiguration_check']
        )
        self.results['phases']['vulnerabilities'] = vuln_results.data

    async def _assess_exposure(self, target: str):
        """Assess public exposure and potential data leaks."""
        self._log_phase('Starting exposure assessment')

        # Check for exposed information
        exposure_results = await self.framework.scan_with_modules(
            target,
            ['data_leak_check', 'credential_exposure', 'social_media']
        )
        self.results['phases']['exposure'] = exposure_results.data

    async def _generate_final_analysis(self):
        """Generate final analysis and recommendations."""
        self._log_phase('Generating final analysis')

        # Calculate risk metrics
        self.results['metrics'] = await self._calculate_risk_metrics()

        # Generate prioritized recommendations
        self.results['recommendations'] = await self._generate_recommendations()

        # Create executive summary
        self.results['executive_summary'] = self._create_executive_summary()

    def _log_phase(self, message: str):
        """Log workflow phase with timestamp."""
        timestamp = datetime.now()
        duration = timestamp - self.start_time if self.start_time else None
        
        self.results['timeline'].append({
            'timestamp': timestamp.isoformat(),
            'duration': str(duration) if duration else None,
            'message': message
        })
        self.logger.info(f"[{timestamp}] {message}")
```

## Using Workflows

Here's how to use workflows in your security assessments:

```python
# Initialize the framework and workflow
framework = OSINTFramework()
config = {
    'scan_depth': 'comprehensive',
    'risk_tolerance': 'low',
    'report_format': 'detailed'
}

# Create and execute the workflow
workflow = ComprehensiveSecurityWorkflow(framework, config)
results = await workflow.execute("example.com")

# Process the results
print(f"Assessment completed with {len(results['recommendations'])} recommendations")
for recommendation in results['recommendations']:
    print(f"Priority: {recommendation['priority']}")
    print(f"Finding: {recommendation['finding']}")
    print(f"Recommendation: {recommendation['recommendation']}")
    print("Remediation Steps:")
    for step in recommendation['remediation_steps']:
        print(f"- {step}")
```

## Workflow Best Practices

When creating custom workflows, follow these guidelines:

1. Structured Phases: Organize your workflow into clear, logical phases:
```python
async def execute(self, target: str):
    # Clear phase structure
    await self._phase_1_reconnaissance()
    await self._phase_2_analysis()
    await self._phase_3_assessment()
    await self._phase_4_reporting()
```

2. Error Handling: Implement comprehensive error handling:
```python
try:
    result = await self._execute_phase()
except PhaseExecutionError as e:
    self._log_phase_error(e)
    await self._handle_phase_failure()
except Exception as e:
    self._log_critical_error(e)
    raise WorkflowError(f"Unexpected error: {str(e)}")
```

3. Progress Tracking: Maintain detailed progress information:
```python
def _log_progress(self, phase: str, progress: float, message: str):
    self.results['progress'] = {
        'phase': phase,
        'percentage': progress,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
```

4. Resource Management: Properly manage system resources:
```python
async def _execute_phase(self):
    async with self._resource_lock:
        try:
            await self._acquire_resources()
            result = await self._run_phase_operations()
            return result
        finally:
            await self._release_resources()
```

5. Documentation: Maintain clear documentation:
```python
class DocumentedWorkflow(BaseWorkflow):
    """
    A well-documented workflow that demonstrates proper documentation practices.

    This workflow performs:
    1. Initial reconnaissance
    2. Detailed analysis
    3. Risk assessment
    4. Recommendation generation

    Configuration Options:
        - scan_depth: Depth of scanning (basic, standard, comprehensive)
        - risk_tolerance: Risk tolerance level (high, medium, low)
        - report_format: Format of final report (basic, detailed, executive)
    """
```

Remember that workflows should be designed to provide clear, actionable results that help improve the security posture of the target system. Always ensure your workflows follow security best practices and handle sensitive information appropriately.

