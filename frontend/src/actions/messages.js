import {
    FETCH_CHAT_MESSAGES_FAIL,
    FETCH_CHAT_MESSAGES_SUCCESS,
    FETCH_DIALOGS_FAIL,
    FETCH_DIALOGS_SUCCESS, SEND_MESSAGE_FAIL, SEND_MESSAGE_SUCCESS
} from "./types";
import axios from "axios";

export const sendMessage = (token, text, lastMessage) => async dispatch => {
    const config = {
        params: {
            token: token
        }
    }
    const data = {
        receiver_id: lastMessage.interlocutor_id,
        context: lastMessage.context,
        source: 'WEB',
        type: 'MESSAGE',
        text: text,
        offer_id: lastMessage.offer_id,
        task_id: lastMessage.task_id
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/messages`, data, config)

        if (res.status === 201) {
            dispatch({
                type: SEND_MESSAGE_SUCCESS,
                payload: res.data.message
            })
        }
    } catch (err) {
        console.log(`ERROR WHILE SENDING MESSAGE ${err}`)
        dispatch({
            type: SEND_MESSAGE_FAIL
        })
    }

}

export const getChatMessages = (token, lastMessage) => async dispatch => {
    let config = {
        params: {
            token: token,
            context: lastMessage.context,
            interlocutor_id: lastMessage.interlocutor_id,
            offer_id: lastMessage.offer_id,
            task_id: lastMessage.task_id
        }
    }

    try {
        const res = await axios.get(`${process.env.REACT_APP_DTASKBOT_API_URL}/messages`, config)

        if (res.status === 200) {
            dispatch({
                type: FETCH_CHAT_MESSAGES_SUCCESS,
                payload: res.data
            })
        }
    } catch (err) {
        console.log(`ERROR WHILE GETTING CHAT MESSAGES ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: FETCH_CHAT_MESSAGES_FAIL
        });
    }
}

export const getDialogs = (token, taskId) => async dispatch => {
    const config = {
        params: {
            token: token,
            task_id: taskId
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: FETCH_DIALOGS_FAIL
        });
    }

    try {
        const res = await axios.get(`${process.env.REACT_APP_DTASKBOT_API_URL}/messages/dialogs`, config)

        if (res.status === 200) {
            dispatch({
                type: FETCH_DIALOGS_SUCCESS,
                payload: res.data
            })
        }
    } catch (err) {
        console.log(`ERROR WHILE GETTING DIALOGS ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: FETCH_DIALOGS_FAIL
        });
    }
}