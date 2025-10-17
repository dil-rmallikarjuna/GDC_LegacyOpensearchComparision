# K6 Performance Testing - Excel Search Terms Integration

## ✅ All Test Scenarios Updated

All K6 performance test scenarios now use **only the search terms from your Excel file** instead of random generated names.

### Updated Test Scenarios:

1. **✅ opensearch-api-test.js** - Main performance test
2. **✅ example-test.js** - Simple example test  
3. **✅ stress-test.js** - Stress testing
4. **✅ spike-test.js** - Spike testing
5. **✅ load-test.js** - Load testing
6. **✅ volume-test.js** - Volume testing
7. **✅ endurance-test.js** - Endurance testing

### Search Terms Used (from Excel file):

- Narendra Modi
- Industrial & Commercial Bank of China
- Credit Suisse Group AG
- David Thomas Smith
- Apple Inc
- Microsoft Corporation
- Google LLC
- Amazon.com Inc
- Tesla Inc
- Meta Platforms Inc

### How It Works:

1. **All test scenarios** now import `getRandomSearchTerm()` from `../data/search-terms.js`
2. **Each test iteration** randomly selects one of the 10 Excel search terms
3. **Terms are reused** throughout the test duration (no new random generation)
4. **Consistent testing** across all performance test types

### Benefits:

- ✅ **Realistic testing** with actual search terms from your data
- ✅ **Consistent results** across all test scenarios
- ✅ **No random name generation** - only your Excel terms
- ✅ **Reusable terms** - same terms used repeatedly as requested
- ✅ **Easy to update** - just update the Excel file and re-run the extraction script

### To Update Search Terms:

1. Update your Excel file: `Test terms copy.xlsx`
2. Run: `python3 data/extract_search_terms.py`
3. All K6 tests will automatically use the new terms

### Test Commands:

```bash
# Run all tests with Excel search terms
./run-tests.sh all

# Run specific test types
./run-tests.sh smoke
./run-tests.sh load
./run-tests.sh stress
./run-tests.sh spike
./run-tests.sh volume
./run-tests.sh endurance
```

All performance tests now use **only your Excel search terms** - no random generation! 🚀
