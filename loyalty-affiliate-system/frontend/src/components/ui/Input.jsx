import { forwardRef } from 'react'
import clsx from 'clsx'

const Input = forwardRef(({
  label,
  error,
  helperText,
  className,
  ...props
}, ref) => {
  const inputClasses = clsx(
    'block w-full px-3 py-2 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
    error
      ? 'border-danger-300 text-danger-900 focus:ring-danger-500 focus:border-danger-500'
      : 'border-gray-300 text-gray-900',
    props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
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
        ref={ref}
        className={inputClasses}
        {...props}
      />
      {error && (
        <p className="text-sm text-danger-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  )
})

Input.displayName = 'Input'

export default Input