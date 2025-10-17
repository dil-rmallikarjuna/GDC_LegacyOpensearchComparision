/**
 * K6 Volume Test for OpenSearch API
 * Tests system behavior under high data volume scenarios
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { getRandomSearchTerm } from '../data/search-terms.js';
import { config, API_CONFIG } from '../config/k6-config.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const searchLatency = new Trend('search_latency');
const highVolumeLatency = new Trend('high_volume_latency');
const totalRequests = new Counter('total_requests');
const highVolumeRequests = new Counter('high_volume_requests');

// Using search terms from Excel file

/**
 * Main test function - executed by each VU
 */
export default function() {
    // 80% normal requests, 20% high volume requests
    const isHighVolume = Math.random() < 0.2;
    
    let searchTerm;
    let limit;
    
    if (isHighVolume) {
        // High volume scenario - large limit, complex query
        searchTerm = getRandomSearchTerm();
        limit = Math.floor(Math.random() * 500) + 500; // 500-1000 limit
        highVolumeRequests.add(1);
    } else {
        // Normal volume scenario
        searchTerm = getRandomSearchTerm();
        limit = Math.floor(Math.random() * 100) + 10; // 10-110 limit
    }
    
    // Prepare API request
    const url = `${config.baseUrl}${API_CONFIG.endpoints.search}`;
    const headers = {
        ...API_CONFIG.headers,
        'Authorization': `Bearer ${config.apiKey}`
    };
    
    const payload = {
        query: searchTerm,
        schemas: API_CONFIG.schemas,
        limit: limit,
        search_types: API_CONFIG.searchTypes
    };
    
    // Make API request
    const response = http.post(url, JSON.stringify(payload), { headers });
    
    // Update counters
    totalRequests.add(1);
    
    // Performance checks
    const checksResult = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 10s': (r) => r.timings.duration < 10000,
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
    
    if (isHighVolume) {
        highVolumeLatency.add(response.timings.duration);
    }
    
    // Log high volume requests and errors
    if (isHighVolume) {
        console.log(`📊 High Volume: "${searchTerm}" | Limit: ${limit} | Time: ${response.timings.duration}ms`);
    }
    
    if (response.status !== 200) {
        console.log(`❌ Error: "${searchTerm}" | Status: ${response.status} | Time: ${response.timings.duration}ms`);
    }
    
    // Shorter think time for volume test (0.2-2 seconds)
    sleep(Math.random() * 1.8 + 0.2);
}

/**
 * Setup function - runs once before all VUs
 */
export function setup() {
    console.log('🚀 Starting OpenSearch API Volume Test');
    console.log(`📊 Environment: ${config.baseUrl}`);
    console.log(`👥 VUs: ${__ENV.VUS || 50}`);
    console.log(`⏱️  Duration: ${__ENV.DURATION || '10m'}`);
    console.log(`📊 Large Dataset: ${largeDataset.length} pre-generated search terms`);
    console.log('🔄 This test includes high volume scenarios with large result sets');
    
    return { startTime: Date.now() };
}

/**
 * Teardown function - runs once after all VUs
 */
export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    
    console.log('🏁 Volume Test Completed');
    console.log(`⏱️  Total Duration: ${(duration / 60).toFixed(2)} minutes`);
    console.log(`📊 Total Requests: ${totalRequests.count}`);
    console.log(`📊 High Volume Requests: ${highVolumeRequests.count}`);
    console.log(`📈 High Volume Percentage: ${((highVolumeRequests.count / totalRequests.count) * 100).toFixed(2)}%`);
}
