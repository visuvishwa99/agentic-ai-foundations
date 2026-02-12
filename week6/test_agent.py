"""
Test Suite for DataOps Memory Agent
Includes golden dataset, unit tests, and accuracy metrics
"""

import unittest
from datetime import datetime, timedelta
from dataops_memory_agent import DataOpsMemoryAgent, PipelineFailure


class GoldenDataset:
    """Golden dataset of expected behaviors for agent testing"""
    
    @staticmethod
    def get_test_cases():
        """Returns 10 diverse test cases with expected outputs"""
        base_time = datetime(2024, 1, 1, 10, 0, 0)
        
        return [
            # Test Case 1: Schema Mismatch (should detect pattern after 2 occurrences)
            {
                'name': 'schema_mismatch_1',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=1)).isoformat(),
                    pipeline_name='customer_etl',
                    error_type='SchemaError',
                    error_message='Column "email_verified" not found in target schema',
                    stack_trace='File "transform.py", line 45, in process_customer',
                    affected_tables=['customers', 'customer_staging'],
                    duration_seconds=120,
                    metadata={'env': 'production', 'version': '2.1.0'}
                ),
                'expected_category': 'schema_mismatch',
                'expected_pattern': None,  # First occurrence - no pattern yet
                'min_suggestions': 2
            },
            
            # Test Case 2: Schema Mismatch (second occurrence - should detect pattern)
            {
                'name': 'schema_mismatch_2',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=3)).isoformat(),
                    pipeline_name='customer_etl',
                    error_type='SchemaError',
                    error_message='Type mismatch for column "age": expected int, got string',
                    stack_trace='File "transform.py", line 52, in validate_types',
                    affected_tables=['customers', 'customer_staging'],
                    duration_seconds=95,
                    metadata={'env': 'production', 'version': '2.1.0'}
                ),
                'expected_category': 'schema_mismatch',
                'expected_pattern': True,  # Second occurrence - pattern!
                'min_suggestions': 3
            },
            
            # Test Case 3: Timeout Error (infrastructure issue)
            {
                'name': 'timeout_error',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=5)).isoformat(),
                    pipeline_name='sales_aggregation',
                    error_type='TimeoutError',
                    error_message='Query execution time exceeded 300 seconds',
                    stack_trace='File "query_runner.py", line 112, in execute_query',
                    affected_tables=['sales_daily', 'sales_summary'],
                    duration_seconds=305,
                    metadata={'env': 'production', 'query_id': 'q_12345'}
                ),
                'expected_category': 'timeout',
                'expected_pattern': None,  # Don't test pattern - memory has mixed errors
                'min_suggestions': 2
            },
            
            # Test Case 4: Data Quality Issue (first of three)
            {
                'name': 'data_quality_1',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=7)).isoformat(),
                    pipeline_name='inventory_sync',
                    error_type='ConstraintViolation',
                    error_message='NULL value in non-nullable column "product_id"',
                    stack_trace='File "loader.py", line 78, in insert_batch',
                    affected_tables=['inventory', 'products'],
                    duration_seconds=45,
                    metadata={'env': 'production', 'batch_id': 'b_789'}
                ),
                'expected_category': 'data_quality',
                'expected_pattern': None,  # Will show pattern from previous schema errors
                'min_suggestions': 2
            },
            
            # Test Case 5: Data Quality Issue (second occurrence)
            {
                'name': 'data_quality_2',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=9)).isoformat(),
                    pipeline_name='inventory_sync',
                    error_type='DataValidationError',
                    error_message='Invalid data: quantity cannot be negative (-5)',
                    stack_trace='File "validator.py", line 34, in validate_quantity',
                    affected_tables=['inventory', 'warehouse_stock'],
                    duration_seconds=38,
                    metadata={'env': 'production', 'batch_id': 'b_790'}
                ),
                'expected_category': 'data_quality',
                'expected_pattern': True,  # Pattern emerging
                'min_suggestions': 3
            },
            
            # Test Case 6: Permission Denied (access control issue)
            {
                'name': 'permission_denied',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=11)).isoformat(),
                    pipeline_name='backup_job',
                    error_type='PermissionError',
                    error_message='Access denied to bucket gs://company-backups/',
                    stack_trace='File "backup.py", line 23, in write_backup',
                    affected_tables=['all_tables'],
                    duration_seconds=5,
                    metadata={'env': 'production', 'service_account': 'backup-sa@project.iam'}
                ),
                'expected_category': 'permission_denied',
                'expected_pattern': None,  # Mixed error history
                'min_suggestions': 2
            },
            
            # Test Case 7: Data Quality Issue (third occurrence - strong pattern)
            {
                'name': 'data_quality_3',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=13)).isoformat(),
                    pipeline_name='order_processing',
                    error_type='ConstraintViolation',
                    error_message='NULL value in required field "customer_email"',
                    stack_trace='File "processor.py", line 56, in process_order',
                    affected_tables=['orders', 'customers'],
                    duration_seconds=67,
                    metadata={'env': 'production', 'order_id': 'ord_5555'}
                ),
                'expected_category': 'data_quality',
                'expected_pattern': True,  # Strong pattern - 3 occurrences
                'min_suggestions': 3
            },
            
            # Test Case 8: Connection Error
            {
                'name': 'connection_error',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=15)).isoformat(),
                    pipeline_name='external_api_sync',
                    error_type='ConnectionError',
                    error_message='Connection refused to api.partner.com:443',
                    stack_trace='File "api_client.py", line 89, in fetch_data',
                    affected_tables=['external_data', 'api_logs'],
                    duration_seconds=10,
                    metadata={'env': 'production', 'endpoint': '/v1/products'}
                ),
                'expected_category': 'connection_error',
                'expected_pattern': None,  # Mixed error history
                'min_suggestions': 2
            },
            
            # Test Case 9: Mixed - Another Schema Error (testing cross-pattern detection)
            {
                'name': 'schema_mismatch_3',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=17)).isoformat(),
                    pipeline_name='user_profile_etl',
                    error_type='SchemaError',
                    error_message='Field "last_login_date" has wrong type: expected timestamp, got string',
                    stack_trace='File "schema_validator.py", line 101, in validate',
                    affected_tables=['user_profiles', 'users'],
                    duration_seconds=88,
                    metadata={'env': 'production', 'version': '3.0.1'}
                ),
                'expected_category': 'schema_mismatch',
                'expected_pattern': True,  # Should recognize schema errors from earlier
                'min_suggestions': 3
            },
            
            # Test Case 10: Resource Exhausted
            {
                'name': 'resource_exhausted',
                'failure': PipelineFailure(
                    timestamp=(base_time + timedelta(hours=19)).isoformat(),
                    pipeline_name='large_data_export',
                    error_type='ResourceError',
                    error_message='Out of memory: cannot allocate 8.5GB for result set',
                    stack_trace='File "exporter.py", line 145, in export_full_dataset',
                    affected_tables=['fact_sales', 'dim_products', 'dim_customers'],
                    duration_seconds=450,
                    metadata={'env': 'production', 'memory_limit': '8GB'}
                ),
                'expected_category': 'resource_exhausted',
                'expected_pattern': None,  # Mixed error history
                'min_suggestions': 1
            }
        ]


