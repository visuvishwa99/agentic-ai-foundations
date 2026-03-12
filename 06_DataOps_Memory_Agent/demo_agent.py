"""
Demo Script for DataOps Memory Agent
Shows real-world usage and capabilities
"""

from dataops_memory_agent import DataOpsMemoryAgent, PipelineFailure
from datetime import datetime, timedelta
import json


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_analysis(analysis, test_name):
    """Pretty print analysis results"""
    print(f"\nAnalysis for: {test_name}")
    print("-" * 70)
    print(f"Error Category: {analysis['error_category']}")
    print(f"Confidence: {analysis['confidence']:.2%}")
    print(f"Pattern Detected: {analysis['pattern_detected']}")
    print(f"Pattern Description: {analysis['pattern_description']}")
    
    if analysis['affected_systems']:
        print(f"Affected Systems: {', '.join(analysis['affected_systems'][:5])}")
    
    print(f"\nRemediation Suggestions:")
    for i, suggestion in enumerate(analysis['remediation_suggestions'], 1):
        print(f"  {i}. {suggestion}")
    
    if analysis['similar_failures_details']:
        print(f"\nSimilar Past Failures:")
        for detail in analysis['similar_failures_details']:
            print(f"  - {detail['timestamp']}: {detail['pipeline']} ({detail['error']}) "
                  f"[similarity: {detail['similarity']}]")


def demo_scenario_1():
    """Demo: Detecting schema drift pattern"""
    print_section("SCENARIO 1: Detecting Schema Drift Pattern")
    
    agent = DataOpsMemoryAgent()
    base_time = datetime.now()
    
    # First schema error
    failure_1 = PipelineFailure(
        timestamp=(base_time - timedelta(hours=2)).isoformat(),
        pipeline_name='customer_360_etl',
        error_type='SchemaError',
        error_message='Column "loyalty_tier" not found in target table',
        stack_trace='File "transform.py", line 234 in merge_customer_data',
        affected_tables=['customers', 'customer_analytics'],
        duration_seconds=145,
        metadata={'version': '3.2.1', 'env': 'production'}
    )
    
    agent.log_failure(failure_1)
    analysis_1 = agent.identify_root_cause(failure_1)
    print_analysis(analysis_1, "First Schema Error")
    
    # Second schema error - should detect pattern
    failure_2 = PipelineFailure(
        timestamp=base_time.isoformat(),
        pipeline_name='customer_360_etl',
        error_type='SchemaError',
        error_message='Type mismatch: expected INTEGER for "customer_age", got VARCHAR',
        stack_trace='File "validator.py", line 89 in validate_schema',
        affected_tables=['customers', 'customer_analytics'],
        duration_seconds=98,
        metadata={'version': '3.2.1', 'env': 'production'}
    )
    
    agent.log_failure(failure_2)
    analysis_2 = agent.identify_root_cause(failure_2)
    print_analysis(analysis_2, "Second Schema Error - Pattern Detected!")
    
    print("\nKey Insight: Agent detected recurring schema issues, suggesting systematic "
          "schema validation problem")


def demo_scenario_2():
    """Demo: Multi-system data quality crisis"""
    print_section("SCENARIO 2: Multi-System Data Quality Crisis")
    
    agent = DataOpsMemoryAgent()
    base_time = datetime.now()
    
    # Multiple data quality failures across systems
    failures = [
        PipelineFailure(
            timestamp=(base_time - timedelta(hours=3)).isoformat(),
            pipeline_name='inventory_sync',
            error_type='ConstraintViolation',
            error_message='NULL value in non-nullable column "warehouse_id"',
            stack_trace='File "loader.py", line 456',
            affected_tables=['inventory', 'warehouses'],
            duration_seconds=67,
            metadata={'source': 'legacy_system_1'}
        ),
        PipelineFailure(
            timestamp=(base_time - timedelta(hours=2)).isoformat(),
            pipeline_name='order_processing',
            error_type='DataValidationError',
            error_message='Invalid email format for customer contact',
            stack_trace='File "validator.py", line 123',
            affected_tables=['orders', 'customers'],
            duration_seconds=45,
            metadata={'source': 'web_api'}
        ),
        PipelineFailure(
            timestamp=(base_time - timedelta(hours=1)).isoformat(),
            pipeline_name='product_enrichment',
            error_type='ConstraintViolation',
            error_message='Negative price value: -15.99',
            stack_trace='File "enrichment.py", line 234',
            affected_tables=['products', 'pricing'],
            duration_seconds=89,
            metadata={'source': 'partner_feed'}
        ),
        PipelineFailure(
            timestamp=base_time.isoformat(),
            pipeline_name='customer_segmentation',
            error_type='DataValidationError',
            error_message='NULL value in required field "signup_date"',
            stack_trace='File "segmentation.py", line 567',
            affected_tables=['customers', 'segments', 'analytics'],
            duration_seconds=134,
            metadata={'source': 'mobile_app'}
        )
    ]
    
    for failure in failures:
        agent.log_failure(failure)
    
    # Analyze the crisis
    analysis = agent.identify_root_cause(failures[-1])
    print_analysis(analysis, "Current Data Quality Crisis")
    
    stats = agent.get_memory_stats()
    print(f"\nMemory Statistics:")
    print(f"  Total failures tracked: {stats['total_failures_in_memory']}")
    print(f"  Error distribution: {stats['error_type_distribution']}")
    print(f"\nKey Insight: Multiple systems affected - suggests upstream data source issue")


