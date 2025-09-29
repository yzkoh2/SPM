const express = require('express');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const app = express();

// Load the unified documentation
const swaggerDocPath = path.join(__dirname, 'swaggerJson', 'documentation.json');

try {
  // Check if the documentation file exists
  if (fs.existsSync(swaggerDocPath)) {
    const swaggerDocument = require(swaggerDocPath);
    
    // Serve the unified API documentation
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, {
      explorer: true,
      customCss: '.swagger-ui .topbar { display: none }',
      customSiteTitle: "SPM API Documentation",
      swaggerOptions: {
        filter: true,
        displayRequestDuration: true
      }
    }));
    
    console.log('✅ Unified API documentation loaded successfully');
    console.log('📖 Documentation available at: http://localhost:6008/api-docs');
  } else {
    console.error('❌ Documentation file not found at:', swaggerDocPath);
    
    // Serve a simple error page
    app.get('/api-docs', (req, res) => {
      res.status(404).send(`
        <h1>Documentation Not Found</h1>
        <p>Please ensure the documentation.json file exists in the swaggerJson directory.</p>
        <p>Expected location: ${swaggerDocPath}</p>
      `);
    });
  }
} catch (error) {
  console.error('❌ Error loading documentation:', error.message);
  
  // Serve an error page
  app.get('/api-docs', (req, res) => {
    res.status(500).send(`
      <h1>Documentation Error</h1>
      <p>Error loading documentation: ${error.message}</p>
    `);
  });
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'swagger-documentation',
    timestamp: new Date().toISOString()
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'SPM API Documentation Server',
    documentation: '/api-docs',
    health: '/health'
  });
});

const port = process.env.PORT || 6008;
app.listen(port, () => {
  console.log(`🚀 Swagger documentation server running on port ${port}`);
  console.log(`📋 Available endpoints:`);
  console.log(`   - Documentation: http://localhost:${port}/api-docs`);
  console.log(`   - Health Check:  http://localhost:${port}/health`);
  console.log(`   - Root:          http://localhost:${port}/`);
});