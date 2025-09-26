import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Plus, Edit, Trash2, MessageSquare, Copy, Eye } from 'lucide-react'
import { whatsappAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Input from '../ui/Input'

const TemplateManager = () => {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('all')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    watch
  } = useForm()

  const categories = [
    'all',
    'welcome',
    'birthday',
    'loyalty',
    'promotion',
    'bill',
    'affiliate'
  ]

  useEffect(() => {
    fetchTemplates()
  }, [selectedCategory])

  const fetchTemplates = async () => {
    try {
      setLoading(true)
      let category = null
      if (selectedCategory !== 'all') {
        category = selectedCategory.toUpperCase()
      }

      const response = await whatsappAPI.getTemplates(category)
      setTemplates(response)
    } catch (err) {
      setError('Failed to fetch templates')
      console.error('Error fetching templates:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTemplate = async (data) => {
    try {
      await whatsappAPI.createTemplate({
        name: data.name,
        category: data.category.toUpperCase(),
        content: data.content,
        variables: data.variables ? data.variables.split(',').map(v => v.trim()) : [],
        message_type: data.message_type || 'text',
        media_url: data.media_url || null
      })

      setShowCreateForm(false)
      reset()
      fetchTemplates()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create template')
    }
  }

  const handleUpdateTemplate = async (data) => {
    try {
      await whatsappAPI.updateTemplate(editingTemplate.id, {
        name: data.name,
        content: data.content,
        category: data.category.toUpperCase(),
        variables: data.variables ? data.variables.split(',').map(v => v.trim()) : [],
        message_type: data.message_type || 'text',
        media_url: data.media_url || null
      })

      setEditingTemplate(null)
      reset()
      fetchTemplates()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update template')
    }
  }

  const handleDeleteTemplate = async (templateId) => {
    if (!confirm('Are you sure you want to delete this template?')) return

    try {
      await whatsappAPI.deleteTemplate(templateId)
      fetchTemplates()
    } catch (err) {
      setError('Failed to delete template')
    }
  }

  const copyTemplateContent = (content) => {
    navigator.clipboard.writeText(content)
    // You could add a toast notification here
  }

  const previewTemplate = (template) => {
    const preview = template.content.replace(/\{\{(\w+)\}\}/g, (match, variable) => {
      return `[${variable.toUpperCase()}]`
    })
    alert(`Template Preview:\n\n${preview}`)
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'welcome': return 'bg-green-100 text-green-800'
      case 'birthday': return 'bg-pink-100 text-pink-800'
      case 'loyalty': return 'bg-blue-100 text-blue-800'
      case 'promotion': return 'bg-purple-100 text-purple-800'
      case 'bill': return 'bg-yellow-100 text-yellow-800'
      case 'affiliate': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-danger-600">
          <p>{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchTemplates}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">WhatsApp Templates</h3>
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Template
          </Button>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1 text-sm rounded-full transition-colors ${
                selectedCategory === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>

        {/* Create/Edit Form */}
        {(showCreateForm || editingTemplate) && (
          <Card className="p-4 mb-6 border-2 border-primary-200">
            <h4 className="text-md font-medium text-gray-900 mb-4">
              {editingTemplate ? 'Edit Template' : 'Create New Template'}
            </h4>

            <form onSubmit={handleSubmit(editingTemplate ? handleUpdateTemplate : handleCreateTemplate)}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Template Name"
                  {...register('name', { required: 'Template name is required' })}
                  error={errors.name?.message}
                  placeholder="e.g., welcome_message"
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    {...register('category', { required: 'Category is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select category</option>
                    <option value="welcome">Welcome</option>
                    <option value="birthday">Birthday</option>
                    <option value="loyalty">Loyalty</option>
                    <option value="promotion">Promotion</option>
                    <option value="bill">Bill</option>
                    <option value="affiliate">Affiliate</option>
                  </select>
                  {errors.category && (
                    <p className="text-sm text-danger-600 mt-1">{errors.category.message}</p>
                  )}
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message Content
                </label>
                <textarea
                  {...register('content', { required: 'Content is required' })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter message content with {{variables}} for dynamic content"
                />
                {errors.content && (
                  <p className="text-sm text-danger-600 mt-1">{errors.content.message}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Use {{'{{variable_name}}'}} for dynamic content (e.g., {{'{{name}}'}}, {{'{{points}}'}})
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <Input
                  label="Variables (comma-separated)"
                  {...register('variables')}
                  placeholder="name, points, tier"
                />

                <Input
                  label="Media URL (optional)"
                  {...register('media_url')}
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateForm(false)
                    setEditingTemplate(null)
                    reset()
                  }}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {editingTemplate ? 'Update' : 'Create'} Template
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Templates List */}
        <div className="space-y-4">
          {templates.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No templates found</p>
              <p className="text-sm text-gray-400 mt-1">
                {selectedCategory === 'all' ? 'Create your first template to get started' : `No templates in ${selectedCategory} category`}
              </p>
            </div>
          ) : (
            templates.map(template => (
              <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(template.category)}`}>
                        {template.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        Used {template.usage_count} times
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{template.content}</p>
                    {template.variables.length > 0 && (
                      <div className="text-xs text-blue-600">
                        Variables: {template.variables.join(', ')}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => previewTemplate(template)}
                    >
                      <Eye className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyTemplateContent(template.content)}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingTemplate(template)
                        reset({
                          name: template.name,
                          category: template.category,
                          content: template.content,
                          variables: template.variables.join(', '),
                          message_type: template.message_type,
                          media_url: template.media_url
                        })
                      }}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteTemplate(template.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>

                {template.last_used && (
                  <div className="text-xs text-gray-500">
                    Last used: {new Date(template.last_used).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}

export default TemplateManager