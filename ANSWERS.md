&#x20;TechVault API - Answers to Questions

&#x20;Name: Lucy Kimani

&#x20;Registration Number: C027-01-0890/2024



&#x20;Exercise 2: Supplier Model Questions



1\. Why is it important to validate email format on the backend?



Validating email format on the backend is crucial for several reasons:

\- Data Integrity: Ensures all emails in the database follow a standard format, making them usable for communication

\- Security: Prevents injection attacks and validates that input is legitimate

\- Reliability: Guarantees that emails can be used for automated notifications, invoices, and communications

\- Professionalism: Maintains professional data quality and prevents embarrassing formatting issues

\- Error Prevention: Catches typos early before they cause delivery failures

\- Consistency: Backend validation works regardless of frontend implementation



&#x20;2. What would happen if a product is created with a supplier\_id that doesn't exist?



If a product is created with a non-existent supplier\_id:

\- A foreign key constraint violation would be triggered at the database level

\- The operation would fail and rollback

\- The API would return a 409 Conflict error (as handled by our integrity\_error\_handler)

\- The product would not be created, ensuring database referential integrity

\- This prevents orphaned records and maintains data consistency



Exercise 3: Bulk Update Questions



1\. How would you handle a scenario where some products in the category would fall below the minimum price?



The implementation handles this by:

\- Pre-checking: Calculating the new price for each product before updating

\- Validation: Checking if the new price would be below 100 KSh

\- Skipping: Products that would go below minimum are skipped from the update

\- Reporting: Details of skipped products are returned in the response

\- Transactional Safety: Only successful updates are committed; failures don't affect other products



Alternative approaches could include:

\- Capping prices at minimum (setting them to exactly 100 KSh)

\- Rejecting the entire operation if any product would go below minimum

\- Notifying the user to adjust the discount percentage



2\. Should this endpoint be available to all users or only administrators?



This endpoint should be restricted to administrators only because:

\- Financial Impact: Bulk price changes affect revenue and profit margins

\- Security: Prevents unauthorized users from manipulating prices

\- Auditing: Price changes should be tracked and attributable

\- Business Rules: Only authorized personnel should make pricing decisions

\- Potential Damage: An attacker could set all prices to 1 KSh or apply 100% discounts



Implementation would require:

\- Authentication (JWT tokens)

\- Authorization (role-based access control)

\- Audit logging of who made changes



&#x20;Exercise 4: Stock Adjustment Questions



1\. Why would it be problematic to allow negative stock adjustments without validation?



Allowing negative stock adjustments without validation causes several issues:

\- Inventory Integrity: Could result in negative stock, which is impossible in real life

\- Order Fulfillment: Might allow selling products that don't exist

\- Business Logic: Breaks inventory management rules

\- Reporting: Distorts inventory reports and financial statements

\- Customer Trust: Could lead to orders being placed for out-of-stock items



Our validation ensures:

\- Stock never goes negative

\- Maximum stock limits are respected

\- Inventory remains accurate and reliable



&#x20;2. How would you handle concurrent stock adjustments (two people updating the same product at the same time)?



Concurrent stock adjustments can be handled using:



1\. Optimistic Locking:

\- Add a version column to the product table

\- Check version when updating

\- If version mismatches, reject the update and retry



2\. Pessimistic Locking:

\- Use database SELECT ... FOR UPDATE

\- Locks the row until transaction completes

\- Guarantees consistency but reduces concurrency



3\. Atomic Updates:

\- Use SQL UPDATE with conditions

\- Example: `UPDATE products SET stock = stock + ? WHERE id = ?`

\- Database handles concurrency automatically



4\. Queue-based System:

\- Put stock adjustments in a queue

\- Process sequentially in order

\- Ensures consistency but introduces latency



Recommended for this system: Atomic database updates with transaction isolation to handle concurrent updates safely.



&#x20;Exercise 5: Error Response Format Question



Why is it important to have a consistent error response format across all endpoints?



A consistent error response format provides:



1\. Client Developer Experience:

\- Easier to handle errors in frontend code

\- Predictable structure for error parsing

\- Reduced debugging time



2\. API Maintainability:

\- Standardized logging format

\- Easier to add error handling middleware

\- Consistent monitoring and alerting



3\. User Experience:

\- Clear, consistent error messages

\- Better error recovery flows

\- Professional API feel



4\. Tooling Compatibility:

\- Works with API clients and SDKs

\- Easy integration with monitoring tools

\- Standardized for API documentation



5\. Operational Benefits:

\- Faster troubleshooting

\- Consistent error tracking

\- Easier to identify patterns in errors



Our format includes:

\- `success: false` - Clear success/failure indicator

\- `status\_code` - HTTP status code

\- `message` - Human-readable error message

\- `errors` - Detailed field-level errors (when available)

\- `timestamp` - When the error occurred

\- `path` - Which endpoint was called



This provides everything needed for debugging and user feedback.

