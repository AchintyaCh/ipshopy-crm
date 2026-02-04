<div align="center" markdown="1">

<a href="https://github.com/shubh1199/ipshopy-crm">
    <img src="/assets/ipshopy-logo.png" height="80" alt="IP CRM Logo">
</a>

<h1>IP CRM</h1>

<strong>Simplify Sales, Amplify Relationships</strong>

<br/>

<sub>
A customized, production-ready CRM built on top of
<a href="https://github.com/frappe/crm" target="_blank">Frappe CRM</a>
</sub>

<br/><br/>

<div>
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/FrappeCRMHeroImage.png">
        <img width="1402" alt="IP CRM Dashboard" src=".github/screenshots/FrappeCRMHeroImage.png">
    </picture>
</div>

</div>

---

## IP CRM

**IP CRM** is a customized CRM solution built on the **Frappe Framework**, extending
Frappe CRM with business-specific workflows, telephony integrations, and UI
enhancements.

It is designed for internal teams and production use, focusing on:
- Faster sales operations
- Integrated calling workflows
- Clean, modern UI
- Easy deployment and scalability

---

## Motivation

IP CRM was created to solve real-world sales and communication challenges that
require more than an out-of-the-box CRM.

While **Frappe CRM** provides a solid and flexible foundation, IP CRM adds:
- Custom telephony integrations
- Tailored lead and deal workflows
- Enhanced frontend experience
- Production-ready configuration

The goal is to provide a CRM that teams can deploy quickly and adapt easily.

---

## Key Features

- **Modern & Custom UI**  
  Clean Vue-based frontend with business-specific enhancements.

- **All-in-One Lead & Deal Management**  
  Activities, calls, notes, and status tracking in a single view.

- **Telephony Integration**  
  Built-in and custom call handling with automatic call logs.

- **Kanban & Custom Views**  
  Visual deal tracking with drag-and-drop pipelines.

- **Extensible Architecture**  
  Built using Frappe Framework best practices.

---

## Integrations

- **TATA Telephony (Custom Integration)**  
  Deep integration for calling, logging, and agent workflows.

- **Twilio**  
  Make and receive calls with recording support.

- **Exotel**  
  Mobile-based calling for agents.

- **WhatsApp**  
  Messaging integration via Frappe WhatsApp.

- **ERPNext (Optional)**  
  Extend CRM with accounting and invoicing.

---

## Under the Hood

- **Frappe Framework**  
  https://github.com/frappe/frappe

- **Frappe UI (Vue.js)**  
  https://github.com/frappe/frappe-ui

---

## Compatibility

| IP CRM Branch | Stability | Frappe Version |
|--------------|----------|----------------|
| develop      | Stable   | v15 / v16     |

---

## Getting Started (Development)

### Local Setup

1. Install Bench  
   https://docs.frappe.io/framework/user/en/installation

2. Initialize Bench
   ```bash
   bench init my-bench
   cd my-bench
