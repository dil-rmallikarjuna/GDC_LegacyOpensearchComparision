# K6 Performance Testing Framework

A comprehensive performance testing framework for OpenSearch API using K6.

## 🚀 Features

- **Multiple Test Scenarios**: Smoke, Load, Stress, Spike, Volume, and Endurance tests
- **Realistic Test Data**: Random name generators for persons and entities
- **Advanced Metrics**: Custom metrics for performance analysis
- **Flexible Configuration**: Environment-based configuration with multiple scenarios
- **Comprehensive Reporting**: Detailed performance reports with thresholds
- **User Behavior Simulation**: Realistic user behavior patterns

## 📁 Project Structure

```
k6-tests/
├── config/
│   └── k6-config.js          # Centralized configuration
├── data/
│   └── name-generators.js    # Random data generators
├── scenarios/
│   ├── opensearch-api-test.js    # Main API test
│   ├── load-test.js              # Load testing
│   ├── stress-test.js            # Stress testing
│   ├── spike-test.js             # Spike testing
│   ├── volume-test.js            # Volume testing
│   └── endurance-test.js         # Endurance testing
├── utils/
│   └── test-helpers.js       # Utility functions
├── run-tests.sh              # Test runner script
└── README.md                 # This file
```

## 🛠️ Installation

### Prerequisites

1. **Install K6**:
   ```bash
   # macOS
   brew install k6
   
   # Linux
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
   echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update
   sudo apt-get install k6
   
   # Windows
   choco install k6
   ```

2. **Verify Installation**:
   ```bash
   k6 version
   ```

## 🚀 Quick Start

### Basic Usage

```bash
# Run a quick smoke test
./run-tests.sh smoke

# Run load testing
./run-tests.sh load

# Run all tests
./run-tests.sh all
```

### Advanced Usage

```bash
# Custom VUs and duration
./run-tests.sh -v 50 -d 10m load

# Different environment
./run-tests.sh -e prod stress

# Custom output directory
./run-tests.sh -o ./my-results all
```

## 📊 Test Scenarios

### 1. Smoke Test
- **Purpose**: Quick validation that the API is working
- **VUs**: 2-5
- **Duration**: 1-2 minutes
- **Use Case**: CI/CD pipelines, quick health checks

### 2. Load Test
- **Purpose**: Normal production load simulation
- **VUs**: 10-50
- **Duration**: 5-10 minutes
- **Use Case**: Performance baseline, capacity planning

### 3. Stress Test
- **Purpose**: System behavior under high load
- **VUs**: 50-200
- **Duration**: 10-15 minutes
- **Use Case**: Breaking point identification, scalability testing

### 4. Spike Test
- **Purpose**: Sudden traffic spikes
- **VUs**: 100-150
- **Duration**: 5-10 minutes
- **Use Case**: Traffic surge handling, auto-scaling validation

### 5. Volume Test
- **Purpose**: High data volume scenarios
- **VUs**: 30-50
- **Duration**: 10 minutes
- **Use Case**: Large result sets, data processing limits

### 6. Endurance Test
- **Purpose**: Long-term stability testing
- **VUs**: 10-20
- **Duration**: 30+ minutes
- **Use Case**: Memory leaks, resource degradation

## ⚙️ Configuration

### Environment Configuration

Edit `config/k6-config.js` to configure different environments:

```javascript
export const ENVIRONMENTS = {
    dev: {
        baseUrl: 'https://dev-api.example.com',
        apiKey: 'your-dev-api-key',
        timeout: '30s'
    },
    staging: {
        baseUrl: 'https://staging-api.example.com',
        apiKey: 'your-staging-api-key',
        timeout: '30s'
    },
    prod: {
        baseUrl: 'https://prod-api.example.com',
        apiKey: 'your-prod-api-key',
        timeout: '30s'
    }
};
```

### Test Scenarios

Configure test scenarios in `config/k6-config.js`:

```javascript
export const SCENARIOS = {
    smoke: {
        executor: 'constant-vus',
        vus: 5,
        duration: '2m'
    },
    load: {
        executor: 'ramping-vus',
        startVUs: 10,
        stages: [
            { duration: '2m', target: 20 },
            { duration: '5m', target: 20 },
            { duration: '2m', target: 0 }
        ]
    }
};
```

### Performance Thresholds

Set performance thresholds:

```javascript
export const THRESHOLDS = {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
    http_reqs: ['rate>10'],            // At least 10 requests per second
    checks: ['rate>0.9']               // 90% of checks should pass
};
```

## 📈 Metrics and Reporting

### Built-in Metrics

- **HTTP Request Duration**: Response time metrics
- **HTTP Request Rate**: Requests per second
- **HTTP Request Failed**: Error rate
- **Checks**: Custom check pass rate