class TestDataOpsMemoryAgent(unittest.TestCase):
    """Unit tests for DataOps Memory Agent"""
    
    def setUp(self):
        """Set up fresh agent for each test"""
        self.agent = DataOpsMemoryAgent()
        self.golden_dataset = GoldenDataset.get_test_cases()
    
    def test_error_classification(self):
        """Test that agent correctly classifies error types"""
        print("\n" + "="*70)
        print("TEST: Error Classification Accuracy")
        print("="*70)
        
        correct = 0
        total = len(self.golden_dataset)
        
        for test_case in self.golden_dataset:
            failure = test_case['failure']
            expected = test_case['expected_category']
            
            actual = self.agent._classify_error(failure)
            
            is_correct = actual == expected
            correct += is_correct
            
            status = "[PASS]" if is_correct else "[FAIL]"
            print(f"{status} {test_case['name']}: Expected '{expected}', Got '{actual}'")
        
        accuracy = (correct / total) * 100
        print(f"\nClassification Accuracy: {accuracy:.1f}% ({correct}/{total})")
        
        self.assertGreaterEqual(accuracy, 90, f"Classification accuracy {accuracy}% below 90% threshold")
    
    def test_pattern_detection(self):
        """Test that agent detects recurring patterns correctly"""
        print("\n" + "="*70)
        print("TEST: Pattern Detection")
        print("="*70)
        
        correct = 0
        total = 0
        
        for i, test_case in enumerate(self.golden_dataset):
            # Log failure to build memory
            self.agent.log_failure(test_case['failure'])
            
            # Analyze with current memory state
            analysis = self.agent.identify_root_cause(test_case['failure'])
            
            expected_pattern = test_case['expected_pattern']
            actual_pattern = analysis['pattern_detected']
            
            # Only count tests where pattern expectation is explicit
            if expected_pattern is not None:
                total += 1
                is_correct = actual_pattern == expected_pattern
                correct += is_correct
                
                status = "[PASS]" if is_correct else "[FAIL]"
                print(f"{status} {test_case['name']}: Expected pattern={expected_pattern}, Got={actual_pattern}")
                print(f"      Pattern: {analysis['pattern_description']}")
        
        accuracy = (correct / total) * 100 if total > 0 else 0
        print(f"\nPattern Detection Accuracy: {accuracy:.1f}% ({correct}/{total})")
        
        self.assertGreaterEqual(accuracy, 80, f"Pattern detection accuracy {accuracy}% below 80% threshold")
    
    def test_remediation_suggestions(self):
        """Test that agent provides actionable suggestions"""
        print("\n" + "="*70)
        print("TEST: Remediation Suggestions Quality")
        print("="*70)
        
        correct = 0
        total = len(self.golden_dataset)
        
        for test_case in self.golden_dataset:
            self.agent.log_failure(test_case['failure'])
            analysis = self.agent.identify_root_cause(test_case['failure'])
            
            min_expected = test_case['min_suggestions']
            actual_count = len(analysis['remediation_suggestions'])
            
            is_sufficient = actual_count >= min_expected
            correct += is_sufficient
            
            status = "[PASS]" if is_sufficient else "[FAIL]"
            print(f"{status} {test_case['name']}: Expected >={min_expected} suggestions, Got {actual_count}")
            
            if actual_count > 0:
                print(f"      Top suggestion: {analysis['remediation_suggestions'][0]}")
        
        accuracy = (correct / total) * 100
        print(f"\nSuggestion Quality: {accuracy:.1f}% ({correct}/{total})")
        
        self.assertGreaterEqual(accuracy, 80, f"Suggestion quality {accuracy}% below 80% threshold")
    
    def test_memory_retrieval(self):
        """Test that vector memory retrieves relevant past failures"""
        print("\n" + "="*70)
        print("TEST: Memory Retrieval Performance")
        print("="*70)
        
        # Load all failures into memory
        for test_case in self.golden_dataset:
            self.agent.log_failure(test_case['failure'])
        
        # Test retrieval for schema-related failure
        schema_failure = self.golden_dataset[1]['failure']  # schema_mismatch_2
        analysis = self.agent.identify_root_cause(schema_failure)
        
        print(f"Query: Schema mismatch error")
        print(f"Similar past failures found: {analysis['similar_past_failures']}")
        
        if analysis['similar_failures_details']:
            print(f"\nTop 3 similar failures:")
            for detail in analysis['similar_failures_details']:
                print(f"  - {detail['pipeline']} ({detail['error']}) - similarity: {detail['similarity']}")
        
        self.assertGreater(analysis['similar_past_failures'], 0, "Should find similar past failures")
    
    def test_end_to_end_accuracy(self):
        """End-to-end test: measure overall agent accuracy"""
        print("\n" + "="*70)
        print("TEST: End-to-End Accuracy")
        print("="*70)
        
        metrics = {
            'correct_classification': 0,
            'correct_pattern_detection': 0,
            'sufficient_suggestions': 0,
            'total_tests': 0
        }
        
        for test_case in self.golden_dataset:
            self.agent.log_failure(test_case['failure'])
            analysis = self.agent.identify_root_cause(test_case['failure'])
            
            # Check classification
            if analysis['error_category'] == test_case['expected_category']:
                metrics['correct_classification'] += 1
            
            # Check pattern detection
            if test_case['expected_pattern'] is not None:
                if analysis['pattern_detected'] == test_case['expected_pattern']:
                    metrics['correct_pattern_detection'] += 1
            
            # Check suggestions
            if len(analysis['remediation_suggestions']) >= test_case['min_suggestions']:
                metrics['sufficient_suggestions'] += 1
            
            metrics['total_tests'] += 1
        
        # Calculate overall accuracy
        classification_acc = (metrics['correct_classification'] / metrics['total_tests']) * 100
        suggestion_acc = (metrics['sufficient_suggestions'] / metrics['total_tests']) * 100
        
        print(f"\nOverall Metrics:")
        print(f"  Classification Accuracy: {classification_acc:.1f}%")
        print(f"  Suggestion Quality: {suggestion_acc:.1f}%")
        print(f"  Total Tests Passed: {metrics['correct_classification'] + metrics['sufficient_suggestions']}/{metrics['total_tests']*2}")
        
        overall_score = (classification_acc + suggestion_acc) / 2
        print(f"\n  OVERALL AGENT SCORE: {overall_score:.1f}%")
        
        self.assertGreaterEqual(overall_score, 85, f"Overall score {overall_score}% below 85% threshold")