def demo_scenario_3():
    """Demo: Performance degradation detection"""
    print_section("SCENARIO 3: Performance Degradation Detection")
    
    agent = DataOpsMemoryAgent()
    base_time = datetime.now()
    
    # Escalating timeout issues
    timeouts = [
        (180, "SELECT * FROM large_table JOIN bigger_table"),
        (245, "Complex aggregation query with 5 joins"),
        (310, "Full table scan on unindexed column")
    ]
    
    for i, (duration, description) in enumerate(timeouts):
        failure = PipelineFailure(
            timestamp=(base_time - timedelta(hours=3-i)).isoformat(),
            pipeline_name='analytics_pipeline',
            error_type='TimeoutError',
            error_message=f'Query execution exceeded {duration}s: {description}',
            stack_trace=f'File "query_engine.py", line {200+i*10}',
            affected_tables=['fact_sales', 'dim_products', 'dim_customers'],
            duration_seconds=duration + 5,
            metadata={'query_complexity': 'high', 'data_size_gb': 150 + i*50}
        )
        agent.log_failure(failure)
    
    # Analyze pattern
    analysis = agent.identify_root_cause(failure)
    print_analysis(analysis, "Escalating Timeout Issues")
    
    print(f"\nKey Insight: Pattern of timeouts with increasing duration suggests "
          "performance degradation")


def demo_comprehensive_report():
    """Demo: Generate comprehensive failure report"""
    print_section("SCENARIO 4: Comprehensive Week-in-Review")
    
    agent = DataOpsMemoryAgent()
    base_time = datetime.now()
    
    # Simulate a week of diverse failures
    weekly_failures = [
        ('schema_mismatch', 'customer_etl', 3),
        ('data_quality', 'inventory_sync', 4),
        ('timeout', 'analytics_job', 2),
        ('permission_denied', 'backup_job', 1),
        ('connection_error', 'external_api', 2)
    ]
    
    for error_type, pipeline, count in weekly_failures:
        for i in range(count):
            failure = PipelineFailure(
                timestamp=(base_time - timedelta(days=6-i, hours=i*2)).isoformat(),
                pipeline_name=pipeline,
                error_type=error_type,
                error_message=f'Sample {error_type} error #{i+1}',
                stack_trace='...',
                affected_tables=[pipeline.split('_')[0]],
                duration_seconds=100 + i*20,
                metadata={'occurrence': i+1}
            )
            agent.log_failure(failure)
    
    stats = agent.get_memory_stats()
    
    print("\nWeek-in-Review Summary:")
    print(f"  Total Failures: {stats['total_failures_in_memory']}")
    print(f"\n  Error Breakdown:")
    for error_type, count in stats['error_type_distribution'].items():
        print(f"    - {error_type}: {count} occurrences")
    
    print(f"\n  Top Issues to Address:")
    sorted_errors = sorted(stats['error_type_distribution'].items(), 
                          key=lambda x: x[1], reverse=True)
    
    for i, (error_type, count) in enumerate(sorted_errors[:3], 1):
        print(f"    {i}. {error_type} ({count} failures) - HIGH PRIORITY")


def main():
    """Run all demo scenarios"""
    print("\n" + "="*70)
    print("DATAOPS MEMORY AGENT - INTERACTIVE DEMO")
    print("="*70)
    print("\nThis demo showcases the agent's ability to:")
    print("  1. Classify errors accurately")
    print("  2. Detect recurring patterns")
    print("  3. Provide actionable remediation suggestions")
    print("  4. Use semantic memory to find similar past failures")
    
    demo_scenario_1()
    input("\n\nPress Enter to continue to Scenario 2...")
    
    demo_scenario_2()
    input("\n\nPress Enter to continue to Scenario 3...")
    
    demo_scenario_3()
    input("\n\nPress Enter to continue to Scenario 4...")
    
    demo_comprehensive_report()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Run 'python test_agent.py' for full test suite")
    print("  2. Integrate agent into your DataOps monitoring system")
    print("  3. Customize failure patterns and suggestions for your environment")
    print("  4. Set up automated alerting for detected patterns")


if __name__ == '__main__':
    main()
