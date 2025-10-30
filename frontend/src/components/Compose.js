import React from 'react';
import '../styles/Compose.css';
import {connect} from "react-redux";
import {sendMessage} from "../actions/messages";
import {useSearchParams} from "react-router-dom";

function Compose(props) {
    const [sP, setSP] = useSearchParams();
    const onSubmit = (e) => {
        if (e.code === 'Enter') {
            props.sendMessage(sP.get('token'), e.target.value, props.lastMessage)
            e.target.value = '';
            console.log('sent message!')
        }
    }

    return (
      <div className="compose">
        <input
          type="text"
          className="compose-input"
          placeholder={`Type a message for ${props.chat.interlocutor.full_name}`}
          onKeyDown={onSubmit}
        />

        {
          props.rightItems
        }
      </div>
    );
}

const mapStateToProps = (state) => ({
    chats: state.messages.chats
})

export default connect(mapStateToProps, { sendMessage })(Compose);
