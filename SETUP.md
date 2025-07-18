## 🚀 Setup Instructions

This project lets you interact with GitHub (summarize repos, issues, PRs, etc.) via SMS using Twilio and OpenAI.

---

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/git-sms.git
cd git-sms
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a file named `.env` in the project root and add your credentials:

```env

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# GitHub authentication (optional, read-only)
# Only public read-only access is supported; write operations are disabled.
```

---

### 4. Run the Server

```bash
uvicorn main:app --reload
```

Your server will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 5. Expose with ngrok

In a separate terminal window:

```bash
ngrok http 8000
```

Copy the HTTPS URL it provides (e.g., `https://abc123.ngrok.io`).

---

### 6. Configure Twilio Webhook

1. Go to your [Twilio Console](https://console.twilio.com/)
2. Navigate to your **Phone Number > Messaging > Webhook**
3. Set the webhook URL to:

```
https://abc123.ngrok.io/webhook
```

4. Set the method to `POST`

---

### ✅ Done

Try texting your Twilio number with:

```text
help
summarize github/github
summarize owner/repo issue 123
```

Let the bots do the rest.
