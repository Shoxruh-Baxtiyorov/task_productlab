import {
    FETCH_CHAT_MESSAGES_SUCCESS,
    FETCH_DIALOGS_FAIL,
    FETCH_DIALOGS_SUCCESS, SEND_MESSAGE_FAIL,
    SEND_MESSAGE_SUCCESS
} from "../actions/types";

const initialState = {
    dialogs: null,
    chats: []
}

export default function (state=initialState, action) {
    switch (action.type) {
        case SEND_MESSAGE_SUCCESS:
            return {
                ...state,
                chats: state.chats.map(c => c.interlocutor_id === action.payload.interlocutor_id ? {...c, messages: [...c.messages, action.payload]} : c)
            }
        case FETCH_CHAT_MESSAGES_SUCCESS:
            return {
                ...state,
                chats: [...state.chats, {interlocutor_id: action.payload[0].interlocutor_id, messages: action.payload}]
            }
        case FETCH_DIALOGS_SUCCESS:
            return {
                ...state,
                dialogs: action.payload
            }
        case FETCH_DIALOGS_FAIL:
        case SEND_MESSAGE_FAIL:
        default:
            return state
    }
}