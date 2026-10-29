<div align="center">

# 🛡️ VeriSafe

### DETECT . DECODE . DEFEND .

**An explainable fraud and phishing analysis platform powered by intelligent detection.**

Helping people recognize suspicious messages, investigate potentially malicious URLs, understand security risks, and make safer digital decisions.

<br/>

![Project](https://img.shields.io/badge/Project-VeriSafe-00BFA6?style=for-the-badge)
![Category](https://img.shields.io/badge/Domain-AI%20%26%20Cybersecurity-635BFF?style=for-the-badge)
![Team](https://img.shields.io/badge/Team-Shadow%20Paradox-111827?style=for-the-badge)

</div>

---

## 📌 Overview

**VeriSafe** is a cybersecurity platform designed to help users assess suspicious messages and URLs through evidence-based analysis and understandable risk explanations.

Digital scams often rely on urgency, impersonation, misleading links, and requests for sensitive information. VeriSafe aims to make these warning signs easier to recognize by bringing message analysis, URL inspection, and practical safety recommendations into one accessible platform.

Rather than relying solely on a simple safe-or-dangerous label, VeriSafe focuses on explaining **what looks suspicious, why it matters, and what the user can do next.**

## 🎯 The Problem

People encounter potentially dangerous digital communications across email, SMS, messaging applications, and websites.

Common warning signs include:

- 🚨 Urgent or threatening messages designed to pressure recipients.
- 🎭 Impersonation of trusted organizations or individuals.
- 🔗 Misleading domains and suspicious URLs.
- 🔑 Requests for passwords, OTPs, or other sensitive information.
- 💸 Unexpected payment requests and suspicious financial instructions.

Recognizing these indicators can be challenging without technical knowledge or dedicated security tools.

## 💡 Our Solution

VeriSafe provides an accessible workflow for analyzing suspicious messages and URLs.

1. **Submit:** Enter a suspicious message or URL.
2. **Analyze:** Examine relevant patterns and potential warning signs.
3. **Understand:** Review the indicators and explanations behind the assessment.
4. **Act Safely:** Follow practical recommendations and independently verify important requests.

The objective is to help users make more informed decisions without presenting automated assessments as infallible security verdicts.

## ✨ Core Features

### 📩 1. Suspicious Message Analysis

Examine messages for potential warning signs, including:

- Urgent or threatening language.
- Requests for passwords, OTPs, or sensitive information.
- Suspicious payment instructions.
- Possible impersonation indicators.
- Embedded links that warrant further inspection.

### 🔗 2. URL Risk Analysis

Inspect URL characteristics to identify potentially suspicious patterns, such as:

- Misleading domain names and subdomains.
- Unusual URL structures and encoding.
- Patterns commonly associated with phishing attempts.
- Other indicators that may warrant additional verification.

### 🔍 3. Explainable Risk Assessment

Provide understandable analysis results instead of an unexplained verdict.

The proposed classification system includes:

| Classification | Meaning |
|---|---|
| 🟢 **Low** | Few suspicious indicators were identified by the available checks. |
| 🟡 **Medium** | Some suspicious indicators require attention. |
| 🔴 **High** | Multiple or significant warning signs were identified. |
| ⚪ **Needs Review** | The available evidence is insufficient or inconclusive. |

These categories represent an assessment of available indicators, not a guarantee that a message or URL is safe or malicious.

### 🛡️ 4. Actionable Safety Recommendations

Help users respond more safely to suspicious communications by recommending steps such as:

- Verify the sender through an independently obtained official contact channel.
- Avoid sharing passwords, OTPs, or sensitive information in response to unexpected requests.
- Navigate to official websites directly rather than following suspicious links.
- Seek further verification when the available evidence is inconclusive.

### 🧩 5. Modular Architecture

Separate the user interface, API, and detection logic to support maintainability, testing, and future enhancements.

### 🚀 6. Extensible Design

The architecture can support future additions such as investigation history, case management, reviewer feedback, and trusted threat-intelligence integrations.

These extensions should be introduced when they provide measurable value and can be implemented safely.

## 🏗️ System Architecture

VeriSafe separates the frontend from the detection engine.

```text
┌──────────────────────────────────────┐
│                 USER                 │
│        Message or URL submission     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│               FRONTEND               │
│          React + TypeScript          │
│                                      │
│  Input Forms • Results • Explanations│
└──────────────────┬───────────────────┘
                   │
                   │ REST API / JSON
                   ▼
┌──────────────────────────────────────┐
│                BACKEND               │
│              Python + FastAPI        │
│                                      │
│     Validation • API • Services      │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│           DETECTION ENGINE           │
│                                      │
│  Message Analysis • URL Inspection   │
│       Evidence • Risk Assessment     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│           ANALYSIS RESULTS           │
│                                      │
│  Risk Category • Evidence • Guidance │
└──────────────────────────────────────┘
```

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Programming Language | TypeScript |
| Styling | Tailwind CSS |
| Backend | Python |
| API Framework | FastAPI |
| Data Validation | Pydantic |
| API Communication | REST API with JSON |
| Version Control | Git and GitHub |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |

The initial version does not require a database. Persistent storage can be introduced if investigation history or case management becomes necessary.

## 📁 Project Structure

```text
VeriSafe/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       ├── types/
│       ├── utils/
│       ├── App.tsx
│       ├── main.tsx
│       └── index.css
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       ├── core/
│       ├── detection/
│       ├── schemas/
│       ├── services/
│       └── main.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── TESTING.md
│
├── .gitignore
├── README.md
└── LICENSE
```

This structure defines the intended organization of the project; the directory and file contents should be added as implementation proceeds.

## 🔌 API Design

The backend is organized around dedicated endpoints for message analysis, URL analysis, and service health.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check backend availability. |
| `POST` | `/api/messages/analyze` | Analyze a submitted message. |
| `POST` | `/api/urls/analyze` | Analyze a submitted URL. |

The frontend communicates with the backend using JSON requests and responses.

API behavior, validation rules, response schemas, and error formats should be documented and tested as the implementation evolves.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or a compatible version.
- Node.js and npm.
- Git.
- A code editor such as Visual Studio Code.

### 1. Clone the repository

```bash
git clone https://github.com/brosploit/VeriSafe.git
cd VeriSafe
```

### 2. Set up the backend

```bash
cd backend
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies after the project's `requirements.txt` has been created:

```bash
pip install -r requirements.txt
```

Start the API after the application entry point is implemented:

```bash
uvicorn app.main:app --reload
```

The local API address is typically:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is typically available at:

```text
http://127.0.0.1:8000/docs
```

### 3. Set up the frontend

Open a separate terminal:

```bash
cd frontend
npm install
```

Start the development server after the frontend project files have been created:

```bash
npm run dev
```

Vite will display the local address for the frontend.

**Note:** These commands assume the project files, dependency manifests, and application entry points have been implemented. They will not run successfully until those files exist.

## 👥 Team

### Shadow Paradox

**Project:** VeriSafe

**Domain:** Artificial Intelligence & Cybersecurity

We aim to build practical technology that makes digital security easier to understand and helps users make better-informed decisions.

## 🗺️ Project Roadmap

- [ ] Establish the shared repository and development workflow.
- [ ] Implement the backend API and request validation.
- [ ] Develop the message-analysis engine.
- [ ] Develop the URL-analysis engine.
- [ ] Build the responsive frontend.
- [ ] Integrate the frontend with the backend.
- [ ] Test detection behavior and edge cases.
- [ ] Add appropriate error handling and security controls.
- [ ] Deploy the application.
- [ ] Validate the complete user workflow.
- [ ] Prepare the hackathon demonstration.

## 🔐 Security & Responsible Use

VeriSafe is intended to support security awareness and preliminary analysis.

- **No absolute guarantees:** Automated analysis can produce false positives and false negatives.
- **Human judgment matters:** Users should independently verify consequential requests.
- **Protect sensitive information:** Avoid submitting confidential messages or personal information unless appropriate safeguards are in place.
- **Handle URLs carefully:** URL analysis should use safe validation and avoid automatically visiting arbitrary user-submitted destinations from the backend.
- **Protect credentials:** API keys, secrets, and private configuration must not be committed to the repository.
- **Explain uncertainty:** Inconclusive results should be identified rather than presented as definitive verdicts.

## 🤝 Contributing

Contributions are welcome as the project develops.

1. Fork the repository or create a feature branch.
2. Make focused changes.
3. Test your changes.
4. Open a pull request describing what changed and why.

For team development, coordinate changes through Git branches and pull requests to reduce conflicts.

## 📄 License

The project's license should be selected and added to the repository before others are granted permission to reuse, modify, or distribute the code.

---

<div align="center">

### 🛡️ VeriSafe — Detect. Understand. Verify.

**Built by Shadow Paradox**

*Making digital security more understandable, one assessment at a time.*

</div>
