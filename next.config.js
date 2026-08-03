/** @type {import('next').NextConfig} */
const nextConfig = {
  // In development the Flask app runs separately on 5328. In production Vercel
  // routes /api/* into the Python function itself (see vercel.json), so no
  // rewrite is needed — and the previous one dropped the path, sending
  // /api/chat to a route Flask does not serve.
  rewrites: async () =>
    process.env.NODE_ENV === 'development'
      ? [
          {
            source: '/api/:path*',
            destination: 'http://127.0.0.1:5328/api/:path*',
          },
        ]
      : [],
}

module.exports = nextConfig
