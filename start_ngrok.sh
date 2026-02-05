#!/bin/bash
# Start ngrok tunnel for Quest VR access

echo "Starting ngrok tunnel on port 8503..."
ngrok http 8503 --log=stdout
