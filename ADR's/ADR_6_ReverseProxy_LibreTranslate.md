# ADR 006: Use NGINX as a Reverse Proxy for HTTPS with LibreTranslate

## Status
Decided

## Context
LibreTranslate is a core component of Textify, providing translation services. However, it does not natively support HTTPS for secure communication. To ensure secure interactions between clients and the LibreTranslate service, HTTPS support must be added. Various solutions were considered to implement HTTPS, including:

1. Modifying LibreTranslate to handle SSL/TLS directly.
2. Using a reverse proxy (e.g., NGINX, HAProxy) to manage HTTPS externally.
3. Relying on cloud-native tools to handle HTTPS (e.g., AWS ALB, GCP HTTPS Load Balancer).

Key factors influencing the decision include:

- **Ease of implementation**
- **Maintainability**
- **Performance**
- **Security**
- **Flexibility**
- **Scalability**

## Decision
NGINX will be used as a reverse proxy to handle HTTPS for LibreTranslate.

## Rationale

### Why NGINX?
1. **Proven Performance**: NGINX is a widely used, high-performance web server and reverse proxy solution capable of handling large volumes of traffic efficiently.
2. **Ease of SSL/TLS Configuration**: NGINX offers straightforward mechanisms to set up SSL/TLS, making it easy to enforce HTTPS.
3. **Flexibility**: 
   - NGINX supports complex configurations, such as load balancing, rate limiting, and caching, which may be useful in future scaling.
   - It can manage multiple backend services, making it adaptable for deployment scenarios with multiple microservices.
4. **Separation of Concerns**:
   - By delegating HTTPS handling to NGINX, LibreTranslate can remain focused on its core functionality without the overhead of SSL/TLS management.
   - This separation improves maintainability and reduces the risk of introducing security vulnerabilities in LibreTranslate.
5. **Community and Support**: NGINX has extensive documentation and a large user community, ensuring long-term support and quick resolution of issues.
6. **Cost-Effective**: As open-source software, NGINX is free to use, minimizing additional deployment costs.

### Alternatives Considered

1. **Adding HTTPS Support to LibreTranslate**
   - **Pros**:
     - Direct SSL/TLS handling by the service.
   - **Cons**:
     - Significant development effort.
     - Increased complexity and maintenance burden on LibreTranslate.
     - Potential for introducing security vulnerabilities.
   - **Reason for Rejection**: Lack of direct SSL/TLS support in LibreTranslate and the overhead of custom implementation.

2. **Cloud-Native HTTPS Solutions**
   - **Pros**:
     - Simplifies management in a cloud environment.
     - Automatic certificate management (e.g., Let’s Encrypt integration).
   - **Cons**:
     - Vendor lock-in.
     - Additional costs.
     - Complexity in hybrid or local deployment scenarios.
   - **Reason for Rejection**: Limited flexibility and higher cost in non-cloud environments.

3. **Other Reverse Proxies (e.g., HAProxy, Caddy)**
   - **HAProxy**:
     - **Pros**: Excellent load balancing capabilities, high performance.
     - **Cons**: More complex configuration compared to NGINX for SSL/TLS.
   - **Caddy**:
     - **Pros**: Built-in HTTPS with automatic certificate renewal.
     - **Cons**: Smaller community and ecosystem than NGINX.
   - **Reason for Rejection**: NGINX’s balance of performance, flexibility, and support makes it the preferred choice.

## Consequences

### Positive
- **Enhanced Security**: HTTPS ensures secure communication, protecting sensitive data from interception or tampering.
- **Scalability**: NGINX can efficiently handle increased traffic as the application scales.
- **Simplified Configuration**: Centralized SSL/TLS management reduces the complexity of securing LibreTranslate.
- **Maintainability**: LibreTranslate remains lightweight and focused on its primary purpose.

### Negative
- **Additional Component**: Introducing NGINX adds another layer to the deployment stack, which requires monitoring and management.
- **Initial Setup**: Setting up and configuring NGINX requires time and expertise.

## Implementation
1. **NGINX Setup**:
   - Install NGINX on the same server or container as LibreTranslate or on a separate machine.
   - Configure NGINX as a reverse proxy for LibreTranslate, forwarding traffic from an HTTPS endpoint to LibreTranslate’s HTTP endpoint.
   
2. **SSL/TLS Configuration**:
   - Obtain SSL/TLS certificates (e.g., using Let’s Encrypt).
   - Configure NGINX to use the certificates and enforce HTTPS for all incoming traffic.
   
3. **Testing**:
   - Verify secure communication between clients and LibreTranslate via NGINX.
   - Test error handling and edge cases (e.g., expired or revoked certificates).

4. **Monitoring**:
   - Set up monitoring for NGINX to track traffic, performance, and errors.

## Decision Owner
Engineering Lead – Textify Project