### Custom Metrics

- **Error Rate**: Custom error rate tracking
- **Search Latency**: Search-specific latency tracking
- **Response Size**: Response payload size tracking
- **High Volume Latency**: Specialized metrics for high-volume scenarios

### Performance Analysis

The framework includes advanced performance analysis:

```javascript
// Percentile analysis
p50ResponseTime: 150,
p95ResponseTime: 800,
p99ResponseTime: 1200,

// Performance thresholds
meetsMaxResponseTime: true,
meetsErrorRate: true,
meetsP95: true,
overallPass: true
```

## 🎯 Test Data Generation

### Random Name Generation

The framework includes comprehensive name generators:

```javascript
// Generate random person
const person = generateRandomPerson();
// { firstName: 'John', lastName: 'Smith', fullName: 'John Smith', type: 'P' }

// Generate random entity
const entity = generateRandomEntity();
// { name: 'Global Solutions Inc', type: 'E' }

// Generate weighted random data (more realistic)
const weightedPerson = generateWeightedRandomPerson();
```

### User Behavior Simulation

Simulate realistic user behavior patterns:

- **Quick Search**: Fast searches with short think time
- **Thorough Search**: Slower searches with longer think time
- **Exploratory**: Multiple related searches
- **Casual Browsing**: Random searches with variable timing

## 🔧 Customization

### Adding New Test Scenarios

1. Create a new test file in `scenarios/`
2. Import required modules and configuration
3. Implement the test logic
4. Add to the test runner script

### Custom Metrics

Add custom metrics to track specific performance aspects:

```javascript
import { Rate, Trend, Counter } from 'k6/metrics';

const customErrorRate = new Rate('custom_error_rate');
const customLatency = new Trend('custom_latency');
const customCounter = new Counter('custom_counter');
```

### Custom Data Generators

Extend the data generators for specific test requirements:

```javascript
export function generateCustomSearchTerm() {
    // Custom logic for generating test data
    return {
        query: 'custom search term',
        type: 'E',
        customField: 'custom value'
    };
}
```

## 📊 Running Tests

### Command Line Options

```bash
./run-tests.sh [OPTIONS] [TEST_TYPE]

Options:
  -e, --env ENV        Environment (dev|staging|prod) [default: dev]
  -v, --vus VUS        Virtual Users [default: 10]
  -d, --duration TIME  Test duration [default: 1m]
  -o, --output DIR     Output directory [default: ./results]
  -h, --help           Show help

Test Types:
  smoke               Quick smoke test
  load                Load testing
  stress              Stress testing
  spike               Spike testing
  volume              Volume testing
  endurance           Endurance testing
  all                 Run all tests
```

### Examples

```bash
# Quick smoke test
./run-tests.sh smoke

# Load test with 50 VUs for 10 minutes
./run-tests.sh -v 50 -d 10m load

# Stress test against production
./run-tests.sh -e prod stress

# All tests with custom output directory
./run-tests.sh -o ./performance-results all
```

## 📋 Best Practices

### 1. Test Planning
- Start with smoke tests for basic validation
- Use load tests for baseline performance
- Run stress tests to find breaking points
- Use endurance tests for stability validation

### 2. Environment Management
- Use separate environments for different test types
- Keep production testing minimal and controlled
- Use staging environments for comprehensive testing

### 3. Data Management
- Use realistic test data that matches production patterns
- Avoid hardcoded test data that might not exist
- Use weighted random data for more realistic scenarios

### 4. Performance Monitoring
- Set appropriate thresholds based on business requirements
- Monitor system resources during tests
- Use multiple metrics for comprehensive analysis

### 5. Test Execution
- Run tests during off-peak hours for production
- Use appropriate VU counts for your infrastructure
- Monitor test execution and stop if issues arise

## 🐛 Troubleshooting

### Common Issues

1. **K6 Not Found**
   ```bash
   # Install K6
   brew install k6  # macOS
   # or
   sudo apt-get install k6  # Linux
   ```

2. **API Connection Issues**
   - Check API URL and authentication
   - Verify network connectivity
   - Check API rate limits

3. **High Error Rates**
   - Reduce VU count
   - Increase think time
   - Check API capacity

4. **Memory Issues**
   - Reduce test duration
   - Lower VU count
   - Check system resources

### Debug Mode

Run tests with debug output:

```bash
k6 run --verbose scenarios/opensearch-api-test.js
```

## 📚 Additional Resources

- [K6 Documentation](https://k6.io/docs/)
- [K6 Examples](https://github.com/grafana/k6/tree/master/examples)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/)
- [K6 Cloud](https://k6.io/cloud/) for distributed testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your test scenarios or improvements
4. Test your changes
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
