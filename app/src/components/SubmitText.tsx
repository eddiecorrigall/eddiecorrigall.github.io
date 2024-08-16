import React, { FormEventHandler } from 'react'
import * as css from './SubmitText.module.css'

function SubmitText(props: {
  onSubmit: FormEventHandler<HTMLFormElement>,
  onTextChange: React.ChangeEventHandler<HTMLInputElement>,
  text?: string,
  placeholder?: string,
  buttonLabel?: string,
}) {
  const classNames = css as any
  return <div className={classNames.container}>
    <div className={classNames.search}>
      <form onSubmit={props.onSubmit}>
        <input
          type='text'
          autoComplete='off'
          placeholder={props.placeholder || ''}
          value={props.text || ''}
          onChange={props.onTextChange}
        />
        <button type="submit">
          { props.buttonLabel || 'Search' }
        </button>
      </form>
    </div>
  </div>
}

export default SubmitText