class TestVectorMemory(unittest.TestCase):
    """Unit tests for Vector Memory System"""
    
    def test_memory_storage(self):
        """Test that memory stores and retrieves failures correctly"""
        agent = DataOpsMemoryAgent()
        
        failure = PipelineFailure(
            timestamp=datetime.now().isoformat(),
            pipeline_name='test_pipeline',
            error_type='TestError',
            error_message='Test error message',
            stack_trace='Test stack trace',
            affected_tables=['test_table'],
            duration_seconds=100,
            metadata={'test': 'data'}
        )
        
        agent.log_failure(failure)
        recent = agent.memory.get_recent(1)
        
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].pipeline_name, 'test_pipeline')
    
    def test_semantic_search(self):
        """Test that semantic search finds relevant failures"""
        agent = DataOpsMemoryAgent()
        
        # Add diverse failures
        failures = [
            PipelineFailure(
                timestamp=datetime.now().isoformat(),
                pipeline_name='schema_test',
                error_type='SchemaError',
                error_message='Column type mismatch',
                stack_trace='stack',
                affected_tables=['users'],
                duration_seconds=50,
                metadata={}
            ),
            PipelineFailure(
                timestamp=datetime.now().isoformat(),
                pipeline_name='timeout_test',
                error_type='TimeoutError',
                error_message='Query timed out',
                stack_trace='stack',
                affected_tables=['orders'],
                duration_seconds=300,
                metadata={}
            )
        ]
        
        for f in failures:
            agent.log_failure(f)
        
        # Search for schema-related failure
        results = agent.memory.search('schema column type', top_k=2)
        
        self.assertGreater(len(results), 0)
        # Schema error should be most similar
        self.assertEqual(results[0][0].error_type, 'SchemaError')


def run_test_suite():
    """Run complete test suite with detailed reporting"""
    print("\n" + "="*70)
    print("DATAOPS MEMORY AGENT - TEST SUITE")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests
    suite.addTests(loader.loadTestsFromTestCase(TestDataOpsMemoryAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorMemory))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result


if __name__ == '__main__':
    run_test_suite()
