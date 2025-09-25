import clsx from 'clsx'

const Input = ({
  label,
  error,
  helperText,
  className,
  ...props
}) => {
  const inputClasses = clsx(
    'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400',
    'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
    error && 'border-red-300 focus:ring-red-500 focus:border-red-500',
    className
  )

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        className={inputClasses}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  )
}

export default Input