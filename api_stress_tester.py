# api_stress_tester.py
import requests
import time
import logging
import threading
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from api_config import API_CONFIG, API_SUCCESS_CRITERIA, HTTP_CONFIG, LOGGING_CONFIG
import psutil
import datetime

# Setup logging based on config
if LOGGING_CONFIG['log_to_file']:
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['log_file']),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format']
    )

class APITester:
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.auth_type = API_CONFIG['auth_type']
        self.session = requests.Session()
        self.setup_auth()
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        self.lock = threading.Lock()

    def setup_auth(self):
        """Setup authentication based on config"""
        if self.auth_type == 'bearer':
            self.session.headers.update({
                'Authorization': f"Bearer {API_CONFIG['auth_token']}"
            })
        elif self.auth_type == 'api_key':
            self.session.headers.update({
                'X-API-Key': API_CONFIG['api_key']
            })
        elif self.auth_type == 'basic':
            self.session.auth = (
                API_CONFIG['username'], 
                API_CONFIG['password']
            )

    def generate_dummy_data(self, method, path):
        """Generate realistic dummy data based on endpoint"""
        if method == 'GET':
            return None
        
        # Generate generic dummy data based on common patterns
        # This is now truly general and not hardcoded to specific endpoints
        dummy_data = {
            'id': random.randint(1, 10000),
            'name': f'Test Item {random.randint(1, 1000)}',
            'description': f'Test description {random.randint(1, 1000)}',
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'status': random.choice(['active', 'inactive', 'pending']),
            'value': random.randint(1, 1000),
            'price': round(random.uniform(10.0, 1000.0), 2),
            'email': f'test{random.randint(1, 1000)}@example.com',
            'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'address': f'{random.randint(1, 9999)} Test Street, Test City, TS {random.randint(10000, 99999)}',
            'category': random.choice(['category1', 'category2', 'category3']),
            'tags': [f'tag{random.randint(1, 5)}' for _ in range(random.randint(1, 3))],
            'metadata': {
                'test_data': True,
                'generated_at': int(time.time()),
                'random_id': random.randint(1, 1000000)
            }
        }
        
        # Return a subset of fields to avoid overwhelming APIs
        # This makes it more realistic and less likely to cause validation errors
        return {k: v for k, v in dummy_data.items() if random.random() > 0.3}

    def make_request(self, endpoint):
        """Make a single API request"""
        method = endpoint['method']
        path = endpoint['path']
        expected_status = endpoint['expected_status']
        
        url = f"{self.base_url}{path}"
        data = self.generate_dummy_data(method, path)
        
        # Set default headers
        headers = HTTP_CONFIG['headers'].copy()
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=HTTP_CONFIG['timeout_seconds'], headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=HTTP_CONFIG['timeout_seconds'], headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, timeout=HTTP_CONFIG['timeout_seconds'], headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=HTTP_CONFIG['timeout_seconds'], headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            with self.lock:
                self.results['total_requests'] += 1
                self.results['response_times'].append(response_time)
                
                if response.status_code == expected_status:
                    self.results['successful_requests'] += 1
                    logging.info(f"✅ {method} {path} - {response.status_code} ({response_time:.0f}ms)")
                else:
                    self.results['failed_requests'] += 1
                    self.results['errors'].append({
                        'method': method,
                        'path': path,
                        'expected': expected_status,
                        'actual': response.status_code,
                        'response_time': response_time
                    })
                    logging.warning(f"❌ {method} {path} - Expected {expected_status}, got {response.status_code} ({response_time:.0f}ms)")
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            with self.lock:
                self.results['total_requests'] += 1
                self.results['failed_requests'] += 1
                self.results['errors'].append({
                    'method': method,
                    'path': path,
                    'error': str(e),
                    'response_time': response_time
                })
            logging.error(f"💥 {method} {path} - Error: {e}")

    def log_system_metrics(self, prefix=""):
        """Log system resource usage"""
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        logging.info(f"{prefix}CPU: {cpu}%, Memory: {mem.percent}% used ({mem.used // (1024*1024)}MB/{mem.total // (1024*1024)}MB)")

    def run_stress_test(self):
        """Run the API stress test"""
        endpoints = API_CONFIG['endpoints']
        concurrent_users = API_CONFIG['concurrent_users']
        requests_per_second = API_CONFIG['requests_per_second']
        duration_minutes = API_CONFIG['test_duration_minutes']
        
        logging.info(f"🚀 Starting API stress test")
        logging.info(f"   Base URL: {self.base_url}")
        logging.info(f"   Endpoints: {len(endpoints)}")
        logging.info(f"   Concurrent users: {concurrent_users}")
        logging.info(f"   Target RPS: {requests_per_second}")
        logging.info(f"   Duration: {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        self.log_system_metrics("Before test: ")
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            while time.time() < end_time:
                # Submit requests to maintain target RPS
                for _ in range(requests_per_second):
                    endpoint = random.choice(endpoints)
                    executor.submit(self.make_request, endpoint)
                
                time.sleep(1)  # Wait 1 second before next batch
        
        self.log_system_metrics("After test: ")
        
        # Calculate and log results
        self.log_results()

    def log_results(self):
        """Log test results and check success criteria"""
        total = self.results['total_requests']
        successful = self.results['successful_requests']
        failed = self.results['failed_requests']
        
        if total == 0:
            logging.error("No requests were made!")
            return
            
        success_rate = (successful / total) * 100
        error_rate = (failed / total) * 100
        avg_response_time = sum(self.results['response_times']) / len(self.results['response_times']) if self.results['response_times'] else 0
        max_response_time = max(self.results['response_times']) if self.results['response_times'] else 0
        
        logging.info(f"📊 Test Results:")
        logging.info(f"   Total requests: {total}")
        logging.info(f"   Successful: {successful} ({success_rate:.1f}%)")
        logging.info(f"   Failed: {failed} ({error_rate:.1f}%)")
        logging.info(f"   Avg response time: {avg_response_time:.0f}ms")
        logging.info(f"   Max response time: {max_response_time:.0f}ms")
        
        # Check success criteria
        criteria_met = True
        if success_rate < API_SUCCESS_CRITERIA['success_rate_percent']:
            logging.error(f"❌ Success rate {success_rate:.1f}% below threshold {API_SUCCESS_CRITERIA['success_rate_percent']}%")
            criteria_met = False
        else:
            logging.info(f"✅ Success rate {success_rate:.1f}% meets threshold {API_SUCCESS_CRITERIA['success_rate_percent']}%")
            
        if avg_response_time > API_SUCCESS_CRITERIA['response_time_ms']:
            logging.error(f"❌ Avg response time {avg_response_time:.0f}ms above threshold {API_SUCCESS_CRITERIA['response_time_ms']}ms")
            criteria_met = False
        else:
            logging.info(f"✅ Avg response time {avg_response_time:.0f}ms meets threshold {API_SUCCESS_CRITERIA['response_time_ms']}ms")
            
        if error_rate > API_SUCCESS_CRITERIA['max_error_rate_percent']:
            logging.error(f"❌ Error rate {error_rate:.1f}% above threshold {API_SUCCESS_CRITERIA['max_error_rate_percent']}%")
            criteria_met = False
        else:
            logging.info(f"✅ Error rate {error_rate:.1f}% meets threshold {API_SUCCESS_CRITERIA['max_error_rate_percent']}%")
        
        if criteria_met:
            logging.info("🎉 All success criteria met!")
        else:
            logging.error("💥 Some success criteria failed!")
            
        # Log detailed errors if any
        if self.results['errors']:
            logging.info(f"📋 Error Details (showing first 10):")
            for error in self.results['errors'][:10]:
                logging.info(f"   {error}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_stress_test() 