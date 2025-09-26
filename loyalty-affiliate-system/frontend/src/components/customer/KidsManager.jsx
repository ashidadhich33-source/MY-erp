import { useState, useEffect } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { Plus, Trash2, Users, Calendar, Edit } from 'lucide-react'
import { customersAPI } from '../../services/api'
import Card from '../ui/Card'
import Button from '../ui/Input'

const KidsManager = ({ customerId, customerName }) => {
  const [kids, setKids] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({
    defaultValues: {
      kids_data: []
    }
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: "kids_data"
  })

  useEffect(() => {
    fetchKids()
  }, [customerId])

  const fetchKids = async () => {
    try {
      setLoading(true)
      const response = await customersAPI.getKids(customerId)
      setKids(response.kids)

      // Reset form with existing kids data
      reset({
        kids_data: response.kids.map(kid => ({
          id: kid.id,
          name: kid.name,
          date_of_birth: kid.date_of_birth.split('T')[0], // Convert to date format
          gender: kid.gender || '',
          notes: kid.notes || ''
        }))
      })
    } catch (err) {
      setError('Failed to fetch kids information')
      console.error('Error fetching kids:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (data) => {
    try {
      setSaving(true)

      // Prepare kids data for API
      const kidsData = data.kids_data.map(kid => ({
        id: kid.id,
        name: kid.name,
        date_of_birth: kid.date_of_birth,
        gender: kid.gender || null,
        notes: kid.notes || null,
        is_active: true
      }))

      await customersAPI.manageKids(customerId, { kids_data: kidsData })
      await fetchKids() // Refresh the data
      alert('Kids information updated successfully!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save kids information')
      console.error('Error saving kids:', err)
    } finally {
      setSaving(false)
    }
  }

  const addKid = () => {
    append({
      name: '',
      date_of_birth: '',
      gender: '',
      notes: ''
    })
  }

  const removeKid = (index) => {
    remove(index)
  }

  const calculateAge = (dateOfBirth) => {
    if (!dateOfBirth) return ''
    const today = new Date()
    const birth = new Date(dateOfBirth)
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }

    return age >= 0 ? `${age} years old` : ''
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
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
            onClick={fetchKids}
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
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Kids Information - {customerName}
            </h3>
            <p className="text-gray-600">
              Manage children's information for birthday promotions and age-based offers.
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={addKid}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Kid
          </Button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(handleSave)}>
          <div className="space-y-6">
            {fields.map((field, index) => (
              <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-medium text-gray-900">
                    Kid {index + 1}
                  </h4>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeKid(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name *
                    </label>
                    <input
                      {...register(`kids_data.${index}.name`, {
                        required: 'Name is required'
                      })}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Enter child's full name"
                    />
                    {errors.kids_data?.[index]?.name && (
                      <p className="text-sm text-danger-600 mt-1">
                        {errors.kids_data[index].name.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date of Birth *
                    </label>
                    <input
                      {...register(`kids_data.${index}.date_of_birth`, {
                        required: 'Date of birth is required'
                      })}
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    {errors.kids_data?.[index]?.date_of_birth && (
                      <p className="text-sm text-danger-600 mt-1">
                        {errors.kids_data[index].date_of_birth.message}
                      </p>
                    )}
                    {/* Show calculated age */}
                    {field.date_of_birth && (
                      <p className="text-sm text-gray-500 mt-1">
                        {calculateAge(field.date_of_birth)}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gender
                    </label>
                    <select
                      {...register(`kids_data.${index}.gender`)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">Select gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Relationship / Notes
                    </label>
                    <input
                      {...register(`kids_data.${index}.notes`)}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g., Son, Daughter, Niece"
                    />
                  </div>
                </div>
              </div>
            ))}

            {fields.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No kids information added yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Add kids information to enable birthday promotions and age-based offers
                </p>
                <Button
                  type="button"
                  variant="outline"
                  onClick={addKid}
                  className="mt-4"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add First Kid
                </Button>
              </div>
            )}

            {fields.length > 0 && (
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <Button
                  type="button"
                  variant="outline"
                  onClick={fetchKids}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  loading={saving}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            )}
          </div>
        </form>
      </Card>

      {/* Kids Benefits Info */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Why Add Kids Information?</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-blue-600 text-sm">🎂</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Birthday Promotions</h4>
              <p className="text-sm text-gray-600">
                Automatic birthday messages and special offers for kids' birthdays
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-green-600 text-sm">🎁</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Age-Based Offers</h4>
              <p className="text-sm text-gray-600">
                Personalized promotions and rewards based on children's ages
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-purple-600 text-sm">📱</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">WhatsApp Notifications</h4>
              <p className="text-sm text-gray-600">
                Automated WhatsApp messages for birthdays and special occasions
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-yellow-600 text-sm">🏆</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">Family Rewards</h4>
              <p className="text-sm text-gray-600">
                Additional loyalty points and benefits for family activities
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default KidsManager