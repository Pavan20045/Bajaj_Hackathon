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

// Upload PDF to Supabase and index it
app.post('/upload', async (req, res) => {
  try {
    if (!req.files || !req.files.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const file = req.files.file;
    const bucketName = 'pdf-bucket'; // Change to your Supabase bucket name
    const filePath = `uploads/${Date.now()}_${file.name}`;

    // Upload file to Supabase
    const { data, error } = await supabase.storage
      .from(bucketName)
      .upload(filePath, file.data, { contentType: file.mimetype });

    if (error) {
      console.error('Supabase upload error:', error.message);
      return res.status(500).json({ error: 'File upload to Supabase failed' });
    }

    // Get the public URL
    const { data: publicUrlData } = supabase.storage
      .from(bucketName)
      .getPublicUrl(filePath);

    const fileUrl = publicUrlData.publicUrl;
    console.log(`File uploaded to Supabase: ${fileUrl}`);

    // Run Python indexing script with the file URL
    const command = `python3 projects/index_faiss.py "${fileUrl}"`;
    exec(command, (err, stdout, stderr) => {
      if (err) {
        console.error('Error while building vector store:', stderr);
        return res.status(500).json({ error: 'Vector store creation failed' });
      }
      return res.json({ message: 'Upload and indexing complete', fileUrl });
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ error: 'Upload failed' });
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
