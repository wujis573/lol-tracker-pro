"""Vercel Serverless 入口"""
from app.main import app, vercel_handler

# Vercel 使用 Mangum 将 ASGI 应用转换为 WSGI
handler = vercel_handler
