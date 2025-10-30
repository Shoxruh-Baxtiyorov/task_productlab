import React, {useEffect} from 'react';
import shave from 'shave';
import {useNavigate, useSearchParams} from "react-router-dom";

import '../styles/ConversationListItem.css';

export default function ConversationListItem({ dialog, chosen }) {
    const nav = useNavigate();
    const [sP, setSP] = useSearchParams();

    useEffect(() => {
        shave('.conversation-snippet', 20);
    })

    const switchChatToCurrent = () => {
        nav(`/messenger/${dialog.interlocutor_id}?token=${sP.get('token')}`)
    }

    return (
      <div className={`conversation-list-item${chosen ? ' chosen' : ''}`} onClick={switchChatToCurrent}>
        <img className="conversation-photo" src={'https://upload.wikimedia.org/wikipedia/commons/a/ac/Default_pfp.jpg'} alt="conversation" />
        <div className="conversation-info">
          <h1 className="conversation-title">{ dialog.interlocutor.full_name }</h1>
          <p className="conversation-snippet">{ dialog.text }</p>
        </div>
      </div>
    );
}