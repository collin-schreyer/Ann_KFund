# Deploy K Fund Allocation Tool to Render

## Quick Deploy

1. **Create a Render account** at https://render.com

2. **Fork or push this repo** to GitHub

3. **Create a new Web Service** on Render:
   - Connect your GitHub repo
   - Select the `prototype` directory as root
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt && python ingest_documents.py`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** in Render dashboard:
   ```
   OPENAI_API_KEY=sk-your-key-here
   EMBEDDING_MODEL=text-embedding-3-small
   LLM_MODEL=gpt-4-turbo-preview
   ```

5. **Deploy** - Render will build and deploy automatically

## Your Shareable URL

After deployment, your app will be available at:
```
https://your-app-name.onrender.com
```

Share this URL with your team!

## Pages

- `/` or `/index.html` - Home page
- `/search.html` - Search K Fund guidelines
- `/allocation.html` - Event allocation tool
- `/api/v1/health` - API health check

## Local Development

```bash
cd prototype
pip install -r requirements.txt
python ingest_documents.py  # First time only
python api_server.py
```

Then open http://localhost:8002

## Notes

- The free tier on Render may spin down after inactivity (first request takes ~30s)
- For production, upgrade to a paid plan for always-on service
- ChromaDB data is ephemeral on Render free tier - documents are re-ingested on each deploy
