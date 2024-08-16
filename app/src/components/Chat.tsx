import React, { FormEventHandler, ChangeEventHandler } from 'react'
import SubmitText from './SubmitText'
import * as css from './Chat.module.css'
import { MessageDTO } from '../dto/MessageDTO';

const Chat = (props: {
  onSubmit: FormEventHandler<HTMLFormElement>,
  userMessageText: string,
  onUserMessageTextChange: ChangeEventHandler<HTMLInputElement>,
  messages: MessageDTO[],
  messagePlaceholder: string,
  submitLabel: string,
}) => {
  const classNames = css as any;
  const getRoleClassName = (message: MessageDTO) => {
    return message.role === 'user'
      ? classNames.user
      : classNames.assistant
  }
  const messageDataContext = (message: MessageDTO) => {
    const messenger = message.role === 'user'
      ? 'You'
      : 'Assistant'
    const timeString = message.created_at.toLocaleTimeString()
    return `${messenger} ${timeString}`
  }
  return <div className={classNames.container}>
    <SubmitText
      onSubmit={props.onSubmit}
      onTextChange={props.onUserMessageTextChange}
      text={props.userMessageText}
      placeholder={props.messagePlaceholder}
      buttonLabel={props.submitLabel}
    />
    <div className={classNames.messages}>
      {props.messages.map((message, index) => (
        <p
          key={index}
          data-context={messageDataContext(message)}
          className={`${classNames.message} ${getRoleClassName(message)}`}>
          {message.text}
        </p>
      ))}
    </div>
  </div>
};

export default Chat
