import React, {useEffect, useState} from 'react';
import Compose from './Compose';
import Toolbar from './Toolbar';
import ToolbarButton from './ToolbarButton';
import Message from './Message';
import moment from 'moment';
import {getChatMessages} from "../actions/messages";
import {connect} from "react-redux";
import '../styles/MessageList.css';
import {useSearchParams} from "react-router-dom";
import {Skeleton} from "antd";

function MessageList({ getChatMessages, chats, chat }) {
    const [sP, setSP] = useSearchParams();
    const chatData = chats.find(c => c.interlocutor_id === chat.interlocutor_id)

    useEffect(() => {
        const fetchChatMessages = async () => {
            await getChatMessages(sP.get('token'), chat)
        }
        if (chatData === undefined) {
            fetchChatMessages()
        }
    })

    if (chatData === undefined) {
        return <Skeleton active/>
    }
    console.log(chatData)
    const messages = chatData.messages
    console.log(Date.parse(messages[0].created_at))
    console.log(new Date().getTime())

  const renderMessages = () => {
    let i = 0;
    let messageCount = messages.length;
    let tempMessages = [];

    while (i < messageCount) {
      let previous = messages[i - 1];
      let current = messages[i];
      let next = messages[i + 1];
      let isMine = current.interlocutor_id !== current.author_id;
      let currentMoment = moment(Date.parse(current.created_at));
      let prevBySameAuthor = false;
      let nextBySameAuthor = false;
      let startsSequence = true;
      let endsSequence = true;
      let showTimestamp = true;

      if (previous) {
        let previousMoment = moment(Date.parse(previous.created_at));
        let previousDuration = moment.duration(currentMoment.diff(previousMoment));
        prevBySameAuthor = previous.author_id === current.author_id;
        
        if (prevBySameAuthor && previousDuration.as('hours') < 1) {
          startsSequence = false;
        }

        if (previousDuration.as('hours') < 1) {
          showTimestamp = false;
        }
      }

      if (next) {
        let nextMoment = moment(Date.parse(next.created_at));
        let nextDuration = moment.duration(nextMoment.diff(currentMoment));
        nextBySameAuthor = next.author_id === current.author_id;

        if (nextBySameAuthor && nextDuration.as('hours') < 1) {
          endsSequence = false;
        }
      }

      tempMessages.push(
        <Message
          key={i}
          isMine={isMine}
          startsSequence={startsSequence}
          endsSequence={endsSequence}
          showTimestamp={showTimestamp}
          data={current}
        />
      );

      // Proceed to the next message.
      i += 1;
    }

    return tempMessages;
  }
    const renderedMessages = renderMessages();

    return(
      <div className="message-list">
        <Toolbar
          title={chat.interlocutor.full_name}
          rightItems={[
            <ToolbarButton key="info" icon="ion-ios-information-circle-outline" />
          ]}
        />

        <div className="message-list-container">{renderedMessages}</div>

        <Compose
            rightItems={[
                <ToolbarButton key='send' icon='ion-ios-send'/>
            ]}
            lastMessage={messages.slice(-1)[0]}
            chat={chat}
        />
      </div>
    );
}

const mapStateToProps = state => ({
    chats: state.messages.chats
});

export default connect(mapStateToProps, {getChatMessages})(MessageList);