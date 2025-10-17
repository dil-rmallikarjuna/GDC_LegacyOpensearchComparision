/**
 * Random Name Generators for K6 Performance Testing
 * Generates realistic test data for OpenSearch API testing
 */

// First names for person testing
const FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica',
    'William', 'Ashley', 'James', 'Amanda', 'Christopher', 'Jennifer', 'Daniel',
    'Lisa', 'Matthew', 'Nancy', 'Anthony', 'Karen', 'Mark', 'Helen', 'Donald',
    'Sandra', 'Steven', 'Donna', 'Paul', 'Carol', 'Andrew', 'Ruth', 'Joshua',
    'Sharon', 'Kenneth', 'Michelle', 'Kevin', 'Laura', 'Brian', 'Sarah',
    'George', 'Kimberly', 'Timothy', 'Deborah', 'Ronald', 'Dorothy', 'Jason',
    'Lisa', 'Edward', 'Nancy', 'Jeffrey', 'Karen', 'Ryan', 'Betty', 'Jacob',
    'Helen', 'Gary', 'Sandra', 'Nicholas', 'Donna', 'Eric', 'Carol', 'Jonathan',
    'Ruth', 'Stephen', 'Sharon', 'Larry', 'Michelle', 'Justin', 'Laura',
    'Scott', 'Sarah', 'Brandon', 'Kimberly', 'Benjamin', 'Deborah', 'Samuel',
    'Dorothy', 'Gregory', 'Lisa', 'Alexander', 'Nancy', 'Patrick', 'Karen',
    'Jack', 'Betty', 'Dennis', 'Helen', 'Jerry', 'Sandra', 'Tyler', 'Donna',
    'Aaron', 'Carol', 'Jose', 'Ruth', 'Henry', 'Sharon', 'Adam', 'Michelle',
    'Douglas', 'Laura', 'Nathan', 'Sarah', 'Peter', 'Kimberly', 'Zachary',
    'Deborah', 'Kyle', 'Dorothy', 'Noah', 'Lisa', 'Alan', 'Nancy', 'Jeremy',
    'Karen', 'Kevin', 'Betty', 'Brian', 'Helen', 'Jacob', 'Sandra', 'Gary',
    'Donna', 'Timothy', 'Carol', 'Jose', 'Ruth', 'Jeffrey', 'Sharon', 'Ryan',
    'Michelle', 'Jacob', 'Laura', 'Gary', 'Sarah', 'Nicholas', 'Kimberly',
    'Eric', 'Deborah', 'Jonathan', 'Dorothy', 'Stephen', 'Lisa', 'Larry',
    'Nancy', 'Justin', 'Karen', 'Scott', 'Betty', 'Brandon', 'Helen', 'Benjamin',
    'Sandra', 'Samuel', 'Donna', 'Gregory', 'Carol', 'Alexander', 'Ruth',
    'Patrick', 'Sharon', 'Jack', 'Michelle', 'Dennis', 'Laura', 'Jerry', 'Sarah',
    'Tyler', 'Kimberly', 'Aaron', 'Deborah', 'Jose', 'Dorothy', 'Henry', 'Lisa',
    'Adam', 'Nancy', 'Douglas', 'Karen', 'Nathan', 'Betty', 'Peter', 'Helen',
    'Zachary', 'Sandra', 'Kyle', 'Donna', 'Noah', 'Carol', 'Alan', 'Ruth',
    'Jeremy', 'Sharon', 'Kevin', 'Michelle', 'Brian', 'Laura', 'Jacob', 'Sarah'
];

// Last names for person testing
const LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
    'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell',
    'Mitchell', 'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner',
    'Diaz', 'Parker', 'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris',
    'Morales', 'Murphy', 'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper',
    'Peterson', 'Bailey', 'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox',
    'Ward', 'Richardson', 'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett',
    'Gray', 'Mendoza', 'Ruiz', 'Hughes', 'Price', 'Alvarez', 'Castillo', 'Sanders',
    'Patel', 'Myers', 'Long', 'Ross', 'Foster', 'Jimenez', 'Powell', 'Jenkins',
    'Perry', 'Russell', 'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson',
    'Barnes', 'Gonzales', 'Fisher', 'Vasquez', 'Simmons', 'Romero', 'Jordan',
    'Patterson', 'Alexander', 'Hamilton', 'Graham', 'Reynolds', 'Griffin', 'Wallace',
    'Moreno', 'West', 'Cole', 'Hayes', 'Bryant', 'Herrera', 'Gibson', 'Ellis',
    'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray', 'Ford', 'Castro', 'Marshall',
    'Owen', 'Harrison', 'Fernandez', 'McDonald', 'Woods', 'Washington', 'Kennedy',
    'Wells', 'Vargas', 'Henry', 'Chen', 'Freeman', 'Webb', 'Tucker', 'Guzman',
    'Burns', 'Crawford', 'Olson', 'Simpson', 'Porter', 'Hunter', 'Gordon', 'Mendez',
    'Silva', 'Shaw', 'Snyder', 'Mason', 'Dixon', 'Munoz', 'Hunt', 'Hicks',
    'Holmes', 'Palmer', 'Wagner', 'Black', 'Robertson', 'Boyd', 'Rose', 'Stone',
    'Salazar', 'Fox', 'Warren', 'Mills', 'Meyer', 'Rice', 'Schmidt', 'Garza',
    'Daniels', 'Ferguson', 'Nichols', 'Stephens', 'Soto', 'Weaver', 'Ryan', 'Gardner',
    'Payne', 'Grant', 'Dunn', 'Kelley', 'Spencer', 'Hawkins', 'Arnold', 'Pierce',
    'Vazquez', 'Hansen', 'Peters', 'Santos', 'Hart', 'Bradley', 'Knight', 'Elliott',
    'Cunningham', 'Knight', 'Bradley', 'Willis', 'Ray', 'Watkins', 'Olson', 'Carroll',
    'Duncan', 'Snyder', 'Hart', 'Cunningham', 'Bradley', 'Lane', 'Andrews', 'Ruiz',
    'Harper', 'Fox', 'Riley', 'Armstrong', 'Carpenter', 'Weaver', 'Greene', 'Lawrence',
    'Elliott', 'Chavez', 'Sims', 'Austin', 'Peters', 'Kelley', 'Franklin', 'Lawson'
];

