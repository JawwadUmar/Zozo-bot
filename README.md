# 🤖 Zozo-bot — LinkedIn Easy Apply Automation

Zozo-bot is an intelligent automation bot that applies to LinkedIn jobs on your behalf using **Playwright** for browser automation and **Groq LLM** for AI-powered form filling. It handles multi-step Easy Apply forms, skips already-applied listings, fills out questions intelligently using your resume, and submits applications automatically.

---

## ✨ Features

- 🔐 **Automated LinkedIn login** — securely logs in using your credentials
- 📋 **Job listing iteration** — scans all job cards on a search results page and skips already-applied ones
- 📝 **Smart form filling** — handles multi-step Easy Apply forms including:
  - Phone number
  - Resume section
  - Work authorization (radio buttons)
  - Additional questions (text inputs, dropdowns, radio buttons)
- 🤖 **AI-powered answers** — uses Groq LLM to intelligently answer application questions based on your resume
- 🧠 **Human-like behavior** — randomized delays and typing patterns to avoid detection
- 🔁 **Single job & search page support** — works on both individual job pages and LinkedIn search results

---

## 🗂️ Project Structure

```
Zozo-bot/
├── main.py                    # Entry point
├── sample.env                 # Environment variable template
├── requirements.txt           # Python dependencies
├── data/
│   ├── resume.txt             # Your resume (plain text)
│   ├── system_prompt.txt      # LLM system prompt with answering rules
│   └── human_prompt.txt       # LLM human prompt template
└── app/
    ├── ai/
    │   ├── llm.py             # Groq LLM initialization
    │   └── ai_answer.py       # AI answer generation logic
    ├── bot/
    │   ├── bot_runner.py      # Main bot orchestration
    │   ├── handle_login.py    # LinkedIn login handler
    │   ├── click_easy_apply.py# Clicks the Easy Apply button
    │   ├── fill_form.py       # Multi-step form filling logic
    │   └── click_buttons.py   # Next / Review / Submit button handlers
    ├── config/
    │   └── config.py          # Loads environment variables
    └── utils/
        ├── file_loader.py     # Reads resume and prompt files
        └── human.py           # Human-like delay and typing utilities
```

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Zozo-bot.git
cd Zozo-bot
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

### 5. Configure Environment Variables

Copy the sample env file and fill in your details:

```bash
cp sample.env .env
```

Edit `.env` with your credentials:

```env
LINKEDIN_EMAIL="youremail@email.com"
LINKEDIN_PASSWORD="your_linkedin_password"
LINKEDIN_JOB_LINK="https://www.linkedin.com/jobs/search/?f_AL=true&keywords=your+job+title"
PHONE_NUMBER="your_phone_number"
```

> **Note:** You also need a `GROQ_API_KEY` in your `.env` for the LLM. Get one free at [console.groq.com](https://console.groq.com).

```env
GROQ_API_KEY="your_groq_api_key"
```

### 6. Add Your Resume

Create `data/resume.txt` and paste your resume as plain text. The bot uses it to answer resume-related application questions.

---

## 🚀 Running the Bot

```bash
python main.py
```

The bot will:
1. Launch a Chromium browser window
2. Log in to LinkedIn
3. Navigate to your configured job search URL
4. Iterate through all job listings, skipping already-applied ones
5. Click **Easy Apply**, fill the form step-by-step, and submit

> Press `Ctrl+C` at any time to stop the bot. The browser stays open for manual inspection.

---

## 🔧 Configuration & Customization

### Job Search Link

Set `LINKEDIN_JOB_LINK` in `.env` to any LinkedIn job search URL. To filter for Easy Apply jobs posted in the last 24 hours:

```
https://www.linkedin.com/jobs/search/?f_AL=true&f_TPR=r86400&keywords=software+engineer&sortBy=DD
```

### AI Answering Rules

Edit `data/system_prompt.txt` to customize how the LLM answers questions:
- Default experience years
- Salary expectations
- Notice period
- Self-rating scale
- Openness to relocation, shifts, etc.

### Human Prompt Template

Edit `data/human_prompt.txt` to adjust the prompt format sent to the LLM for each question.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `playwright` | Browser automation |
| `langchain-groq` | Groq LLM integration |
| `langchain-core` | LangChain prompt templates |
| `python-dotenv` | Environment variable loading |

---

## ⚠️ Disclaimer

This bot is intended for **personal use only** to automate repetitive job applications. Use responsibly and in accordance with [LinkedIn's Terms of Service](https://www.linkedin.com/legal/user-agreement). Automated activity on LinkedIn may result in account restrictions.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
