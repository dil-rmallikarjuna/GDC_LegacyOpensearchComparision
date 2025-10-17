
// Search terms extracted from Excel file
// Generated automatically - do not edit manually

export const searchTerms = [
  "Narendra Modi",
  "Industrial & Commercial Bank of China",
  "Credit Suisse Group AG",
  "David Thomas Smith",
  "Apple Inc",
  "Microsoft Corporation",
  "Google LLC",
  "Amazon.com Inc",
  "Tesla Inc",
  "Meta Platforms Inc"
];

export const getRandomSearchTerm = () => {
    const randomIndex = Math.floor(Math.random() * searchTerms.length);
    return searchTerms[randomIndex];
};

export const getSearchTermByIndex = (index) => {
    return searchTerms[index % searchTerms.length];
};

export const getTotalSearchTerms = () => {
    return searchTerms.length;
};