// Company/Entity names for entity testing
const COMPANY_NAMES = [
    'Global Solutions Inc', 'Tech Innovations Ltd', 'Digital Dynamics Corp', 'Future Systems LLC',
    'Advanced Technologies', 'Smart Solutions Group', 'Innovation Partners', 'NextGen Systems',
    'Cyber Security Corp', 'Data Analytics Ltd', 'Cloud Computing Inc', 'AI Solutions Group',
    'Blockchain Technologies', 'Quantum Computing Corp', 'Machine Learning Ltd', 'IoT Solutions Inc',
    'Robotics Systems', 'Automation Corp', 'Software Development Ltd', 'IT Consulting Group',
    'Network Solutions Inc', 'Database Systems Corp', 'Web Development Ltd', 'Mobile Apps Corp',
    'E-commerce Solutions', 'Digital Marketing Inc', 'Social Media Corp', 'Content Management Ltd',
    'Video Production Inc', 'Media Solutions Corp', 'Publishing House Ltd', 'News Corporation',
    'Broadcasting Systems', 'Entertainment Corp', 'Gaming Technologies', 'Virtual Reality Inc',
    'Augmented Reality Corp', 'Mixed Reality Ltd', 'Immersive Technologies', '3D Solutions Inc',
    'Graphics Design Corp', 'Animation Studios', 'Film Production Ltd', 'Music Corporation',
    'Recording Studios', 'Sound Systems Inc', 'Audio Technologies', 'Video Streaming Corp',
    'Content Delivery Ltd', 'CDN Solutions Inc', 'Cloud Storage Corp', 'Data Centers Ltd',
    'Server Management Inc', 'Hosting Services Corp', 'Domain Registration Ltd', 'Web Hosting Inc',
    'Email Services Corp', 'Communication Systems', 'Telecom Solutions Ltd', 'Network Infrastructure',
    'Wireless Technologies', 'Satellite Systems Corp', 'Fiber Optics Ltd', 'Cable Networks Inc',
    'Internet Service Corp', 'Broadband Solutions', '5G Technologies Ltd', 'Mobile Networks Inc',
    'Telecommunications Corp', 'Phone Systems Ltd', 'VoIP Solutions Inc', 'Video Conferencing Corp',
    'Collaboration Tools Ltd', 'Project Management Inc', 'Task Automation Corp', 'Workflow Systems',
    'Business Process Ltd', 'Enterprise Solutions', 'CRM Systems Inc', 'ERP Technologies Corp',
    'Accounting Software Ltd', 'Financial Systems Inc', 'Banking Solutions Corp', 'Payment Processing Ltd',
    'Fintech Innovations', 'Cryptocurrency Corp', 'Digital Banking Ltd', 'Investment Systems Inc',
    'Trading Platforms Corp', 'Market Analysis Ltd', 'Financial Analytics Inc', 'Risk Management Corp',
    'Insurance Systems Ltd', 'Actuarial Services Inc', 'Underwriting Corp', 'Claims Processing Ltd',
    'Healthcare Systems Inc', 'Medical Technologies Corp', 'Pharmaceutical Ltd', 'Biotech Solutions',
    'Research Laboratories', 'Clinical Trials Corp', 'Drug Development Ltd', 'Medical Devices Inc',
    'Diagnostic Systems Corp', 'Treatment Solutions Ltd', 'Patient Management Inc', 'Electronic Health Records',
    'Telemedicine Corp', 'Remote Healthcare Ltd', 'Digital Therapeutics Inc', 'Health Analytics Corp',
    'Wellness Technologies Ltd', 'Fitness Solutions Inc', 'Nutrition Systems Corp', 'Mental Health Ltd',
    'Therapy Services Inc', 'Counseling Corp', 'Psychology Solutions Ltd', 'Behavioral Analytics Inc',
    'Educational Technologies', 'Learning Management Corp', 'Online Education Ltd', 'E-learning Solutions',
    'Training Systems Inc', 'Skill Development Corp', 'Professional Services Ltd', 'Consulting Group Inc',
    'Management Consulting Corp', 'Strategy Solutions Ltd', 'Business Advisory Inc', 'Financial Consulting Corp',
    'Legal Services Ltd', 'Law Firm Inc', 'Legal Technology Corp', 'Compliance Solutions Ltd',
    'Regulatory Affairs Inc', 'Government Relations Corp', 'Public Policy Ltd', 'Political Consulting Inc',
    'Lobbying Services Corp', 'Advocacy Groups Ltd', 'Non-profit Organizations', 'Charitable Foundations',
    'Social Services Corp', 'Community Development Ltd', 'Urban Planning Inc', 'Environmental Solutions Corp',
    'Sustainability Ltd', 'Green Technologies Inc', 'Renewable Energy Corp', 'Solar Power Systems',
    'Wind Energy Ltd', 'Hydroelectric Corp', 'Geothermal Solutions Inc', 'Nuclear Technologies Ltd',
    'Energy Storage Corp', 'Battery Systems Inc', 'Electric Vehicles Ltd', 'Transportation Solutions Corp',
    'Logistics Systems Inc', 'Supply Chain Management Ltd', 'Warehouse Automation Corp', 'Inventory Systems Inc',
    'Distribution Networks Ltd', 'Shipping Solutions Corp', 'Freight Management Inc', 'Transportation Technologies',
    'Railway Systems Corp', 'Aviation Solutions Ltd', 'Aerospace Technologies Inc', 'Defense Systems Corp',
    'Security Solutions Ltd', 'Surveillance Systems Inc', 'Access Control Corp', 'Identity Management Ltd',
    'Authentication Systems Inc', 'Authorization Corp', 'Permission Management Ltd', 'Role-based Access Inc',
    'Single Sign-On Corp', 'Multi-factor Authentication Ltd', 'Biometric Systems Inc', 'Facial Recognition Corp',
    'Voice Recognition Ltd', 'Fingerprint Systems Inc', 'Iris Scanning Corp', 'Retinal Recognition Ltd',
    'Palm Print Systems Inc', 'Hand Geometry Corp', 'Gait Recognition Ltd', 'Behavioral Biometrics Inc',
    'Keystroke Dynamics Corp', 'Mouse Movement Analysis Ltd', 'Touch Screen Patterns Inc', 'Device Fingerprinting Corp',
    'Hardware Security Ltd', 'Trusted Computing Inc', 'Secure Boot Corp', 'Hardware Attestation Ltd',
    'Cryptographic Systems Inc', 'Encryption Technologies Corp', 'Key Management Ltd', 'Digital Signatures Inc',
    'Certificate Authorities Corp', 'Public Key Infrastructure Ltd', 'Secure Communications Inc', 'VPN Technologies Corp',
    'Network Security Ltd', 'Firewall Systems Inc', 'Intrusion Detection Corp', 'Vulnerability Assessment Ltd',
    'Penetration Testing Inc', 'Security Auditing Corp', 'Compliance Monitoring Ltd', 'Risk Assessment Inc',
    'Threat Intelligence Corp', 'Security Analytics Ltd', 'Incident Response Inc', 'Forensic Analysis Corp',
    'Digital Forensics Ltd', 'Evidence Collection Inc', 'Chain of Custody Corp', 'Legal Discovery Ltd',
    'E-discovery Systems Inc', 'Document Management Corp', 'Content Analysis Ltd', 'Text Mining Inc',
    'Natural Language Processing Corp', 'Machine Translation Ltd', 'Speech Recognition Inc', 'Text-to-Speech Corp',
    'Voice Synthesis Ltd', 'Audio Processing Inc', 'Signal Analysis Corp', 'Pattern Recognition Ltd',
    'Computer Vision Inc', 'Image Processing Corp', 'Video Analysis Ltd', 'Object Detection Inc',
    'Facial Analysis Corp', 'Emotion Recognition Ltd', 'Gesture Detection Inc', 'Motion Tracking Corp',
    'Augmented Reality Ltd', 'Virtual Reality Inc', 'Mixed Reality Corp', 'Immersive Technologies Ltd',
    'Haptic Systems Inc', 'Tactile Feedback Corp', 'Force Feedback Ltd', 'Vibration Systems Inc',
    'Sensory Technologies Corp', 'Multimodal Interfaces Ltd', 'Brain-Computer Interfaces Inc', 'Neural Interfaces Corp',
    'Prosthetic Systems Ltd', 'Medical Implants Inc', 'Bionic Technologies Corp', 'Cyborg Systems Ltd',
    'Human Enhancement Inc', 'Transhuman Technologies Corp', 'Life Extension Ltd', 'Anti-aging Systems Inc',
    'Longevity Research Corp', 'Genetic Engineering Ltd', 'Gene Therapy Inc', 'CRISPR Technologies Corp',
    'Synthetic Biology Ltd', 'Bioengineering Inc', 'Tissue Engineering Corp', 'Organ Printing Ltd',
    'Regenerative Medicine Inc', 'Stem Cell Technologies Corp', 'Cellular Therapy Ltd', 'Immunotherapy Inc',
    'Cancer Treatment Corp', 'Oncology Solutions Ltd', 'Radiation Therapy Inc', 'Chemotherapy Corp',
    'Targeted Therapy Ltd', 'Precision Medicine Inc', 'Personalized Healthcare Corp', 'Genomic Medicine Ltd',
    'Pharmacogenomics Inc', 'Drug Discovery Corp', 'Molecular Medicine Ltd', 'Systems Biology Inc',
    'Computational Biology Corp', 'Bioinformatics Ltd', 'Genomics Technologies Inc', 'Proteomics Corp',
    'Metabolomics Ltd', 'Transcriptomics Inc', 'Epigenomics Corp', 'Microbiome Research Ltd',
    'Microbial Technologies Inc', 'Fermentation Systems Corp', 'Bioreactor Technologies Ltd', 'Industrial Biotechnology Inc',
    'Biofuels Corp', 'Biomaterials Ltd', 'Biodegradable Plastics Inc', 'Sustainable Materials Corp',
    'Circular Economy Ltd', 'Waste Management Inc', 'Recycling Technologies Corp', 'Upcycling Solutions Ltd',
    'Zero Waste Systems Inc', 'Carbon Capture Corp', 'Climate Technologies Ltd', 'Environmental Monitoring Inc',
    'Air Quality Systems Corp', 'Water Treatment Ltd', 'Pollution Control Inc', 'Clean Energy Corp',
    'Energy Efficiency Ltd', 'Smart Grid Technologies Inc', 'Power Management Corp', 'Energy Storage Ltd',
    'Battery Technologies Inc', 'Fuel Cells Corp', 'Hydrogen Systems Ltd', 'Electric Grid Inc',
    'Power Distribution Corp', 'Transmission Systems Ltd', 'Substation Technologies Inc', 'Smart Meters Corp',
    'Energy Analytics Ltd', 'Demand Response Inc', 'Load Balancing Corp', 'Grid Optimization Ltd',
    'Microgrid Systems Inc', 'Distributed Energy Corp', 'Community Solar Ltd', 'Residential Energy Inc',
    'Commercial Energy Corp', 'Industrial Energy Ltd', 'Manufacturing Systems Inc', 'Production Optimization Corp',
    'Quality Control Ltd', 'Process Automation Inc', 'Industrial IoT Corp', 'Smart Manufacturing Ltd',
    'Industry 4.0 Inc', 'Digital Twin Corp', 'Predictive Maintenance Ltd', 'Condition Monitoring Inc',
    'Asset Management Corp', 'Equipment Optimization Ltd', 'Supply Chain Visibility Inc', 'Inventory Optimization Corp',
    'Demand Forecasting Ltd', 'Sales Analytics Inc', 'Customer Analytics Corp', 'Market Research Ltd',
    'Business Intelligence Inc', 'Data Warehousing Corp', 'Data Lakes Ltd', 'Big Data Technologies Inc',
    'Data Processing Corp', 'Data Integration Ltd', 'ETL Systems Inc', 'Data Pipeline Corp',
    'Stream Processing Ltd', 'Real-time Analytics Inc', 'Batch Processing Corp', 'Data Orchestration Ltd',
    'Workflow Automation Inc', 'Process Mining Corp', 'Task Automation Ltd', 'Robotic Process Automation Inc',
    'Intelligent Automation Corp', 'Cognitive Computing Ltd', 'Artificial Intelligence Inc', 'Machine Learning Corp',
    'Deep Learning Ltd', 'Neural Networks Inc', 'Reinforcement Learning Corp', 'Supervised Learning Ltd',
    'Unsupervised Learning Inc', 'Semi-supervised Learning Corp', 'Transfer Learning Ltd', 'Federated Learning Inc',
    'Edge Computing Corp', 'Fog Computing Ltd', 'Cloud Computing Inc', 'Distributed Computing Corp',
    'Parallel Computing Ltd', 'High Performance Computing Inc', 'Quantum Computing Corp', 'Neuromorphic Computing Ltd',
    'Optical Computing Inc', 'DNA Computing Corp', 'Molecular Computing Ltd', 'Chemical Computing Inc',
    'Biological Computing Corp', 'Organic Computing Ltd', 'Inorganic Computing Inc', 'Hybrid Computing Corp',
    'Multi-core Systems Ltd', 'Many-core Technologies Inc', 'GPU Computing Corp', 'FPGA Systems Ltd',
    'ASIC Technologies Inc', 'System-on-Chip Corp', 'Embedded Systems Ltd', 'Real-time Systems Inc',
    'Operating Systems Corp', 'Middleware Technologies Ltd', 'Application Frameworks Inc', 'Software Architecture Corp',
    'Design Patterns Ltd', 'Software Engineering Inc', 'Agile Development Corp', 'DevOps Technologies Ltd',
    'Continuous Integration Inc', 'Continuous Deployment Corp', 'Infrastructure as Code Ltd', 'Configuration Management Inc',
    'Container Technologies Corp', 'Orchestration Systems Ltd', 'Service Mesh Inc', 'Microservices Architecture Corp',
    'API Management Ltd', 'API Gateway Inc', 'Service Discovery Corp', 'Load Balancing Ltd',
    'Traffic Management Inc', 'Network Optimization Corp', 'Content Delivery Ltd', 'Edge Computing Inc',
    'CDN Technologies Corp', 'Web Performance Ltd', 'Application Performance Inc', 'Monitoring Systems Corp',
    'Observability Technologies Ltd', 'Logging Systems Inc', 'Metrics Collection Corp', 'Tracing Technologies Ltd',
    'Alerting Systems Inc', 'Incident Management Corp', 'Service Level Management Ltd', 'Capacity Planning Inc',
    'Performance Testing Corp', 'Load Testing Ltd', 'Stress Testing Inc', 'Volume Testing Corp',
    'Spike Testing Ltd', 'Endurance Testing Inc', 'Scalability Testing Corp', 'Reliability Testing Ltd',
    'Availability Testing Inc', 'Recovery Testing Corp', 'Disaster Recovery Ltd', 'Business Continuity Inc',
    'Backup Systems Corp', 'Data Protection Ltd', 'Privacy Technologies Inc', 'Compliance Systems Corp',
    'Governance Technologies Ltd', 'Risk Management Inc', 'Security Governance Corp', 'Information Security Ltd',
    'Cybersecurity Inc', 'Network Security Corp', 'Application Security Ltd', 'Data Security Inc',
    'Cloud Security Corp', 'Mobile Security Ltd', 'IoT Security Inc', 'Endpoint Security Corp',
    'Identity Security Ltd', 'Access Security Inc', 'Privileged Access Corp', 'Zero Trust Security Ltd',
    'Security Operations Inc', 'Security Analytics Corp', 'Threat Hunting Ltd', 'Incident Response Inc',
    'Forensic Analysis Corp', 'Digital Forensics Ltd', 'Malware Analysis Inc', 'Vulnerability Research Corp',
    'Exploit Development Ltd', 'Penetration Testing Inc', 'Red Team Operations Corp', 'Blue Team Defense Ltd',
    'Purple Team Collaboration Inc', 'Security Training Corp', 'Awareness Programs Ltd', 'Security Culture Inc',
    'Human Factors Corp', 'Social Engineering Ltd', 'Phishing Prevention Inc', 'Security Awareness Corp',
    'Training Systems Ltd', 'Simulation Technologies Inc', 'Gamification Corp', 'Learning Management Ltd',
    'Knowledge Management Inc', 'Documentation Systems Corp', 'Wiki Technologies Ltd', 'Collaboration Tools Inc',
    'Communication Systems Corp', 'Messaging Platforms Ltd', 'Video Conferencing Inc', 'Screen Sharing Corp',
    'File Sharing Ltd', 'Version Control Inc', 'Code Repository Corp', 'Source Code Management Ltd',
    'Branching Strategies Inc', 'Merge Technologies Corp', 'Conflict Resolution Ltd', 'Code Review Inc',
    'Static Analysis Corp', 'Dynamic Analysis Ltd', 'Code Quality Inc', 'Technical Debt Corp',
    'Refactoring Technologies Ltd', 'Legacy Modernization Inc', 'Migration Strategies Corp', 'Transformation Planning Ltd',
    'Digital Transformation Inc', 'Business Transformation Corp', 'Process Transformation Ltd', 'Technology Transformation Inc',
    'Cultural Transformation Corp', 'Organizational Change Ltd', 'Change Management Inc', 'Stakeholder Management Corp',
    'Project Management Ltd', 'Program Management Inc', 'Portfolio Management Corp', 'Resource Management Ltd',
    'Time Management Inc', 'Cost Management Corp', 'Quality Management Ltd', 'Risk Management Inc',
    'Communication Management Corp', 'Procurement Management Ltd', 'Integration Management Inc', 'Scope Management Corp',
    'Schedule Management Ltd', 'Budget Management Inc', 'Vendor Management Corp', 'Contract Management Ltd',
    'Legal Management Inc', 'Compliance Management Corp', 'Audit Management Ltd', 'Governance Management Inc',
    'Policy Management Corp', 'Procedure Management Ltd', 'Standard Management Inc', 'Framework Management Corp',
    'Methodology Management Ltd', 'Best Practice Management Inc', 'Knowledge Management Corp', 'Information Management Ltd',
    'Data Management Inc', 'Content Management Corp', 'Document Management Ltd', 'Record Management Inc',
    'Archive Management Corp', 'Retention Management Ltd', 'Disposal Management Inc', 'Lifecycle Management Corp',
    'Asset Management Ltd', 'Inventory Management Inc', 'Supply Chain Management Corp', 'Logistics Management Ltd',
    'Transportation Management Inc', 'Distribution Management Corp', 'Warehouse Management Ltd', 'Fulfillment Management Inc',
    'Order Management Corp', 'Customer Management Ltd', 'Relationship Management Inc', 'Experience Management Corp',
    'Journey Management Ltd', 'Touchpoint Management Inc', 'Channel Management Corp', 'Multi-channel Management Ltd',
    'Omnichannel Management Inc', 'Digital Channel Corp', 'Online Channel Ltd', 'Offline Channel Inc',
    'Mobile Channel Corp', 'Social Channel Ltd', 'Email Channel Inc', 'SMS Channel Corp',
    'Phone Channel Ltd', 'Chat Channel Inc', 'Video Channel Corp', 'Video Management Ltd',
    'Streaming Technologies Inc', 'Broadcasting Corp', 'Production Systems Ltd', 'Post-production Inc',
    'Editing Technologies Corp', 'Color Grading Ltd', 'Audio Mixing Inc', 'Sound Design Corp',
    'Music Production Ltd', 'Recording Studios Inc', 'Live Sound Corp', 'Concert Systems Ltd',
    'Event Technologies Inc', 'Conference Systems Corp', 'Meeting Technologies Ltd', 'Collaboration Spaces Inc',
    'Workspace Design Corp', 'Office Technologies Ltd', 'Smart Buildings Inc', 'Building Automation Corp',
    'Facility Management Ltd', 'Maintenance Systems Inc', 'Energy Management Corp', 'HVAC Systems Ltd',
    'Lighting Control Inc', 'Security Systems Corp', 'Access Control Ltd', 'Surveillance Systems Inc',
    'Alarm Systems Corp', 'Fire Safety Ltd', 'Emergency Systems Inc', 'Safety Technologies Corp',
    'Health and Safety Ltd', 'Environmental Safety Inc', 'Workplace Safety Corp', 'Industrial Safety Ltd',
    'Construction Safety Inc', 'Mining Safety Corp', 'Chemical Safety Ltd', 'Nuclear Safety Inc',
    'Radiation Safety Corp', 'Biological Safety Ltd', 'Laboratory Safety Inc', 'Research Safety Corp',
    'Clinical Safety Ltd', 'Patient Safety Inc', 'Medical Safety Corp', 'Drug Safety Ltd',
    'Device Safety Inc', 'Equipment Safety Corp', 'Machine Safety Ltd', 'Robotic Safety Inc',
    'AI Safety Corp', 'Algorithmic Safety Ltd', 'Data Safety Inc', 'Privacy Safety Corp',
    'Information Safety Ltd', 'Network Safety Inc', 'System Safety Corp', 'Software Safety Ltd',
    'Hardware Safety Inc', 'Component Safety Corp', 'Material Safety Ltd', 'Chemical Safety Inc',
    'Biological Safety Corp', 'Physical Safety Ltd', 'Psychological Safety Inc', 'Social Safety Corp',
    'Economic Safety Ltd', 'Financial Safety Inc', 'Market Safety Corp', 'Investment Safety Ltd',
    'Banking Safety Inc', 'Insurance Safety Corp', 'Regulatory Safety Ltd', 'Compliance Safety Inc',
    'Legal Safety Corp', 'Ethical Safety Ltd', 'Moral Safety Inc', 'Social Responsibility Corp',
    'Corporate Responsibility Ltd', 'Sustainability Inc', 'Environmental Responsibility Corp', 'Social Impact Ltd',
    'Community Impact Inc', 'Stakeholder Impact Corp', 'Shareholder Impact Ltd', 'Employee Impact Inc',
    'Customer Impact Corp', 'Supplier Impact Ltd', 'Partner Impact Inc', 'Vendor Impact Corp',
    'Government Impact Ltd', 'Regulatory Impact Inc', 'Public Impact Corp', 'Global Impact Ltd',
    'Local Impact Inc', 'Regional Impact Corp', 'National Impact Ltd', 'International Impact Inc',
    'Cross-border Impact Corp', 'Multinational Impact Ltd', 'Transnational Impact Inc', 'Globalization Corp',
    'Localization Ltd', 'Internationalization Inc', 'Cultural Adaptation Corp', 'Language Technologies Ltd',
    'Translation Systems Inc', 'Localization Services Corp', 'Global Services Ltd', 'International Services Inc',
    'Cross-cultural Services Corp', 'Diversity Services Ltd', 'Inclusion Services Inc', 'Equity Services Corp',
    'Accessibility Services Ltd', 'Universal Design Inc', 'Inclusive Design Corp', 'Human-centered Design Ltd',
    'User Experience Inc', 'User Interface Corp', 'Interaction Design Ltd', 'Visual Design Inc',
    'Graphic Design Corp', 'Web Design Ltd', 'Mobile Design Inc', 'App Design Corp',
    'Game Design Ltd', 'Product Design Inc', 'Industrial Design Corp', 'Fashion Design Ltd',
    'Interior Design Inc', 'Architectural Design Corp', 'Urban Design Ltd', 'Landscape Design Inc',
    'Environmental Design Corp', 'Sustainable Design Ltd', 'Green Design Inc', 'Eco-friendly Design Corp',
    'Biomimetic Design Ltd', 'Nature-inspired Design Inc', 'Organic Design Corp', 'Fluid Design Ltd',
    'Dynamic Design Inc', 'Adaptive Design Corp', 'Responsive Design Ltd', 'Flexible Design Inc',
    'Modular Design Corp', 'Component Design Ltd', 'System Design Inc', 'Architecture Design Corp',
    'Software Architecture Ltd', 'System Architecture Inc', 'Enterprise Architecture Corp', 'Solution Architecture Ltd',
    'Technical Architecture Inc', 'Business Architecture Corp', 'Information Architecture Ltd', 'Data Architecture Inc',
    'Application Architecture Corp', 'Integration Architecture Ltd', 'Security Architecture Inc', 'Network Architecture Corp',
    'Infrastructure Architecture Ltd', 'Cloud Architecture Inc', 'Microservices Architecture Corp', 'Service Architecture Ltd',
    'API Architecture Inc', 'Event Architecture Corp', 'Streaming Architecture Ltd', 'Real-time Architecture Inc',
    'Batch Architecture Corp', 'Hybrid Architecture Ltd', 'Multi-tier Architecture Inc', 'N-tier Architecture Corp',
    'Layered Architecture Ltd', 'Component Architecture Inc', 'Plugin Architecture Corp', 'Modular Architecture Ltd',
    'Plugin Architecture Inc', 'Extension Architecture Corp', 'Add-on Architecture Ltd', 'Module Architecture Inc',
    'Package Architecture Corp', 'Library Architecture Ltd', 'Framework Architecture Inc', 'Platform Architecture Corp',
    'Ecosystem Architecture Ltd', 'Platform Ecosystem Inc', 'Developer Ecosystem Corp', 'Partner Ecosystem Ltd',
    'Vendor Ecosystem Inc', 'Supplier Ecosystem Corp', 'Customer Ecosystem Ltd', 'User Ecosystem Inc',
    'Community Ecosystem Corp', 'Open Source Ecosystem Ltd', 'Commercial Ecosystem Inc', 'Hybrid Ecosystem Corp',
    'Multi-vendor Ecosystem Ltd', 'Single-vendor Ecosystem Inc', 'Proprietary Ecosystem Corp', 'Open Ecosystem Ltd',
    'Closed Ecosystem Inc', 'Semi-open Ecosystem Corp', 'Controlled Ecosystem Ltd', 'Managed Ecosystem Inc',
    'Self-managing Ecosystem Corp', 'Autonomous Ecosystem Ltd', 'Intelligent Ecosystem Inc', 'Smart Ecosystem Corp',
    'Connected Ecosystem Ltd', 'IoT Ecosystem Inc', 'Digital Ecosystem Corp', 'Virtual Ecosystem Ltd',
    'Physical Ecosystem Inc', 'Real-world Ecosystem Corp', 'Augmented Ecosystem Ltd', 'Mixed Ecosystem Inc',
    'Hybrid Reality Corp', 'Extended Reality Ltd', 'Immersive Reality Inc', 'Virtual Reality Corp',
    'Augmented Reality Ltd', 'Mixed Reality Inc', 'Spatial Computing Corp', '3D Computing Ltd',
    'Volumetric Computing Inc', 'Holographic Computing Corp', 'Light Field Computing Ltd', 'Photonics Computing Inc',
    'Quantum Computing Corp', 'Neuromorphic Computing Ltd', 'DNA Computing Inc', 'Molecular Computing Corp',
    'Chemical Computing Ltd', 'Biological Computing Inc', 'Organic Computing Corp', 'Inorganic Computing Ltd',
    'Hybrid Computing Inc', 'Multi-modal Computing Corp', 'Cross-modal Computing Ltd', 'Transmodal Computing Inc',
    'Metamodal Computing Corp', 'Supramodal Computing Ltd', 'Hypermodal Computing Inc', 'Omnimodal Computing Corp',
    'Panmodal Computing Ltd', 'Universal Computing Inc', 'General Computing Corp', 'Specialized Computing Ltd',
    'Domain-specific Computing Inc', 'Application-specific Computing Corp', 'Task-specific Computing Ltd', 'Purpose-specific Computing Inc',
    'Function-specific Computing Corp', 'Feature-specific Computing Ltd', 'Capability-specific Computing Inc', 'Performance-specific Computing Corp',
    'Efficiency-specific Computing Ltd', 'Optimization-specific Computing Inc', 'Tuning-specific Computing Corp', 'Calibration-specific Computing Ltd',
    'Configuration-specific Computing Inc', 'Customization-specific Computing Corp', 'Personalization-specific Computing Ltd', 'Adaptation-specific Computing Inc',
    'Learning-specific Computing Corp', 'Training-specific Computing Ltd', 'Inference-specific Computing Inc', 'Prediction-specific Computing Corp',
    'Forecasting-specific Computing Ltd', 'Simulation-specific Computing Inc', 'Modeling-specific Computing Corp', 'Analysis-specific Computing Ltd',
    'Synthesis-specific Computing Inc', 'Design-specific Computing Corp', 'Creation-specific Computing Ltd', 'Generation-specific Computing Inc',
    'Production-specific Computing Corp', 'Manufacturing-specific Computing Ltd', 'Fabrication-specific Computing Inc', 'Assembly-specific Computing Corp',
    'Integration-specific Computing Ltd', 'Deployment-specific Computing Inc', 'Operation-specific Computing Corp', 'Maintenance-specific Computing Ltd',
    'Monitoring-specific Computing Inc', 'Management-specific Computing Corp', 'Administration-specific Computing Ltd', 'Governance-specific Computing Inc',
    'Control-specific Computing Corp', 'Regulation-specific Computing Ltd', 'Compliance-specific Computing Inc', 'Audit-specific Computing Corp',
    'Verification-specific Computing Ltd', 'Validation-specific Computing Inc', 'Testing-specific Computing Corp', 'Quality-specific Computing Ltd',
    'Assurance-specific Computing Inc', 'Security-specific Computing Corp', 'Safety-specific Computing Ltd', 'Reliability-specific Computing Inc',
    'Availability-specific Computing Corp', 'Durability-specific Computing Ltd', 'Sustainability-specific Computing Inc', 'Scalability-specific Computing Corp',
    'Flexibility-specific Computing Ltd', 'Adaptability-specific Computing Inc', 'Extensibility-specific Computing Corp', 'Modularity-specific Computing Ltd',
    'Composability-specific Computing Inc', 'Reusability-specific Computing Corp', 'Maintainability-specific Computing Ltd', 'Portability-specific Computing Inc',
    'Interoperability-specific Computing Corp', 'Compatibility-specific Computing Ltd', 'Standards-specific Computing Inc', 'Protocol-specific Computing Corp',
    'Interface-specific Computing Ltd', 'API-specific Computing Inc', 'Service-specific Computing Corp', 'Component-specific Computing Ltd',
    'Module-specific Computing Inc', 'Library-specific Computing Corp', 'Framework-specific Computing Ltd', 'Platform-specific Computing Inc',
    'Infrastructure-specific Computing Corp', 'Foundation-specific Computing Ltd', 'Base-specific Computing Inc', 'Core-specific Computing Corp',
    'Essential-specific Computing Ltd', 'Fundamental-specific Computing Inc', 'Basic-specific Computing Corp', 'Elementary-specific Computing Ltd',
    'Primary-specific Computing Inc', 'Secondary-specific Computing Corp', 'Tertiary-specific Computing Ltd', 'Quaternary-specific Computing Inc',
    'Quinary-specific Computing Corp', 'Senary-specific Computing Ltd', 'Septenary-specific Computing Inc', 'Octonary-specific Computing Corp',
    'Nonary-specific Computing Ltd', 'Denary-specific Computing Inc', 'Undenary-specific Computing Corp', 'Duodenary-specific Computing Ltd',
    'Tridenary-specific Computing Inc', 'Quattuordenary-specific Computing Corp', 'Quindenary-specific Computing Ltd', 'Sexdenary-specific Computing Inc',
    'Septendenary-specific Computing Corp', 'Octodenary-specific Computing Ltd', 'Novemdenary-specific Computing Inc', 'Vigintenary-specific Computing Corp',
    'Centenary-specific Computing Ltd', 'Millenary-specific Computing Inc', 'Decamillenary-specific Computing Corp', 'Centamillenary-specific Computing Ltd',
    'Kilomillenary-specific Computing Inc', 'Megamillenary-specific Computing Corp', 'Gigamillenary-specific Computing Ltd', 'Teramillenary-specific Computing Inc',
    'Petamillenary-specific Computing Corp', 'Examillenary-specific Computing Ltd', 'Zettamillenary-specific Computing Inc', 'Yottamillenary-specific Computing Corp'
];

