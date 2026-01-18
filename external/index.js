const express = require("express");
const app = express();
const port = 8002;

// Middleware to parse JSON bodies
app.use(express.json());

// Sample External API endpoint
app.post("/post", (req, res) => {
    const authHeader = req.headers.authorization;
    
    console.log(`[${new Date().toISOString()}] Received request on /post`);
    console.log("Headers:", req.headers);
    console.log("Payload:", req.body);

    // Simple Bearer token check
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        console.warn("Unauthorized request: Missing or invalid Authorization header");
        return res.status(401).json({ error: "Unauthorized" });
    }

    const token = authHeader.split(" ")[1];
    // In a real app, you'd verify this token
    console.log(`Used Token: ${token}`);

    res.json({
        status: "success",
        message: "Content successfully posted to Sample External API",
        received_at: new Date().toISOString(),
        received_content: req.body.content
    });
});

app.listen(port, () => {
    console.log(`Sample External API listening on port ${port}`);
    console.log(`Post endpoint: http://localhost:${port}/post`);
});