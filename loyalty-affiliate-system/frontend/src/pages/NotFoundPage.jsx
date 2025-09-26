import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300">404</h1>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Page not found</h2>
        <p className="text-gray-600 mb-8">
          Sorry, we couldn't find the page you're looking for.
        </p>
        <div className="space-y-4">
          <Link to="/">
            <Button className="w-full">
              <Home className="h-5 w-5 mr-2" />
              Go back home
            </Button>
          </Link>
          <button
            onClick={() => window.history.back()}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Go back
          </button>
        </div>
      </Card>
    </div>
  )
}

export default NotFoundPage