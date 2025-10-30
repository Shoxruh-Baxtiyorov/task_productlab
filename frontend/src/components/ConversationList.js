import React, {useState, useEffect} from 'react';
import ConversationSearch from './ConversationSearch';
import ConversationListItem from './ConversationListItem';
import Toolbar from './Toolbar';
import ToolbarButton from './ToolbarButton';
import axios from 'axios';

import '../styles/ConversationList.css';

export default function ConversationList({ dialogs, chatId }) {
    return (
      <div className="conversation-list">
        <Toolbar
          title="Messenger"
          leftItems={[
            // <ToolbarButton key="cog" icon="ion-ios-cog" />
          ]}
          rightItems={[
            // <ToolbarButton key="add" icon="ion-ios-add-circle-outline" />
          ]}
        />
        <ConversationSearch />
        {
          dialogs.map(c =>
            <ConversationListItem
                dialog={c}
              key={c.interlocutor_id}
              data={c}
                chosen={chatId === c.interlocutor_id}
            />
          )
        }
      </div>
    );
}