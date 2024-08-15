import React, { FormEventHandler } from 'react'
import * as styles from './SubmitText.module.css'

function SubmitText(props: {
  onSubmit: FormEventHandler<HTMLFormElement>,
  onChange: React.ChangeEventHandler<HTMLInputElement>,
  value?: string,
  placeholder?: string,
  buttonLabel?: string,
}) {
  const { container, search } = (styles as any);
  return <div className={container}>
    <div className={search}>
      <form onSubmit={props.onSubmit}>
        <input
          type='text'
          autoComplete='off'
          placeholder={props.placeholder || ''}
          value={props.value || ''}
          onChange={props.onChange}
        />
        <button type="submit">
          { props.buttonLabel || 'Search' }
        </button>
      </form>
    </div>
  </div>
}

export default SubmitText
