# api_cleanup.py
import requests
import logging
from api_config import API_CONFIG, HTTP_CONFIG, LOGGING_CONFIG

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

class APICleanup:
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.auth_type = API_CONFIG['auth_type']
        self.session = requests.Session()
        self.setup_auth()

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

    def cleanup_test_data(self):
        """Clean up test data created during API testing"""
        logging.info("🧹 Starting API cleanup...")
        
        # This is a general cleanup approach that works with any API
        # It looks for common test data patterns and cleans them up
        endpoints = API_CONFIG['endpoints']
        cleaned_count = 0
        
        for endpoint in endpoints:
            if endpoint['method'] in ['POST', 'PUT']:
                # For POST/PUT endpoints, we might have created test data
                path = endpoint['path']
                
                # General cleanup logic - works with any endpoint
                cleaned_count += self.cleanup_test_resources(path)
        
        if cleaned_count > 0:
            logging.info(f"✅ Cleaned up {cleaned_count} test resources")
        else:
            logging.info("ℹ️  No test data found to clean up")
        
        logging.info("✅ API cleanup completed")

    def cleanup_test_resources(self, base_path):
        """General cleanup for any resource type"""
        try:
            # Try to get all resources from the base endpoint
            url = f"{self.base_url}{base_path}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                resources = response.json()
                deleted_count = 0
                
                for resource in resources:
                    # Look for common test data indicators
                    if self.is_test_data(resource):
                        resource_id = resource.get('id')
                        if resource_id:
                            delete_url = f"{self.base_url}{base_path}/{resource_id}"
                            delete_response = self.session.delete(delete_url)
                            if delete_response.status_code in [200, 204]:
                                deleted_count += 1
                                logging.info(f"🗑️  Deleted test resource: {resource.get('name', resource.get('id', 'unknown'))}")
                
                return deleted_count
        except Exception as e:
            logging.error(f"Error cleaning up test resources for {base_path}: {e}")
        
        return 0

    def is_test_data(self, resource):
        """Check if a resource is test data based on common patterns"""
        # Look for common test data indicators
        test_indicators = [
            'test' in str(resource.get('name', '')).lower(),
            'test' in str(resource.get('email', '')).lower(),
            'test' in str(resource.get('description', '')).lower(),
            resource.get('metadata', {}).get('test_data') == True,
            'Test Item' in str(resource.get('name', '')),
            'test@example.com' in str(resource.get('email', '')),
        ]
        
        return any(test_indicators)

if __name__ == "__main__":
    cleanup = APICleanup()
    cleanup.cleanup_test_data() 