// Random data generators
export function generateRandomPerson() {
    const firstName = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
    const lastName = LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
    return {
        firstName: firstName,
        lastName: lastName,
        fullName: `${firstName} ${lastName}`,
        type: 'P'
    };
}

export function generateRandomEntity() {
    const companyName = COMPANY_NAMES[Math.floor(Math.random() * COMPANY_NAMES.length)];
    return {
        name: companyName,
        type: 'E'
    };
}

export function generateRandomSearchTerm() {
    const isPerson = Math.random() < 0.5;
    if (isPerson) {
        const person = generateRandomPerson();
        return {
            query: person.fullName,
            type: 'P',
            entity: person
        };
    } else {
        const entity = generateRandomEntity();
        return {
            query: entity.name,
            type: 'E',
            entity: entity
        };
    }
}

// Generate multiple random search terms
export function generateRandomSearchTerms(count = 10) {
    const terms = [];
    for (let i = 0; i < count; i++) {
        terms.push(generateRandomSearchTerm());
    }
    return terms;
}

// Weighted random selection (some names more common than others)
export function generateWeightedRandomPerson() {
    // First 50 names have higher probability
    const firstName = Math.random() < 0.7 
        ? FIRST_NAMES[Math.floor(Math.random() * 50)]
        : FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
    
    const lastName = Math.random() < 0.7 
        ? LAST_NAMES[Math.floor(Math.random() * 50)]
        : LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
    
    return {
        firstName: firstName,
        lastName: lastName,
        fullName: `${firstName} ${lastName}`,
        type: 'P'
    };
}

// Generate realistic company names with patterns
export function generateRealisticEntity() {
    const prefixes = ['Global', 'International', 'Advanced', 'Smart', 'Digital', 'Future', 'Next', 'Ultra', 'Super', 'Mega'];
    const cores = ['Tech', 'Systems', 'Solutions', 'Services', 'Group', 'Corp', 'Inc', 'Ltd', 'LLC', 'Partners'];
    const suffixes = ['Technologies', 'Innovations', 'Dynamics', 'Ventures', 'Enterprises', 'Holdings', 'Industries', 'Manufacturing'];
    
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const core = cores[Math.floor(Math.random() * cores.length)];
    const suffix = Math.random() < 0.3 ? suffixes[Math.floor(Math.random() * suffixes.length)] : '';
    
    const name = suffix ? `${prefix} ${core} ${suffix}` : `${prefix} ${core}`;
    
    return {
        name: name,
        type: 'E'
    };
}

// Export all generators
export default {
    generateRandomPerson,
    generateRandomEntity,
    generateRandomSearchTerm,
    generateRandomSearchTerms,
    generateWeightedRandomPerson,
    generateRealisticEntity
};
