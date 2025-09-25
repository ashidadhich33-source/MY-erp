import clsx from 'clsx'

const Card = ({
  children,
  className,
  padding = 'md',
  shadow = 'sm',
  ...props
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  }

  const classes = clsx(
    'bg-white rounded-lg border border-gray-200',
    paddingClasses[padding],
    shadowClasses[shadow],
    className
  )

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

const CardHeader = ({ children, className, ...props }) => {
  const classes = clsx('mb-4', className)
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

const CardTitle = ({ children, className, ...props }) => {
  const classes = clsx('text-lg font-semibold text-gray-900', className)
  return (
    <h3 className={classes} {...props}>
      {children}
    </h3>
  )
}

const CardContent = ({ children, className, ...props }) => {
  const classes = clsx('', className)
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

const CardFooter = ({ children, className, ...props }) => {
  const classes = clsx('mt-6 pt-4 border-t border-gray-200', className)
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

export { Card, CardHeader, CardTitle, CardContent, CardFooter }