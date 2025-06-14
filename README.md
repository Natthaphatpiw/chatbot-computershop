# Next.js Chat Interface with Product Management

A modern web application built with Next.js that features a chat interface and product management system. The application includes a responsive design, dark/light theme support, and various interactive features.

## Features

- 💬 Interactive chat interface with suggested questions
- 🎨 Dark/Light theme support
- 🔍 Product search functionality
- 📱 Responsive design for all devices
- 📝 Markdown support in chat messages
- 🛍️ Product management system
- 🔄 Real-time updates
- 📦 Pagination for product listings
- 📋 Clipboard copy functionality
- ⚡ Fast and optimized performance

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- MongoDB (for data storage)
- React Icons
- React Markdown

## Getting Started

### Prerequisites

- Node.js 18.0 or later
- npm or yarn
- MongoDB (optional, can use mock data)

### Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [your-project-name]
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env.local` file in the root directory and add your environment variables:
```env
MONGODB_URI=your_mongodb_connection_string
```

4. Run the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
├── app/
│   ├── api/           # API routes
│   ├── chat/          # Chat interface components
│   ├── products/      # Product management
│   └── layout.tsx     # Root layout
├── components/        # Reusable components
├── lib/              # Utility functions
├── public/           # Static assets
└── types/            # TypeScript type definitions
```

## Features in Detail

### Chat Interface
- Real-time message updates
- Suggested questions for quick interaction
- Markdown support for rich text formatting
- Message history tracking

### Product Management
- Product listing with pagination
- Search functionality
- Product details modal
- Category-based filtering

### Theme Support
- Automatic theme detection
- Manual theme toggle
- Persistent theme preference

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Next.js team for the amazing framework
- Tailwind CSS for the utility-first CSS framework
- All contributors who have helped shape this project 