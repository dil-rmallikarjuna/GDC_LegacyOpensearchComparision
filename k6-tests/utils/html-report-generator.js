#!/usr/bin/env node

/**
 * K6 HTML Report Generator
 * Converts K6 JSON output to beautiful HTML reports
 */

const fs = require('fs');
const path = require('path');

class K6HTMLReportGenerator {
    constructor() {
        this.metrics = {};
        this.summary = {};
    }

    parseJSONFile(filePath) {
        try {
            const data = fs.readFileSync(filePath, 'utf8');
            const lines = data.trim().split('\n');
            
            for (const line of lines) {
                if (line.trim()) {
                    const parsed = JSON.parse(line);
                    this.processMetric(parsed);
                }
            }
        } catch (error) {
            console.error(`Error parsing JSON file: ${error.message}`);
            process.exit(1);
        }
    }

    processMetric(metric) {
        if (metric.type === 'Metric') {
            this.metrics[metric.metric] = metric.data;
        } else if (metric.type === 'Point') {
            if (!this.metrics[metric.metric]) {
                this.metrics[metric.metric] = { values: [] };
            }
            if (!this.metrics[metric.metric].values) {
                this.metrics[metric.metric].values = [];
            }
            // Prevent infinite recursion by limiting array size
            if (this.metrics[metric.metric].values.length < 10000) {
                this.metrics[metric.metric].values.push(metric.data);
            }
        }
    }

    calculateSummary() {
        const summary = {};
        
        // Calculate summary statistics
        for (const [metricName, metricData] of Object.entries(this.metrics)) {
            if (metricData && metricData.values && Array.isArray(metricData.values) && metricData.values.length > 0) {
                const values = metricData.values.map(v => v.value).filter(v => typeof v === 'number' && !isNaN(v));
                if (values.length > 0) {
                    try {
                        summary[metricName] = {
                            count: values.length,
                            min: Math.min(...values),
                            max: Math.max(...values),
                            avg: values.reduce((a, b) => a + b, 0) / values.length,
                            p90: this.percentile(values, 90),
                            p95: this.percentile(values, 95),
                            p99: this.percentile(values, 99)
                        };
                    } catch (error) {
                        console.warn(`Error calculating summary for ${metricName}:`, error.message);
                        summary[metricName] = {
                            count: values.length,
                            min: 0,
                            max: 0,
                            avg: 0,
                            p90: 0,
                            p95: 0,
                            p99: 0
                        };
                    }
                }
            }
        }
        
        this.summary = summary;
    }

    percentile(arr, p) {
        const sorted = arr.slice().sort((a, b) => a - b);
        const index = Math.ceil((p / 100) * sorted.length) - 1;
        return sorted[index];
    }

    generateHTML() {
        const timestamp = new Date().toLocaleString();
        
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K6 Performance Test Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }
        
        .metric-card h3 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .metric-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #6c757d;
            font-weight: 500;
        }
        
        .stat-value {
            color: #495057;
            font-weight: 600;
        }
        
        .charts-section {
            margin-top: 30px;
        }
        
        .charts-section h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .chart-title {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }
        
        .status-good { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-danger { color: #dc3545; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 K6 Performance Test Report</h1>
            <p>Generated on ${timestamp}</p>
        </div>
        
        <div class="content">
            <div class="summary-grid">
                ${this.generateMetricCards()}
            </div>
            
            <div class="charts-section">
                <h2>📊 Performance Metrics</h2>
                ${this.generateCharts()}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by K6 Performance Testing Framework</p>
            <p>This report shows detailed performance metrics from your load test</p>
        </div>
    </div>
</body>
</html>`;
    }

    generateMetricCards() {
        const cards = [];
        
        // Key metrics to display
        const keyMetrics = [
            'http_reqs',
            'http_req_duration',
            'http_req_failed',
            'vus',
            'iterations'
        ];
        
        for (const metric of keyMetrics) {
            if (this.summary[metric]) {
                const data = this.summary[metric];
                cards.push(this.generateMetricCard(metric, data));
            }
        }
        
        return cards.join('');
    }

    generateMetricCard(metricName, data) {
        const title = this.getMetricTitle(metricName);
        const icon = this.getMetricIcon(metricName);
        
        return `
        <div class="metric-card">
            <h3>${icon} ${title}</h3>
            <div class="metric-stats">
                <div class="stat">
                    <span class="stat-label">Count</span>
                    <span class="stat-value">${data.count.toLocaleString()}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Average</span>
                    <span class="stat-value">${this.formatValue(metricName, data.avg)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Min</span>
                    <span class="stat-value">${this.formatValue(metricName, data.min)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Max</span>
                    <span class="stat-value">${this.formatValue(metricName, data.max)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">95th Percentile</span>
                    <span class="stat-value">${this.formatValue(metricName, data.p95)}</span>
                </div>
            </div>
        </div>`;
    }

    getMetricTitle(metricName) {
        const titles = {
            'http_reqs': 'HTTP Requests',
            'http_req_duration': 'Response Time',
            'http_req_failed': 'Failed Requests',
            'vus': 'Virtual Users',
            'iterations': 'Iterations'
        };
        return titles[metricName] || metricName;
    }

    getMetricIcon(metricName) {
        const icons = {
            'http_reqs': '🌐',
            'http_req_duration': '⏱️',
            'http_req_failed': '❌',
            'vus': '👥',
            'iterations': '🔄'
        };
        return icons[metricName] || '📊';
    }

    formatValue(metricName, value) {
        if (metricName === 'http_req_duration') {
            return `${value.toFixed(2)}ms`;
        } else if (metricName === 'http_req_failed') {
            return `${(value * 100).toFixed(2)}%`;
        } else {
            return value.toLocaleString();
        }
    }

    generateCharts() {
        return `
        <div class="chart-container">
            <div class="chart-title">📈 Performance Overview</div>
            <p>This report provides detailed insights into your application's performance under load.</p>
            <p><strong>Key Insights:</strong></p>
            <ul>
                <li>Total HTTP Requests: ${this.summary.http_reqs?.count || 'N/A'}</li>
                <li>Average Response Time: ${this.formatValue('http_req_duration', this.summary.http_req_duration?.avg || 0)}</li>
                <li>Failed Requests: ${this.formatValue('http_req_failed', this.summary.http_req_failed?.avg || 0)}</li>
                <li>Peak Virtual Users: ${this.summary.vus?.max || 'N/A'}</li>
            </ul>
        </div>`;
    }

    generateReport(jsonFilePath, outputPath) {
        console.log('📊 Parsing K6 JSON data...');
        this.parseJSONFile(jsonFilePath);
        
        console.log('📈 Calculating summary statistics...');
        this.calculateSummary();
        
        console.log('🎨 Generating HTML report...');
        const html = this.generateHTML();
        
        fs.writeFileSync(outputPath, html);
        console.log(`✅ HTML report generated: ${outputPath}`);
    }
}

// Command line usage
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.log('Usage: node html-report-generator.js <json-file> <output-html-file>');
        console.log('Example: node html-report-generator.js results/k6-test.json results/k6-report.html');
        process.exit(1);
    }
    
    const [jsonFile, htmlFile] = args;
    const generator = new K6HTMLReportGenerator();
    generator.generateReport(jsonFile, htmlFile);
}

module.exports = K6HTMLReportGenerator;
