# Hybrid IAM Automation & Cloud Federation

## Executive Summary
This laboratory exercise demonstrates the design and implementation of a robust, hybrid Identity and Access Management (IAM) architecture. By bridging a custom-built, on-premise Active Directory environment with the Okta cloud platform (an industry-standard alternative to Google Workspace), this project establishes seamless and centralized identity federation. 

Beyond fundamental directory synchronization, this deployment heavily emphasizes modern incident response readiness and DevSecOps principles. The successful execution of a Python-driven, zero-touch provisioning and de-provisioning pipeline via a secure WinRM bridge illustrates how programmatic automation can completely eliminate human latency during critical security events. 

---

## Phase 1: On-Premise Directory & Security Baseline
The foundation of the architecture is a Windows Server 2022 Virtual Machine acting as the primary Domain Controller. 
* **Directory Architecture:** Configured Active Directory Domain Services (AD DS) and established a structured Organizational Unit (OU) hierarchy (`Enterprise_Users`) to isolate standard employee accounts.
* **Access Control:** Provisioned initial directory objects and enforced standard enterprise password rotation policies.

<img width="460" height="397" alt="Screenshot 2026-06-05 200817" src="https://github.com/user-attachments/assets/d5b7fc96-b8e2-4747-aaff-49ca3f60b521" />

*> Creating the foundational directory structure and initial test accounts in the local domain.*

### SOC Readiness & Hardening
To prepare the environment for future SIEM integration (such as Splunk or Wazuh), the identity perimeter was hardened using Group Policy Objects (GPO).
* **Account Lockout Policies:** Enforced strict account lockout thresholds (5 invalid attempts) to mitigate brute-force credential attacks.
* **Identity Auditing:** Enabled comprehensive Windows Event logging for Account Management and Logon Events, establishing the necessary telemetry for downstream SOC alerting.

<img width="864" height="705" alt="Screenshot 2026-06-05 232148" src="https://github.com/user-attachments/assets/e02ccf0a-3400-4dc5-9556-b72914709366" />

*> Enforcing Identity Auditing via GPO to generate critical security telemetry.*

---

## Phase 2: The Automation Bridge (WinRM)
To replace manual administrative tasks, a programmatic backdoor was established using Windows Remote Management (WinRM). 
* Configured the Domain Controller to securely accept remote PowerShell payloads over the local network via NTLM authentication.
* Developed a Python application utilizing the `pywinrm` library to simulate an enterprise bulk-onboarding pipeline, routing new user objects directly into the targeted OUs with enforced complex passwords.

---

## Phase 3: Okta Cloud Federation
To achieve modern cloud access and centralized MFA management, the local Active Directory was federated to Okta.
* **Cryptographic Alignment:** Resolved native legacy cryptographic protocol mismatches by forcing the Windows Server .NET framework to utilize modern TLS 1.2 standards.
* **Agent Deployment:** Successfully deployed the Okta AD Agent, bypassing strict local service account limitations to establish a persistent, secure, outbound-only polling tunnel to the Okta cloud environment.

<img width="794" height="794" alt="Screenshot 2026-06-06 011216" src="https://github.com/user-attachments/assets/1d8be01d-4e3f-4e24-8731-3fa16d0ca2f6" />

*> Configuring the directory integration and synchronization rules within the Okta Admin Console.*

---

## Phase 4: Cloud Identity Synchronization
With the tunnel established, synchronization rules were configured to selectively map the targeted on-premise OUs to the cloud directory.
* Implemented User Principal Name (UPN) mapping to ensure cloud identities maintained standard email-format routing.
* Executed a full directory import, successfully translating on-premise Active Directory objects into active, cloud-native Okta profiles.

<img width="809" height="720" alt="Screenshot 2026-06-06 011737" src="https://github.com/user-attachments/assets/5c570bb2-4187-4878-9c1e-bbfbec2ad7b7" />

*> Successful Active Directory to Okta federation, mapping local users to cloud identities.*

---

## Phase 5: Zero-Touch De-Provisioning (Incident Response)
To mitigate the risk of orphaned credentials and compromised accounts, a zero-touch offboarding pipeline was engineered.
* Developed a PowerShell payload that dynamically queries AD objects by UPN and executes immediate account suspension (`Disable-ADAccount`).
* **The Lifecycle Loop:** Validated the automated pipeline by executing the Python offboarding script. The script successfully disabled the targeted on-premise account in real-time, which subsequently triggered an automated access revocation and account suspension in the Okta cloud during the next polling cycle.

---

## Business Value and Security Impact
This architecture demonstrates a highly scalable approach to modern identity security. By replacing manual offboarding with an automated WinRM-to-PowerShell bridge, the environment is fully primed for advanced DevSecOps integration. In the event of a critical security alert—such as anomalous lateral movement caught by a SIEM—an automated SOAR webhook can immediately trigger this Python payload, ensuring the threat is isolated on-premise and access is revoked globally in the cloud with zero human latency.
