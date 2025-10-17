/**
 * K6 Endurance Test for OpenSearch API
 * Tests system stability under sustained load over extended period
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const searchLatency = new Trend('search_latency');
const totalRequests = new Counter('total_requests');
const successfulRequests = new Counter('successful_requests');
const failedRequests = new Counter('failed_requests');

/**
 * Main test function - executed by each VU
 */
export default function() {
    // Generate search term
    const searchTerm = getRandomSearchTerm();
    
    // Prepare API request
    const url = `${config.baseUrl}${API_CONFIG.endpoints.search}`;
    const headers = {
        ...API_CONFIG.headers,
        'Authorization': `Bearer ${config.apiKey}`
    };
    
    const payload = {
        query: searchTerm,
        schemas: API_CONFIG.schemas,
        limit: API_CONFIG.defaultLimit,
        search_types: API_CONFIG.searchTypes
    };
    
    // Make API request
    const response = http.post(url, JSON.stringify(payload), { headers });
    
    // Update counters
    totalRequests.add(1);
    if (response.status === 200) {
        successfulRequests.add(1);
    } else {
        failedRequests.add(1);
    }
    
    // Performance checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 5s': (r) => r.timings.duration < 5000,
        'response has body': (r) => r.body && r.body.length > 0,
        'response is JSON': (r) => {
            try {
                JSON.parse(r.body);
                return true;
            } catch (e) {
                return false;
            }
        }
    });
    
    // Update custom metrics
    errorRate.add(response.status !== 200);
    searchLatency.add(response.timings.duration);
    
    // Log every request with response code
    console.log(`Search: "${searchTerm}" | Status: ${response.status} | Time: ${response.timings.duration}ms`);
    
    // Log every 100th request for monitoring
    if (totalRequests.count % 100 === 0) {
        console.log(`📊 Endurance Test Progress: ${totalRequests.count} requests completed`);
    }
    
    // Variable think time (0.5-3 seconds)
    sleep(Math.random() * 2.5 + 0.5);
}

/**
 * Setup function - runs once before all VUs
 */
export function setup() {
    console.log('🚀 Starting OpenSearch API Endurance Test');
    console.log(`📊 Environment: ${config.baseUrl}`);
    console.log(`👥 VUs: ${__ENV.VUS || 10}`);
    console.log(`⏱️  Duration: ${__ENV.DURATION || '30m'}`);
    console.log('🔄 This test will run for an extended period to check system stability');
    
    return { startTime: Date.now() };
}

/**
 * Teardown function - runs once after all VUs
 */
export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    const successRate = (successfulRequests.count / totalRequests.count) * 100;
    
    console.log('🏁 Endurance Test Completed');
    console.log(`⏱️  Total Duration: ${(duration / 60).toFixed(2)} minutes`);
    console.log(`📊 Total Requests: ${totalRequests.count}`);
    console.log(`✅ Successful Requests: ${successfulRequests.count}`);
    console.log(`❌ Failed Requests: ${failedRequests.count}`);
    console.log(`📈 Success Rate: ${successRate.toFixed(2)}%`);
}
