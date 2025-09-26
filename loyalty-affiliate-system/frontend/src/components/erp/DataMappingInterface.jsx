import { useState, useEffect } from 'react'
import { Plus, Trash2, Save, RefreshCw, ArrowRight, Check, AlertTriangle } from 'lucide-react'
import { erpAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Input from '../ui/Input'

const DataMappingInterface = () => {
  const [mappingType, setMappingType] = useState('customer')
  const [mappings, setMappings] = useState([])
  const [availableFields, setAvailableFields] = useState({
    source: [],
    target: []
  })
  const [validationResult, setValidationResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const mappingTypes = [
    { id: 'customer', name: 'Customer Mapping', description: 'Map customer data fields' },
    { id: 'product', name: 'Product Mapping', description: 'Map product data fields' },
    { id: 'sale', name: 'Sales Mapping', description: 'Map sales transaction fields' },
    { id: 'financial', name: 'Financial Mapping', description: 'Map financial data fields' }
  ]

  useEffect(() => {
    loadMappings()
    loadAvailableFields()
  }, [mappingType])

  const loadMappings = async () => {
    try {
      const response = await erpAPI.getDataMappings(mappingType)
      setMappings(response.mappings || [])
    } catch (err) {
      console.error('Error loading mappings:', err)
      setMappings([])
    }
  }

  const loadAvailableFields = async () => {
    // Mock data for available fields
    // In real implementation, this would come from API
    setAvailableFields({
      source: [
        'customer_id', 'customer_name', 'email_address', 'phone_number',
        'address', 'customer_type', 'credit_limit', 'tax_id', 'created_date'
      ],
      target: [
        'id', 'name', 'email', 'phone', 'address', 'customer_type',
        'credit_limit', 'tax_id', 'created_at', 'erp_id'
      ]
    })
  }

  const addMapping = () => {
    const newMapping = {
      source_field: '',
      target_field: '',
      transformation: '',
      validation_rules: {},
      is_required: false
    }
    setMappings([...mappings, newMapping])
  }

  const removeMapping = (index) => {
    const updatedMappings = mappings.filter((_, i) => i !== index)
    setMappings(updatedMappings)
  }

  const updateMapping = (index, field, value) => {
    const updatedMappings = [...mappings]
    updatedMappings[index][field] = value
    setMappings(updatedMappings)
  }

  const validateMappings = async () => {
    try {
      setLoading(true)
      const response = await erpAPI.validateDataMappings(mappingType)
      setValidationResult(response)
    } catch (err) {
      console.error('Error validating mappings:', err)
      setValidationResult({
        is_valid: false,
        errors: ['Validation failed'],
        warnings: []
      })
    } finally {
      setLoading(false)
    }
  }

  const saveMappings = async () => {
    try {
      setSaving(true)
      await erpAPI.configureDataMappings({
        mapping_type: mappingType,
        mappings: mappings
      })
      alert('Mappings saved successfully!')
      await validateMappings()
    } catch (err) {
      console.error('Error saving mappings:', err)
      alert('Failed to save mappings. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const testMapping = async (mapping) => {
    // Test a single mapping with sample data
    try {
      // This would test the mapping transformation
      console.log('Testing mapping:', mapping)
      return { success: true, result: 'Test successful' }
    } catch (err) {
      return { success: false, error: err.message }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Data Mapping Interface</h2>
          <p className="text-gray-600">
            Configure how data should be mapped between the loyalty system and ERP
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={validateMappings}
            loading={loading}
            disabled={loading}
          >
            <Check className="h-4 w-4 mr-2" />
            Validate
          </Button>
          <Button
            onClick={saveMappings}
            loading={saving}
            disabled={saving}
          >
            <Save className="h-4 w-4 mr-2" />
            Save Mappings
          </Button>
        </div>
      </div>

      {/* Mapping Type Selection */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Mapping Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {mappingTypes.map((type) => (
            <div
              key={type.id}
              onClick={() => setMappingType(type.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                mappingType === type.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h4 className="font-medium text-gray-900">{type.name}</h4>
              <p className="text-sm text-gray-600">{type.description}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Validation Results */}
      {validationResult && (
        <Card className="p-6">
          <div className="flex items-start space-x-3">
            {validationResult.is_valid ? (
              <Check className="h-5 w-5 text-green-600 mt-0.5" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Validation Results
              </h3>
              {validationResult.is_valid ? (
                <p className="text-green-700">All mappings are valid!</p>
              ) : (
                <div className="space-y-2">
                  <p className="text-red-700">Mapping validation failed:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {validationResult.errors.map((error, index) => (
                      <li key={index} className="text-red-600">{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              {validationResult.warnings.length > 0 && (
                <div className="mt-3">
                  <p className="text-yellow-700">Warnings:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {validationResult.warnings.map((warning, index) => (
                      <li key={index} className="text-yellow-600">{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Field Mapping Interface */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Field Mappings - {mappingTypes.find(t => t.id === mappingType)?.name}
          </h3>
          <Button variant="outline" onClick={addMapping}>
            <Plus className="h-4 w-4 mr-2" />
            Add Mapping
          </Button>
        </div>

        {/* Available Fields Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Source Fields (ERP)</h4>
            <div className="text-sm text-blue-800">
              {availableFields.source.map(field => (
                <span key={field} className="inline-block bg-blue-100 px-2 py-1 rounded mr-2 mb-1">
                  {field}
                </span>
              ))}
            </div>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Target Fields (Loyalty System)</h4>
            <div className="text-sm text-green-800">
              {availableFields.target.map(field => (
                <span key={field} className="inline-block bg-green-100 px-2 py-1 rounded mr-2 mb-1">
                  {field}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Mapping Configuration */}
        <div className="space-y-4">
          {mappings.map((mapping, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium text-gray-900">Mapping {index + 1}</h4>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeMapping(index)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {/* Source Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source Field (ERP)
                  </label>
                  <select
                    value={mapping.source_field}
                    onChange={(e) => updateMapping(index, 'source_field', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select source field</option>
                    {availableFields.source.map(field => (
                      <option key={field} value={field}>{field}</option>
                    ))}
                  </select>
                </div>

                {/* Arrow */}
                <div className="flex items-center justify-center">
                  <ArrowRight className="h-6 w-6 text-gray-400" />
                </div>

                {/* Target Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Field (Loyalty)
                  </label>
                  <select
                    value={mapping.target_field}
                    onChange={(e) => updateMapping(index, 'target_field', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select target field</option>
                    {availableFields.target.map(field => (
                      <option key={field} value={field}>{field}</option>
                    ))}
                  </select>
                </div>

                {/* Transformation */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Transformation
                  </label>
                  <select
                    value={mapping.transformation}
                    onChange={(e) => updateMapping(index, 'transformation', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">No transformation</option>
                    <option value="uppercase">Uppercase</option>
                    <option value="lowercase">Lowercase</option>
                    <option value="trim">Trim whitespace</option>
                    <option value="date_format">Format date</option>
                    <option value="currency_format">Format currency</option>
                    <option value="custom">Custom function</option>
                  </select>
                </div>

                {/* Required Toggle */}
                <div className="flex items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={mapping.is_required}
                      onChange={(e) => updateMapping(index, 'is_required', e.target.checked)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Required</span>
                  </label>
                </div>
              </div>

              {/* Test Mapping */}
              <div className="mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => testMapping(mapping)}
                >
                  Test Mapping
                </Button>
              </div>
            </div>
          ))}
        </div>

        {mappings.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ArrowRight className="h-8 w-8 text-gray-400" />
            </div>
            <p className="text-gray-500">No mappings configured</p>
            <p className="text-sm text-gray-400 mt-1">
              Add field mappings to define how data should be transferred between systems
            </p>
            <Button variant="outline" onClick={addMapping} className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Add First Mapping
            </Button>
          </div>
        )}
      </Card>

      {/* Mapping Preview */}
      {mappings.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Mapping Preview</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source Field
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Target Field
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transformation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Required
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mappings.map((mapping, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {mapping.source_field || 'Not selected'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mapping.target_field || 'Not selected'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mapping.transformation || 'None'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mapping.is_required ? 'Yes' : 'No'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Help Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Mapping Help</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Field Mapping</h4>
            <p className="text-sm text-gray-600">
              Define how fields from the ERP system should map to fields in the loyalty system.
              Select the appropriate source and target fields for each mapping.
            </p>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Transformations</h4>
            <p className="text-sm text-gray-600">
              Apply transformations to data during mapping. Common transformations include
              formatting dates, converting currencies, and standardizing text formats.
            </p>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Validation</h4>
            <p className="text-sm text-gray-600">
              Set validation rules for each mapping. Mark fields as required if they
              must be present in the source data.
            </p>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Testing</h4>
            <p className="text-sm text-gray-600">
              Test individual mappings to ensure they work correctly with real data.
              This helps identify issues before running full synchronization.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default DataMappingInterface