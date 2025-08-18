# Approval Process Implementation Guide

This guide explains how to implement approval processes for PROD deployments using both CTMS and GitHub approaches.

## 🏢 **CTMS Approval Process**

### **Overview:**
Uses SAP Transport Management Service's built-in approval workflow for transport requests.

### **Implementation Steps:**

#### **1. Configure CTMS Approval Groups**
In SAP TMS Cockpit:
1. **Navigate**: TMS Cockpit → Administration → Approval Groups
2. **Create**: `PROD_APPROVER_GROUP`
3. **Add Members**: Production approvers (users/emails)
4. **Set Rules**: Require approval for TARGET_NODE (PROD) imports

#### **2. Set Transport Approval Requirements**
```json
{
  "nodeName": "TARGET_NODE",
  "approvalRequired": true,
  "approverGroup": "PROD_APPROVER_GROUP",
  "minimumApprovers": 1,
  "autoApproval": false
}
```

#### **3. API Endpoints for Approval:**

**Request Approval:**
```
POST {TMS_BASE_URL}/v2/transportRequests/{transportId}/approval
{
  "action": "REQUEST_APPROVAL",
  "comment": "GitHub Actions requesting approval for PROD deployment",
  "approver": "PROD_APPROVER_GROUP"
}
```

**Check Approval Status:**
```
GET {TMS_BASE_URL}/v2/transportRequests/{transportId}
Response: {
  "status": "PENDING_APPROVAL",
  "approvalStatus": "PENDING|APPROVED|REJECTED"
}
```

**Approve Transport (Manual):**
```
POST {TMS_BASE_URL}/v2/transportRequests/{transportId}/approve
{
  "comment": "Approved for production deployment",
  "approver": "approver@company.com"
}
```

#### **4. Notification Setup:**
- **Email Notifications**: Configure in TMS for approval requests
- **Slack Integration**: Use webhooks for approval notifications
- **Teams Integration**: Custom notifications via Power Automate

### **CTMS Approval Workflow:**
```
1. Transport Created → 2. Approval Requested → 3. Approver Notified → 
4. Manual Approval → 5. Deployment Proceeds
```

---

## 🔐 **GitHub Environment Approval Process**

### **Overview:**
Uses GitHub's built-in environment protection rules for deployment approvals.

### **Implementation Steps:**

#### **1. Create Production Environment**
In GitHub Repository:
1. **Settings** → **Environments** → **New Environment**
2. **Name**: `production`
3. **Configure Protection Rules**

#### **2. Environment Protection Rules:**

**Required Reviewers:**
- Add specific users/teams who can approve PROD deployments
- Minimum reviewers: 1-6 people
- Prevent self-review if desired

**Wait Timer:**
- Optional delay before deployment (e.g., 5 minutes)
- Allows for last-minute cancellation

**Deployment Branches:**
- Restrict to `main` branch only
- Ensure only main branch can deploy to PROD

#### **3. Workflow Configuration:**
```yaml
jobs:
  deploy_to_prod:
    environment: production  # This triggers approval
    steps:
      # Deployment steps here
```

#### **4. Environment Secrets:**
Store PROD-specific secrets in the production environment:
- `TMS_PROD_NODE_ID`
- `PROD_NOTIFICATION_WEBHOOK`
- Any PROD-specific configurations

### **GitHub Approval Workflow:**
```
1. PR Merged to Main → 2. Workflow Triggered → 3. Approval Required → 
4. Reviewer Approves → 5. Deployment Proceeds
```

---

## 🔄 **Hybrid Approach (Recommended)**

Combine both GitHub and CTMS approvals for maximum security:

### **Implementation:**
1. **GitHub Environment**: Controls workflow execution
2. **CTMS Approval**: Controls transport deployment
3. **Dual Approval**: Both must approve for deployment

### **Workflow:**
```yaml
jobs:
  deploy_to_prod:
    environment: production  # GitHub approval required
    steps:
      - name: Create Transport
      - name: Request CTMS Approval  # CTMS approval required
      - name: Wait for CTMS Approval
      - name: Deploy (only after both approvals)
```

---

## 📋 **Setup Instructions**

### **For CTMS Approval:**

#### **1. Add GitHub Secrets:**
```
CTMS_APPROVER_GROUP = PROD_APPROVER_GROUP
CTMS_NOTIFICATION_WEBHOOK = https://your-webhook-url
```

#### **2. Configure TMS Cockpit:**
- Set up approval groups
- Configure email notifications
- Test approval workflow

#### **3. Test Approval Process:**
```bash
# Create test transport
# Request approval via API
# Verify notification sent
# Approve via TMS Cockpit
# Confirm deployment proceeds
```

### **For GitHub Environment Approval:**

#### **1. Create Environment:**
- Repository → Settings → Environments → New
- Name: `production`

#### **2. Set Protection Rules:**
- Required reviewers: Add approver users/teams
- Deployment branches: `main` only

#### **3. Update Workflow:**
```yaml
environment: production
```

#### **4. Test Approval Process:**
- Merge PR to main
- Verify approval request appears
- Approve via GitHub UI
- Confirm deployment proceeds

---

## 🚨 **Security Best Practices**

### **Access Control:**
- **CTMS**: Separate approver groups for DEV/PROD
- **GitHub**: Use teams, not individual users
- **Principle of Least Privilege**: Minimal necessary permissions

### **Audit Trail:**
- **CTMS**: Built-in transport audit logs
- **GitHub**: Environment deployment history
- **Notifications**: Log all approval requests/responses

### **Emergency Procedures:**
- **Bypass Process**: Document emergency deployment steps
- **Rollback Plan**: Quick rollback via transport reversal
- **Contact List**: 24/7 approver contact information

---

## 📊 **Monitoring & Alerting**

### **Metrics to Track:**
- Time from transport creation to approval
- Approval success/rejection rates
- Deployment success rates
- Mean time to production (MTTP)

### **Alerts:**
- **Pending Approvals**: Alert after 2 hours
- **Failed Deployments**: Immediate notification
- **Long Wait Times**: Alert after 24 hours

---

## 🔧 **Troubleshooting**

### **Common Issues:**

**CTMS Approval Timeout:**
- Check TMS Cockpit for pending approvals
- Verify approver group configuration
- Test notification delivery

**GitHub Environment Issues:**
- Verify environment protection rules
- Check reviewer permissions
- Confirm branch restrictions

**API Errors:**
- Validate TMS credentials
- Check API endpoint availability
- Verify transport request format

### **Debug Commands:**
```bash
# Check transport status
curl -H "Authorization: Bearer $TOKEN" \
     "$TMS_URL/v2/transportRequests/$TRANSPORT_ID"

# Check environment protection
gh api repos/$REPO/environments/production
```

---

## 📞 **Support Contacts**

- **CTMS Issues**: SAP Support Portal
- **GitHub Issues**: GitHub Support
- **Internal Approvers**: [Your approval contact list]
- **Emergency Contacts**: [24/7 on-call information]