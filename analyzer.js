const fs = require('fs-extra');
const path = require('path');
const axios = require('axios');

// Configure Gemini API
const GEMINI_API_KEY = process.env.GEMINI_API_KEY; // Set this environment variable
// Log first few characters of API key for verification
console.log("API Key (first 4 chars):", GEMINI_API_KEY ? GEMINI_API_KEY.substring(0, 4) + "..." : "Not set");

// Updated to v1 (non-beta) endpoint
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite:generateContent';
// Configuration
const SKIP_DIRS = ['node_modules', 'dist', 'build', '.git', 'coverage'];
const FILE_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.php', '.rb', '.go', '.cs'];
const MAX_FILE_SIZE = 100000; // Maximum file size to analyze (100KB)

// Add function to test the API connection
async function testGeminiAPI() {
  try {
    console.log("Testing Gemini API connection...");
    console.log("Using API URL:", GEMINI_API_URL);
    console.log("API Key present:", GEMINI_API_KEY ? "Yes" : "No");
    
    const response = await axios.post(
      `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
      {
        contents: [
          {
            parts: [
              {
                text: "Hello, please respond with the text 'API connection successful' if you receive this message."
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 20
        }
      }
    );
    
    console.log("API test successful!");
    console.log("Response:", response.data.candidates[0].content.parts[0].text);
    return true;
  } catch (error) {
    console.error("API test failed with error:", error.message);
    
    // Log full error details
    if (error.response) {
      console.error("Error status:", error.response.status);
      console.error("Error data:", JSON.stringify(error.response.data, null, 2));
      console.error("Error headers:", JSON.stringify(error.response.headers, null, 2));
    }
    
    return false;
  }
}

// Simple function to guess file type based on path and content
function guessFileType(filePath, code) {
  if (filePath.includes('/controllers/') || filePath.includes('\\controllers\\')) {
    return "controller";
  } else if (filePath.includes('/models/') || filePath.includes('\\models\\')) {
    return "model";
  } else if (filePath.includes('/routes/') || filePath.includes('\\routes\\')) {
    return "route";
  } else if (filePath.includes('/utils/') || filePath.includes('\\utils\\')) {
    return "utility";
  } else if (filePath.includes('/middleware/') || filePath.includes('\\middleware\\') || 
             filePath.includes('/middlewares/') || filePath.includes('\\middlewares\\')) {
    return "middleware";
  } else if (code.includes('import React') || code.includes('React.') || 
             code.includes('useState') || filePath.endsWith('.jsx')) {
    return "component";
  } else if (code.includes('router.get') || code.includes('router.post')) {
    return "route";
  } else if (code.includes('mongoose.Schema') || code.includes('new Schema')) {
    return "model";
  } else if (code.includes('connectMongoDB') || code.includes('mongoose.connect')) {
    return "database";
  }
  
  return "utility";
}

async function analyzeCodeWithGemini(code, filePath) {
  try {
    // Extract file extension and name
    const ext = path.extname(filePath);
    const fileName = path.basename(filePath);
    
    // Create a simpler prompt focused on plain text response
    const prompt = `
Analyze this ${ext} file named "${fileName}".
Provide a comprehensive description of what this code does, including:

1. Main purpose and functionality
2. Key functions and their roles
3. Important data structures
4. External dependencies
5. How it interacts with other parts of the system

Code:
\`\`\`${ext}
${code}
\`\`\`

Give a detailed explanation in plain text format.
    `;

    // Call Gemini API
    const response = await axios.post(
      `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
      {
        contents: [
          {
            parts: [
              {
                text: prompt
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 2048
        }
      }
    );

    // Simply return the text response
    const analysisText = response.data.candidates[0].content.parts[0].text;
    
    return {
      fileName: fileName,
      filePath: filePath,
      fileType: guessFileType(filePath, code),
      analysis: analysisText
    };
  } catch (error) {
    console.error("LLM analysis error for file " + filePath + ":", error.message);
    if (error.response) {
      console.error("Response status:", error.response.status);
      console.error("Response data:", JSON.stringify(error.response.data, null, 2));
    }
    return { 
      fileName: path.basename(filePath),
      filePath,
      fileType: guessFileType(filePath, ""),
      analysis: "Error analyzing file: " + error.message
    };
  }
}

async function findFiles(rootDir) {
  const results = [];
  
  async function traverse(currentPath) {
    try {
      const entries = await fs.readdir(currentPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(currentPath, entry.name);
        
        if (entry.isDirectory()) {
          if (!SKIP_DIRS.includes(entry.name)) {
            await traverse(fullPath);
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name);
          if (FILE_EXTENSIONS.includes(ext)) {
            results.push(fullPath);
          }
        }
      }
    } catch (error) {
      console.error(`Error reading directory ${currentPath}:`, error.message);
    }
  }
  
  await traverse(rootDir);
  console.log(`Found ${results.length} files to analyze`);
  return results;
}

async function analyzeFile(filePath, outputDir) {
  try {
    console.log(`Analyzing: ${filePath}`);
    
    // Read the file
    const fileStats = await fs.stat(filePath);
    if (fileStats.size > MAX_FILE_SIZE) {
      console.log(`Skipping large file (${Math.round(fileStats.size/1024)}KB): ${filePath}`);
      return {
        fileName: path.basename(filePath),
        filePath,
        fileType: "skipped",
        analysis: "File too large to analyze",
        size: fileStats.size
      };
    }
    
    const code = await fs.readFile(filePath, 'utf-8');
    
    // Analyze the code using Gemini
    const analysis = await analyzeCodeWithGemini(code, filePath);
    
    // Create the output path
    const relativePath = path.relative(process.cwd(), filePath);
    const outputPath = path.join(
      outputDir, 
      `${relativePath.replace(/[\/\\]/g, '_')}_analysis.json`
    );
    
    // Ensure the output directory exists
    await fs.ensureDir(path.dirname(outputPath));
    
    // Write the result
    await fs.writeFile(outputPath, JSON.stringify(analysis, null, 2));
    console.log(`Saved analysis to: ${outputPath}`);
    
    return analysis;
  } catch (error) {
    console.error(`Error analyzing file ${filePath}:`, error.message);
    return {
      fileName: path.basename(filePath),
      filePath,
      error: error.message
    };
  }
}

async function generateMarkdownSummary(results, outputPath) {
  let markdown = `# Codebase Analysis Summary\n\n`;
  markdown += `Analysis completed on ${new Date().toLocaleString()}\n\n`;
  
  // Group files by type
  const filesByType = {};
  for (const result of results) {
    const fileType = result.fileType || 'unknown';
    if (!filesByType[fileType]) {
      filesByType[fileType] = [];
    }
    filesByType[fileType].push(result);
  }
  
  // Create table of contents
  markdown += `## Table of Contents\n\n`;
  Object.keys(filesByType).sort().forEach(type => {
    markdown += `- [${type.charAt(0).toUpperCase() + type.slice(1)}](#${type})\n`;
  });
  
  // Add sections for each file type
  for (const [type, files] of Object.entries(filesByType).sort()) {
    markdown += `\n\n## ${type.charAt(0).toUpperCase() + type.slice(1)}\n\n`;
    
    for (const file of files) {
      markdown += `### ${file.fileName}\n\n`;
      markdown += `**Path:** \`${file.filePath}\`\n\n`;
      
      if (file.analysis) {
        markdown += `**Analysis:**\n\n${file.analysis}\n\n`;
      }
      
      markdown += `---\n\n`;
    }
  }
  
  await fs.writeFile(outputPath, markdown);
}

async function main() {
  try {
    // Check if API key is set
    if (!GEMINI_API_KEY) {
      console.error('Error: GEMINI_API_KEY environment variable is not set');
      console.error('Please set the environment variable before running the script');
      process.exit(1);
    }
    
    // Test API connection first
    const apiTest = await testGeminiAPI();
    if (!apiTest) {
      console.error("API connection test failed. Please check your API key and endpoint.");
      process.exit(1);
    }
    
    // Get command line arguments
    const rootDir = process.argv[2] || '.';
    const outputDir = process.argv[3] || './gemini-analysis-output';
    
    console.log(`Starting analysis from: ${rootDir}`);
    console.log(`Results will be saved to: ${outputDir}`);
    
    // Ensure output directory exists
    await fs.ensureDir(outputDir);
    
    // Find all files to analyze
    const files = await findFiles(rootDir);
    
    // Analyze each file (with rate limiting to avoid API limits)
    const results = [];
    for (const file of files) {
      const result = await analyzeFile(file, outputDir);
      results.push(result);
      
      // Add a small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    // Save the overall summary
    const summaryPath = path.join(outputDir, '_summary.json');
    await fs.writeFile(summaryPath, JSON.stringify({
      totalFiles: files.length,
      analyzedFiles: results.length,
      results: results.map(r => ({
        fileName: r.fileName,
        filePath: r.filePath,
        fileType: r.fileType || 'unknown',
        hasError: r.analysis && r.analysis.startsWith('Error analyzing file')
      }))
    }, null, 2));
    
    // Generate a summary index file in markdown
    const markdownPath = path.join(outputDir, 'codebase_summary.md');
    await generateMarkdownSummary(results, markdownPath);
    
    console.log(`Analysis complete. Summary saved to: ${summaryPath}`);
    console.log(`Markdown summary saved to: ${markdownPath}`);
  } catch (error) {
    console.error('Analysis failed:', error.message);
  }
}

// Execute main function
main().catch(console.error);