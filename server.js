const express = require('express');
const fileUpload = require('express-fileupload');
const cors = require('cors');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();
const { supabase } = require('./supabaseClient');

const app = express();
const PORT = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());
app.use(fileUpload());
app.use(express.static(path.join(__dirname, 'public')));

// Upload PDF and index it
app.post('/upload', async (req, res) => {
  try {
    if (!req.files || !req.files.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const file = req.files.file;
    const fileName = `${Date.now()}_${file.name}`;

    console.log(`Uploading ${fileName} to Supabase bucket: ${process.env.SUPABASE_BUCKET}`);

    // Upload to Supabase Storage
    const { data, error } = await supabase.storage
      .from(process.env.SUPABASE_BUCKET)
      .upload(fileName, file.data, {
        contentType: file.mimetype
      });

    if (error) {
      console.error('Supabase upload error:', error); // FULL error in Render logs
      return res.status(500).json({ error: error.message });
    }

    console.log('File uploaded successfully:', data);

    // After upload, run indexing
    const command = `python3 projects/index_faiss.py "${fileName}"`;
    exec(command, (err, stdout, stderr) => {
      if (err) {
        console.error('Error while building vector store:', stderr);
        return res.status(500).json({ error: 'Vector store creation failed' });
      }
      return res.json({ message: 'Upload and indexing complete', file: data });
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ error: error.message });
  }
});

// Handle user queries
app.post('/query', (req, res) => {
  const question = req.body.question;
  if (!question) {
    return res.status(400).json({ error: 'No question provided' });
  }

  const command = `python3 projects/run_gemini.py "${question}"`;
  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error('Error during query execution:', stderr);
      return res.status(500).json({ error: 'Query failed' });
    }
    return res.json({ response: stdout.trim() });
  });
});

// Serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
