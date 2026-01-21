# api_config.py - Configuration for API Stress Testing

# API Testing Configuration
API_CONFIG = {
    'base_url': 'https://jsonplaceholder.typicode.com',  # Free public API for testing
    'auth_type': 'none',  # 'bearer', 'api_key', 'basic', 'none'
    'auth_token': 'your_token_here',
    'api_key': 'your_api_key_here',
    'username': 'your_username',
    'password': 'your_password',
    'concurrent_users': 5,  # Start with low numbers for testing
    'requests_per_second': 10,  # Start with low numbers for testing
    'test_duration_minutes': 1,  # Short test duration
    'endpoints': [
        # Example endpoints - replace with your actual API endpoints
        {'method': 'GET', 'path': '/posts', 'expected_status': 200},
        {'method': 'GET', 'path': '/posts/1', 'expected_status': 200},
        {'method': 'GET', 'path': '/users', 'expected_status': 200},
        {'method': 'GET', 'path': '/users/1', 'expected_status': 200},
        {'method': 'POST', 'path': '/posts', 'expected_status': 201},
        {'method': 'POST', 'path': '/users', 'expected_status': 201},
        # Add your actual endpoints here:
        # {'method': 'GET', 'path': '/your-endpoint', 'expected_status': 200},
        # {'method': 'POST', 'path': '/your-endpoint', 'expected_status': 201},
    ],
    # Optional: Custom dummy data templates for specific endpoints
    'dummy_data_templates': {
        # '/users': {'name': 'string', 'email': 'email', 'age': 'integer'},
        # '/products': {'name': 'string', 'price': 'float', 'category': 'string'},
        # Add custom templates for your endpoints if needed
    }
}

# API Testing Success Criteria
API_SUCCESS_CRITERIA = {
    'response_time_ms': 2000,  # 2 seconds max
    'success_rate_percent': 99,  # 99% success rate
    'max_error_rate_percent': 1   # 1% max error rate
}

# API Testing Control Flags
RUN_API_STRESS_TEST = True       # Set True to run API stress test
RUN_API_CLEANUP = False          # Set True to clean up API test data (if applicable)

# Test Scenarios (optional - for different load patterns)
TEST_SCENARIOS = {
    'light_load': {
        'concurrent_users': 5,
        'requests_per_second': 10,
        'test_duration_minutes': 1
    },
    'medium_load': {
        'concurrent_users': 25,
        'requests_per_second': 50,
        'test_duration_minutes': 5
    },
    'heavy_load': {
        'concurrent_users': 100,
        'requests_per_second': 200,
        'test_duration_minutes': 10
    }
}

# HTTP Request Configuration
HTTP_CONFIG = {
    'timeout_seconds': 10,
    'max_retries': 3,
    'retry_delay_seconds': 1,
    'user_agent': 'Stress-Test-Tool/1.0',
    'headers': {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s [%(levelname)s] %(message)s',
    'log_to_file': False,
    'log_file': 'api_stress_test.log'
}

if __name__ == "__main__":
    print("API Configuration loaded successfully!")
    print(f"Base URL: {API_CONFIG['base_url']}")
    print(f"Endpoints: {len(API_CONFIG['endpoints'])}")
    print(f"Concurrent users: {API_CONFIG['concurrent_users']}")
    print(f"Requests per second: {API_CONFIG['requests_per_second']}")
    print(f"Test duration: {API_CONFIG['test_duration_minutes']} minutes") 