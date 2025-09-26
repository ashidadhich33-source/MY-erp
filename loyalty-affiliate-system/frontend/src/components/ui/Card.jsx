import clsx from 'clsx'

const Card = ({
  children,
  className,
  padding = 'default',
  shadow = 'sm',
  ...props
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    default: 'p-6',
    lg: 'p-8',
  }

  const shadowClasses = {
    none: '',
    xs: 'shadow-xs',
    sm: 'shadow-sm',
    default: 'shadow',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  }

  const classes = clsx(
    'bg-white border border-gray-200 rounded-lg',
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

export default Card