&#x20;ANSWERS FOR HEALTHTRACK API

Student: Lucy Wambui Kimani

&#x20;Registration: C027-01-0890/2024







EXERCISE 1: AUTHENTICATION LOGIC QUESTIONS



Question 1: Why is it important to store the JWT secret key in an environment variable instead of hardcoding it?



Answer:

It is important to store the JWT secret key in an environment variable instead of hardcoding it because of security concerns. If the code is leaked or exposed on platforms like GitHub, the secret key would be compromised. Environment variables allow different secrets for development, staging, and production environments. They also make it easier to rotate or change secret keys without modifying and redeploying code. This follows security best practices and prevents accidental exposure of secrets in version control systems.



Question 2: What would happen if the JWT secret key is compromised?



Answer:

If the JWT secret key is compromised, attackers can create valid JWT tokens impersonating any user in the system. This would lead to a complete system breach where attackers can access all protected endpoints and sensitive patient data. They could impersonate doctors, patients, or administrators. This would result in a serious data breach exposing medical records, potential HIPAA violations, legal consequences, fines, and complete loss of user trust in the system. Immediate action would be required to rotate the secret and invalidate all existing tokens.



Question 3: Why do we use HttpOnly cookies for storing JWT tokens?



Answer:

We use HttpOnly cookies for storing JWT tokens because they provide protection against Cross-Site Scripting attacks since JavaScript cannot access HttpOnly cookies. Cookies are automatically sent with each request, making them convenient for authentication. They can be configured with Secure flags requiring HTTPS and SameSite attributes for additional security. This approach is more secure than storing tokens in localStorage or sessionStorage, which are vulnerable to XSS attacks. HttpOnly cookies also benefit from built-in browser session management features.







EXERCISE 2: PASSWORD RESET QUESTIONS



Question 1: What security measures should be in place for password reset?



Answer:

Security measures for password reset should include rate limiting to prevent brute force attacks, token expiration so reset links expire after a short time like one hour, one-time use tokens that are invalidated after use, no user enumeration so attackers cannot determine if an email is registered, strong cryptographically secure token generation, HTTPS requirement for all reset operations, email verification by sending reset links to registered email addresses, and audit logging to track all password reset attempts for security monitoring.



Question 2: How would you prevent abuse of the forgot password endpoint?



Answer:

To prevent abuse of the forgot password endpoint, I would implement rate limiting to restrict requests per IP address, add CAPTCHA verification after multiple failed attempts, temporarily lock accounts after too many failed reset attempts, send verification links to confirmed email addresses, monitor request patterns for suspicious activity, enforce minimum time between requests, block suspicious IP addresses, and notify users when reset requests are made so they can identify unauthorized attempts.



Question 3: Why should reset tokens have an expiration time?



Answer:

Reset tokens should have an expiration time because it reduces the attack window for stolen tokens, prevents replay attacks by making expired tokens unusable, forces users to reset passwords promptly, improves overall security, allows cleanup of stale tokens from the database, encourages good user behavior, and helps meet security compliance standards that require token expiration.







EXERCISE 3: ROLE-BASED ACCESS CONTROL QUESTIONS



Question 1: Why is it important to have role-based access control in a medical application?



Answer:

Role-based access control is important in medical applications because it protects sensitive patient data from unauthorized access, ensures compliance with healthcare regulations like HIPAA and GDPR, maintains patient privacy by restricting access to only authorized personnel, enforces professional boundaries so doctors only see their own patients, provides clear audit trails for accountability, limits damage if a user account is compromised, follows the principle of least privilege, and builds patient trust by demonstrating commitment to data protection.



Question 2: How would you handle a scenario where a patient needs to be assigned to multiple doctors?



Answer:

To handle multiple doctors per patient, I would create a many-to-many relationship using a junction table like PatientDoctorAssignment. This table would contain patient\_id, doctor\_id, assigned\_at timestamp, and a boolean field for is\_primary to designate the primary care provider. All assigned doctors would have access to the patient's records. The system would implement audit logging to track when doctors are added or removed from patient assignments. An admin interface would allow managing doctor assignments for each patient.



Question 3: What happens if a user's role is changed from patient to doctor?



Answer:

When a user's role is changed from patient to doctor, the permission changes take effect immediately in the system. However, existing JWT tokens still contain the old role information, so the system must either force re-authentication or invalidate all existing tokens. The role change should be logged with timestamp and who made the change. All active sessions should have their permissions re-evaluated. The user should be notified of the role change, and the system should ensure the user can access appropriate data for their new role. Business rules should validate that the role change is allowed and appropriate.







EXERCISE 4: TOKEN BLACKLISTING QUESTIONS



Question 1: Why is token blacklisting necessary when JWTs are stateless?



Answer:

Token blacklisting is necessary for stateless JWTs because it enables immediate revocation of tokens without waiting for expiration. This supports secure logout functionality where users can invalidate their sessions. It allows quick response to security incidents by revoking compromised tokens. It supports password changes by invalidating old tokens. It enables token refresh when user permissions change. It helps with compliance requirements for session management and audit trails. It gives users control over their active sessions and allows quick response during security breaches.



Question 2: What are the trade-offs of implementing token blacklisting?



Answer:

The trade-offs of implementing token blacklisting include performance impact because each request requires a database or cache lookup, additional storage requirements for storing blacklisted tokens, added complexity to the authentication system, cleanup overhead for expired tokens, potential single point of failure if the blacklist service is down, consistency issues in distributed systems, extra latency on authenticated requests, breaking the stateless nature of JWTs, and additional infrastructure costs for maintaining the blacklist storage.



Question 3: How would you handle expired tokens in the blacklist?



Answer:

To handle expired tokens in the blacklist, I would implement automatic cleanup jobs to remove expired tokens, add database indexes on expiration dates for efficient queries, use Redis or similar cache with built-in TTL functionality, filter expired tokens during queries, run background tasks for cleanup like daily cron jobs, only add unexpired tokens to the blacklist, monitor blacklist size and cleanup success, provide an admin tool to view and manage the blacklist, and optimize storage for quick lookups.







EXERCISE 5: TWO-FACTOR AUTHENTICATION QUESTIONS



Question 1: Why is 2FA particularly important for healthcare applications?



Answer:

Two-factor authentication is particularly important for healthcare applications because it protects highly sensitive medical records from unauthorized access, helps meet HIPAA and other regulatory compliance requirements, prevents medical identity theft, secures doctor accounts from unauthorized access, builds patient trust in the system, mitigates the risk of password theft, reduces the risk of data breaches, prevents unauthorized prescriptions, protects patient medical history, and adds an extra layer of security beyond passwords alone.



Question 2: How would you handle a user losing their 2FA device?



Answer:

To handle a user losing their 2FA device, I would provide backup codes during the initial setup process, implement email-based recovery options, use security questions for alternative verification, require identity verification through government ID or other means, allow administrators to disable 2FA with proper authorization, implement time-limited recovery processes, require multiple verification methods for recovery, log all recovery attempts for audit purposes, notify users of recovery attempts via email or SMS, and require re-verification before re-enabling 2FA.



Question 3: What are the trade-offs of implementing 2FA versus using longer passwords?



Answer:

The trade-offs of implementing 2FA versus using longer passwords include: 2FA provides much higher security because it requires two factors but creates more user friction by requiring a device. Longer passwords are simpler to implement but only protect against brute force attacks. 2FA implementation is more complex and costly but protects against phishing and credential theft. Longer passwords are cheaper to implement but are vulnerable if the password is stolen. 2FA requires users to keep a device secure while longer passwords only require memory. Recovery from 2FA issues is more complex while password reset is simpler. 2FA meets higher compliance standards and protects against more attack vectors overall.





