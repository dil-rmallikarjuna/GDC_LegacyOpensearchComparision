/**
 * K6 Performance Testing Configuration
 * Centralized configuration for all K6 performance tests
 */

// Test Environment Configuration
export const ENVIRONMENTS = {
    dev: {
        baseUrl: 'https://knhmspdzmf.execute-api.us-west-2.amazonaws.com/dev',
        apiKey: '',
        timeout: '30s'
    },
    staging: {
        baseUrl: 'https://staging-api.example.com',
        apiKey: __ENV.STAGING_API_KEY || 'your-staging-api-key',
        timeout: '30s'
    },
    prod: {
        baseUrl: 'https://prod-api.example.com',
        apiKey: __ENV.PROD_API_KEY || 'your-prod-api-key',
        timeout: '30s'
    }
};

// Performance Test Scenarios
export const SCENARIOS = {
    // Light load testing
    smoke: {
        executor: 'constant-vus',
        vus: 2,
        duration: '2m',
        tags: { test_type: 'smoke' }
    },
    
    // Average load testing
    load: {
        executor: 'ramping-vus',
        startVUs: 10,
        stages: [
            { duration: '2m', target: 20 },
            { duration: '5m', target: 20 },
            { duration: '2m', target: 0 }
        ],
        tags: { test_type: 'load' }
    },
    
    // High load testing
    stress: {
        executor: 'ramping-vus',
        startVUs: 10,
        stages: [
            { duration: '2m', target: 50 },
            { duration: '5m', target: 50 },
            { duration: '2m', target: 100 },
            { duration: '5m', target: 100 },
            { duration: '2m', target: 0 }
        ],
        tags: { test_type: 'stress' }
    },
    
    // Spike testing
    spike: {
        executor: 'ramping-vus',
        startVUs: 10,
        stages: [
            { duration: '1m', target: 20 },
            { duration: '30s', target: 100 },
            { duration: '1m', target: 20 },
            { duration: '2m', target: 0 }
        ],
        tags: { test_type: 'spike' }
    },
    
    // Volume testing
    volume: {
        executor: 'constant-vus',
        vus: 100,
        duration: '10m',
        tags: { test_type: 'volume' }
    }
};

// API Configuration
export const API_CONFIG = {
    endpoints: {
        search: '/search',
        health: '/health'
    },
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    schemas: ['col', 'rights', 'mex', 'watch', 'soe', 'pep', 'sanction', 'icij'],
    searchTypes: ['keyword', 'phonetic', 'similarity'],
    defaultLimit: 100
};

// Thresholds for performance validation
export const THRESHOLDS = {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
    http_reqs: ['rate>10'],            // At least 10 requests per second
    checks: ['rate>0.9']               // 90% of checks should pass
};

// Test Data Configuration
export const DATA_CONFIG = {
    // Random name generators
    nameGenerators: {
        person: ['firstName', 'lastName', 'fullName'],
        entity: ['companyName', 'organizationName', 'entityName']
    },
    
    // Test data sources
    dataSources: {
        random: 'Generate random names',
        predefined: 'Use predefined test data',
        csv: 'Load from CSV file'
    }
};

// Environment selection
export const ENV = __ENV.ENV || 'dev';
export const config = ENVIRONMENTS[ENV];

// Scenario selection
export const SCENARIO = __ENV.SCENARIO || 'load';
export const scenario = SCENARIOS[SCENARIO];

// Export K6 options
export const options = {
    stages: scenario.stages || [{ duration: '1m', target: scenario.vus || 10 }],
    vus: scenario.vus || 10,
    duration: scenario.duration || '1m',
    thresholds: THRESHOLDS,
    tags: scenario.tags || {}
};
