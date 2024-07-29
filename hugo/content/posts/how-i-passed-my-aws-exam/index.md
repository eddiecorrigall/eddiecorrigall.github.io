+++
title = 'How I Passed My AWS Exam'
date = 2019-12-04T16:04:00-04:00
draft = false

ShowReadingTime = true
ShowWordCount = true

UseHugoToc = true
ShowToc = true
TocOpen = true

[cover]
image = '/posts/how-i-passed-my-aws-exam/cover.png'
alt = 'How I passed my AWS exam cover image'
caption = ''
relative = false
+++

I passed my exam, you can too.
The grade you need to pass is not known, and changes per exam and region taken.
You should aim for a minimum of 70%.

## AWS Certified Developer Associate
This is the easiest of the associate level exams, but that is not to say that everyone will pass.
Its a lot of material, and you will need time for it to soak in.
You can do it!

## Resources
- **Udemy Cloudguru Course by Ryan Kroonenburg** – Bought and thoroughly watched at 1.5x the speed, took lots of notes
- **AWS Certified Solutions Architect (Official Study Guide)** – Read/skimmed not really that helpful
- **WhizLabs Practice Exams** – Extremely useful, very similar to AWS exam
- **AWS FAQs** – Read the FAQs, these are really boring, but often have scenarios that AWS exams draw upon

## Technique
My strategy was to learn the material first, then take practice exams.
When you take a practice exam, mark all questions for review.
Take notes on what you did wrong and try to understand why.
Go back and review video lectures, books, FAQs if you need too.
I made a copy of all the Q&A (and explanations) that I didn't get right, and took a copy with me on the train to the exam.

## Things to Focus on
I will likely forget some stuff here, but this is roughly what I recall as important.

### Limitations (min & max), defaults
Memorization is not fun, but it will get you marks AWS CLI/API.

### Common API names
- Familiarize yourself, focus on capability/features not the exact name
- 4XX, 5XX common scenario response codes

### Security Token Service (STS)
- Federating
- Identity Broker
- LDAP scenario

### Identity and Access Management (IAM)
- Users, Roles, Policies, etc..
- Policy evaluation algorithm
- Sharing an AWS account
- Roles
  - Attaching roles to instances
  - Can it be done on the fly?
  - How can applications assume roles?

### Elastic Cloud Computing (EC2)
- Block store vs Elastic Block Store
- Amazon Machine Image (AMI)
  - How can you share between accounts / regions?
  - Can this affect a CloudFormation template deployment?
- User vs Instance metadata

### DynamoDB
- Optimistic Concurrency Control
- Strongly consistent reads/writes
- How to provision read and write capacity
- Global vs Secondary index
- Partition/Hash vs Sort/Range keys
- Capabilities for SCAN and QUERY
- Provisioned Throughput exceeded exceptions
- Designing a good primary key
- How does it work? – at a high level

### Route53 + CloudFront + Elastic Load Balancer
- Record names (Alias Record and why its important)
- Sticky sessions, and how to resolve issues with ElastiCache

### S3
- Write-after-read consistency scenario
- DNS URL formats
- Static Hosting
  - What are the steps to make a bucket public and statically hosted
  - What is required to host statically?
  - Index document?
  - CORS?
- Storage tiers
  - Standard
  - Infrequent Access (IA)
  - Reduced Redundancy (RRS)
  - Snowball
  - Glacier
- Client-side encryption
- Advanced Encryption Standard (AES-256)
- How to enable encryption at rest (x-amz-server-side-encryption)
- 3 types of server-side encryption: Customer (SSE-C), Key Management Service (SSE-KMS), SSE-S3
- Lambda events
  - Scenario: RRS thumbnail regeneration

### SQS
- Message redundancy to consumers
- MessageVisibility
- FIFO
- Long-polling (what is it? how can it help? defaults? API name?)

### SNS
- Fanout technique
- Message format
- Supported protocols

### CloudFormation
- Rollback scenario
- Know required sections

### Virtual Private Cloud (VPC)
- Regions vs Availability Zones (AZs)
- NAT vs Bastion
- NAT
  - Instance vs gateway
  - How to resolve traffic
- ElasticIP
- Routers
- Subnets
