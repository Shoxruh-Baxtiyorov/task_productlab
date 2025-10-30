import React, {useEffect} from 'react';
import ConversationList from "./ConversationList";
import MessageList from "./MessageList";
import '../styles/Messenger.css';
import '../styles/index.css';
import {connect} from "react-redux";
import {getDialogs} from "../actions/messages";
import {useParams, useSearchParams} from "react-router-dom";
import {Skeleton} from "antd";

const checkDialogsSync = (dialog, taskId) => {
    if (taskId) {
        if (dialog.task_id) {
            return dialog.task_id === taskId;
        } else if (dialog.offer_id) {
            return dialog.offer.task.id === taskId;
        }
        return false;
    }
    return true;
}

function Messenger ({ getDialogs, dialogs }) {
    const [sP, setSP] = useSearchParams();
    const params = useParams();
    const chatId = parseInt(params.id);
    const taskId = parseInt(sP.get('task_id'));
    let chat = null;

    useEffect(() => {
        const fetchDialogs = async () => {
            await getDialogs(sP.get('token'), taskId);
        }
        if (!dialogs || !checkDialogsSync(dialogs[0], taskId)) {
            fetchDialogs();
        }
    })

    if (!dialogs || !checkDialogsSync(dialogs[0], taskId)) {
        return <Skeleton active/>
    }
    console.log('dialogs', dialogs);

    if (chatId) {
        chat = dialogs.find((d) => d.interlocutor_id === chatId);
    }

    let rightPage = (
        <div className={'scrollable content'}>
            <h1>Choose one of chats to start conversation.</h1>
        </div>
    )
    if (chat) {
        rightPage = (
            <div className="scrollable content">
              <MessageList chat={chat}/>
            </div>
        )
    }

    return (
      <div className="messenger">

        <div className="scrollable sidebar">
          <ConversationList dialogs={dialogs} chatId={chatId}/>
        </div>

          {rightPage}
      </div>
    );
}

const mapStateToProps = state => ({
    dialogs: state.messages.dialogs
});

export default connect(mapStateToProps, { getDialogs })(Messenger);
